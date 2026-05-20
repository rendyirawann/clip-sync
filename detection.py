"""
detection.py — Face detection, speaker tracking, and analysis module.
Separated from processor.py for the 2-pass pipeline architecture.
"""
import cv2
import numpy as np
import os
import json
import math

# Safe print
_builtin_print = __builtins__.print if hasattr(__builtins__, 'print') else print
def print(*args, **kwargs):
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            new_args.append(arg.encode('ascii', errors='ignore').decode('ascii'))
        else:
            new_args.append(arg)
    _builtin_print(*new_args, **kwargs)

try:
    import mediapipe as mp
    from mediapipe.solutions import face_detection as mp_face
    from mediapipe.solutions import face_mesh as mp_mesh
    face_detector = mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.3)
    face_mesher = mp_mesh.FaceMesh(static_image_mode=False, max_num_faces=5, min_detection_confidence=0.4)
    HAS_MEDIAPIPE = True
except Exception:
    HAS_MEDIAPIPE = False

try:
    from ultralytics import YOLO
    import logging
    logging.getLogger("ultralytics").setLevel(logging.ERROR)
    model_path = os.path.join(os.path.dirname(__file__), 'yolov8n-pose.pt')
    yolo_model = YOLO(model_path)
    HAS_YOLO = True
except Exception as e:
    import traceback
    print("ERROR LOADING YOLO-POSE:")
    traceback.print_exc()
    HAS_YOLO = False

def calculate_mar(face_lms):
    """Mouth Aspect Ratio — more accurate than simple lip distance.
    Uses 6 landmark points around the mouth for robust speech detection."""
    try:
        # Upper lip inner: 13, 312
        # Lower lip inner: 14, 317
        # Corners: 61 (left), 291 (right)
        top1 = face_lms.landmark[13]
        top2 = face_lms.landmark[312]
        bot1 = face_lms.landmark[14]
        bot2 = face_lms.landmark[317]
        left = face_lms.landmark[61]
        right = face_lms.landmark[291]

        v1 = math.sqrt((top1.x - bot1.x)**2 + (top1.y - bot1.y)**2)
        v2 = math.sqrt((top2.x - bot2.x)**2 + (top2.y - bot2.y)**2)
        h = math.sqrt((left.x - right.x)**2 + (left.y - right.y)**2)
        return (v1 + v2) / (2.0 * h + 1e-6)
    except Exception:
        return 0.0


def detect_faces(frame_bgr):
    """Hybrid Tracker: Detect people with YOLO-Pose and faces with MediaPipe.
    Merges them so we never lose a speaker even if they face sideways."""
    entities = []
    
    # 1. Detect People with YOLO-Pose
    if HAS_YOLO:
        # conf=0.45 ensures we only get high-confidence human detections (no mics/radios)
        y_results = yolo_model(frame_bgr, conf=0.45, verbose=False)
        if y_results and len(y_results[0].boxes) > 0:
            boxes = y_results[0].boxes.xyxyn.cpu().numpy()
            keypoints = y_results[0].keypoints.xyn.cpu().numpy() if y_results[0].keypoints is not None else []
            
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box
                # Filter out objects that are wider than they are tall (mics, tables)
                if (x2 - x1) > (y2 - y1) * 1.5:
                    continue
                    
                # Filter if heavily overlapping with an existing entity
                is_overlap = False
                for e in entities:
                    ex1, ey1, ex2, ey2 = e['bbox']
                    # Calculate Intersection over Union (IoU) or simple containment
                    if x1 >= ex1 and y1 >= ey1 and x2 <= ex2 and y2 <= ey2:
                        is_overlap = True
                        break
                    elif ex1 >= x1 and ey1 >= y1 and ex2 <= x2 and ey2 <= y2:
                        # Existing is inside this new one, we will just ignore the new one for simplicity
                        is_overlap = True
                        break
                
                if is_overlap:
                    continue
                    
                cx = (x1 + x2) / 2
                cy = y1 + (y2 - y1) * 0.2
                fh = (y2 - y1) * 0.3
                
                # Get eye level from pose keypoints if available
                eye_y = y1 + (y2 - y1) * 0.15 
                if len(keypoints) > i:
                    kpts = keypoints[i]
                    # Nose=0, LEye=1, REye=2, LEar=3, REar=4, LShoulder=5, RShoulder=6
                    eyes = [k[1] for k in kpts[1:3] if k[0] > 0 and k[1] > 0]
                    if eyes:
                        eye_y = sum(eyes) / len(eyes)
                    elif kpts[0][1] > 0: # Nose fallback
                        eye_y = kpts[0][1]
                    elif kpts[3][1] > 0 or kpts[4][1] > 0: # Ears fallback
                        ears = [k[1] for k in kpts[3:5] if k[0] > 0 and k[1] > 0]
                        eye_y = sum(ears) / len(ears)
                        
                entities.append({
                    'face_cx': cx, 'face_cy': cy, 'face_h': fh, 
                    'eye_y': float(eye_y), 'mar': 0.0, 'bbox': box, 'is_yolo': True
                })
    
    # 2. Detect Faces with MediaPipe
    mp_faces = []
    if HAS_MEDIAPIPE:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mesh_results = face_mesher.process(rgb)
        if mesh_results.multi_face_landmarks:
            for lms in mesh_results.multi_face_landmarks:
                xs = [l.x for l in lms.landmark]
                ys = [l.y for l in lms.landmark]
                cx = (min(xs) + max(xs)) / 2
                cy = (min(ys) + max(ys)) / 2
                
                # Get exact eye coordinates (Left eye: 33, Right eye: 263)
                leye_y = lms.landmark[33].y
                reye_y = lms.landmark[263].y
                eye_y = (leye_y + reye_y) / 2
                
                fh = max(ys) - min(ys)
                mar = calculate_mar(lms)
                mp_faces.append({
                    'face_cx': cx, 'face_cy': cy, 'face_h': fh, 
                    'eye_y': eye_y, 'mar': mar, 'is_yolo': False
                })
        else:
            det_results = face_detector.process(rgb)
            if det_results.detections:
                for det in det_results.detections:
                    bb = det.location_data.relative_bounding_box
                    cx = bb.xmin + bb.width / 2
                    cy = bb.ymin + bb.height / 2
                    # Approximate eye level for blaze face
                    eye_y = bb.ymin + bb.height * 0.3
                    mp_faces.append({
                        'face_cx': cx, 'face_cy': cy, 'face_h': bb.height,
                        'eye_y': eye_y, 'mar': 0.0, 'is_yolo': False
                    })
                    
    # 3. Merge YOLO-Pose and MediaPipe
    if not HAS_YOLO:
        return mp_faces

    merged = []
    for e in entities:
        bx1, by1, bx2, by2 = e['bbox']
        matched_mp = None
        for i, f in enumerate(mp_faces):
            if f is None: continue
            # Check overlap
            if bx1 <= f['face_cx'] <= bx2 and by1 <= f['face_cy'] <= by2:
                matched_mp = f
                mp_faces[i] = None # Consume it
                break
        
        if matched_mp:
            # Update MAR but keep YOLO's stable coordinates if we want
            # Actually, MediaPipe coords are usually more exact for the face center
            e['face_cx'] = matched_mp['face_cx']
            e['face_cy'] = matched_mp['face_cy']
            e['eye_y'] = matched_mp['eye_y']
            e['face_h'] = matched_mp['face_h']
            e['mar'] = matched_mp['mar']
        
        merged.append(e)
        
    # Do not add unmatched MediaPipe faces because YOLO-Pose is the strict source of truth.
    # If MediaPipe finds a face but YOLO-Pose finds no body, it is a false positive (radio/poster).
            
    return merged


class FaceTracker:
    """Robust Spatial Face Tracker for stable IDs without relying on YOLO.
    Since podcast speakers sit in relatively fixed positions, we track them 
    by their normalized spatial coordinates (cx, cy)."""
    def __init__(self):
        self.tracks = {}  # track_id -> (cx, cy, eye_y)
        self.next_id = 0
        self.dist_threshold = 0.20  # Increased for camera cuts
        
    def update(self, faces):
        for f in faces:
            best_id = None
            best_dist = self.dist_threshold
            
            for tid, (tcx, tcy, teye) in self.tracks.items():
                dist = math.sqrt((f['face_cx'] - tcx)**2 + (f['face_cy'] - tcy)**2)
                if dist < best_dist:
                    best_dist = dist
                    best_id = tid
            
            if best_id is not None:
                f['track_id'] = best_id
                # ULTRA-SMOOTH EMA: 0.9 old + 0.1 new for cinematic stability
                old_cx, old_cy, old_eye = self.tracks[best_id]
                new_cx = old_cx * 0.90 + f['face_cx'] * 0.10
                new_cy = old_cy * 0.90 + f['face_cy'] * 0.10
                new_eye = old_eye * 0.90 + f['eye_y'] * 0.10
                
                self.tracks[best_id] = (new_cx, new_cy, new_eye)
                # Overwrite raw coordinates with smoothed ones for downstream processing
                f['face_cx'], f['face_cy'], f['eye_y'] = new_cx, new_cy, new_eye
            else:
                f['track_id'] = self.next_id
                self.tracks[self.next_id] = (f['face_cx'], f['face_cy'], f['eye_y'])
                self.next_id += 1
                
        return faces


def analyze_clip(video_path, start_time, end_time, sample_fps=8, engine_mode="opsi_a"):
    """PASS 1: Analyze entire clip and produce a crop plan.
    
    Samples at `sample_fps` (default 8) and collects:
    - Face positions per frame
    - MAR (speech activity) per face
    - Audio RMS per frame
    
    Returns: {
        'speakers': {track_id: {'positions': [...], 'mar_scores': [...]}},
        'frames': [{'time': t, 'faces': [...], 'audio_rms': float}],
        'num_speakers': int
    }
    """
    print(f"[PASS 1] Analyzing clip {start_time:.1f}s - {end_time:.1f}s at {sample_fps} fps (Engine Mode: {engine_mode})...")
    
    try:
        from moviepy import VideoFileClip
    except ImportError:
        from moviepy.editor import VideoFileClip

    # Use MoviePy for 100% frame synchronization with PASS 2
    clip = VideoFileClip(video_path).subclipped(start_time, end_time)
    src_fps = clip.fps or 30
    
    # Also open audio via moviepy for RMS
    audio_rms_map = _extract_audio_rms(video_path, start_time, end_time, sample_fps)
    
    all_frames = []
    speaker_data = {}  # track_id -> {xs: [], ys: [], mars: [], times: []}
    tracker = FaceTracker()
    
    frame_idx = 0
    last_faces = []
    
    for t, frame_rgb in clip.iter_frames(fps=sample_fps, with_times=True):
        abs_t = start_time + t
        
        # Opsi B (Smart Hybrid): Run heavy YOLO/Mediapipe every 12 frames (approx every 1.5s) to save CPU/RAM.
        # Otherwise, instantly reuse the last tracked face positions!
        if engine_mode == "opsi_b" and last_faces and (frame_idx % 12 != 0):
            faces = [dict(f) for f in last_faces]
        else:
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            faces = detect_faces(frame_bgr)
            faces = tracker.update(faces)
            last_faces = [dict(f) for f in faces]
            
        frame_idx += 1
        
        # Get audio RMS for this timestamp
        rms_idx = int(t * sample_fps)
        rms = audio_rms_map[rms_idx] if rms_idx < len(audio_rms_map) else 0.0
        
        # Store frame data
        frame_data = {
            'time': t,
            'abs_time': abs_t,
            'faces': [{
                'track_id': f['track_id'],
                'cx': f['face_cx'], 'cy': f['face_cy'],
                'face_h': f['face_h'], 'mar': f['mar'],
                'eye_y': f.get('eye_y', f['face_cy'] - f['face_h']*0.15),
                'is_yolo': f.get('is_yolo', False)
            } for f in faces],
            'audio_rms': rms
        }
        all_frames.append(frame_data)
        
        for f in faces:
            tid = f['track_id']
            if tid not in speaker_data:
                speaker_data[tid] = {'xs': [], 'ys': [], 'eye_ys': [], 'mars': [], 'times': []}
            speaker_data[tid]['xs'].append(f['face_cx'])
            speaker_data[tid]['ys'].append(f['face_cy'])
            speaker_data[tid]['eye_ys'].append(f.get('eye_y', f['face_cy'] - f['face_h']*0.15))
            speaker_data[tid]['mars'].append(f['mar'])
            speaker_data[tid]['times'].append(t)
            
    clip.close()
    del clip
    
    # Identify primary speakers (most frequently detected with lip activity)
    # Require at least 5% of frames
    min_detections = max(3, int(len(all_frames) * 0.05))
    primary_speakers = _identify_primary_speakers(speaker_data, max_speakers=6, min_detections=min_detections)
    
    print(f"[PASS 1] Found {len(primary_speakers)} primary speaker(s): {list(primary_speakers.keys())}")
    print(f"[PASS 1] Analyzed {len(all_frames)} sample frames")
    
    return {
        'speakers': primary_speakers,
        'frames': all_frames,
        'all_speaker_data': speaker_data,
        'num_speakers': len(primary_speakers),
        'src_fps': src_fps,
        'duration': end_time - start_time
    }


def _extract_audio_rms(video_path, start_time, end_time, sample_fps):
    """Extract audio RMS values at sample_fps rate."""
    rms_values = []
    try:
        from moviepy import VideoFileClip
    except ImportError:
        from moviepy.editor import VideoFileClip
    
    try:
        clip = VideoFileClip(video_path).subclipped(start_time, end_time)
        if clip.audio:
            duration = end_time - start_time
            num_samples = int(duration * sample_fps)
            for i in range(num_samples):
                t = i / sample_fps
                try:
                    af = clip.audio.get_frame(t)
                    rms = float(np.sqrt(np.mean(af**2)))
                except:
                    rms = 0.0
                rms_values.append(rms)
        clip.close()
        del clip
    except Exception as e:
        print(f"[!] Audio RMS extraction error: {e}")
    
    if not rms_values:
        rms_values = [0.0]
    return rms_values


def _identify_primary_speakers(speaker_data, max_speakers=3, min_detections=3):
    """From all tracked faces, identify the top N primary speakers 
    based on frequency of detection and lip activity."""
    scored = []
    for tid, data in speaker_data.items():
        frequency = len(data['times'])
        avg_mar = np.mean(data['mars']) if data['mars'] else 0
        max_mar = max(data['mars']) if data['mars'] else 0
        # Score combines how often detected + how much talking
        score = frequency * (1 + avg_mar * 10 + max_mar * 5)
        scored.append((tid, score, data))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    
    primary = {}
    for tid, score, data in scored[:max_speakers]:
        if len(data['times']) >= min_detections:  # At least min_detections
            primary[tid] = {
                'median_x': float(np.median(data['xs'])),
                'median_y': float(np.median(data['ys'])),
                'avg_mar': float(np.mean(data['mars'])),
                'detections': len(data['times']),
                'xs': data['xs'],
                'ys': data['ys'],
                'eye_ys': data['eye_ys'],
                'mars': data['mars'],
                'times': data['times']
            }
    
    if not primary and speaker_data:
        # Fallback: use the most detected face
        tid, score, data = scored[0]
        primary[tid] = {
            'median_x': float(np.median(data['xs'])),
            'median_y': float(np.median(data['ys'])),
            'avg_mar': 0.0,
            'detections': len(data['times']),
            'xs': data['xs'], 'ys': data['ys'], 'eye_ys': data['eye_ys'],
            'mars': data['mars'], 'times': data['times']
        }
    
    return primary

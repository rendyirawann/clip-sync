import cv2
import numpy as np
import subprocess
import math
import time
import sys
import os
import json
import re
from PIL import Image, ImageDraw, ImageFont
import textwrap
import gc
import codecs
from scipy.signal import savgol_filter

try:
    from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, VideoClip
except ImportError:
    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, VideoClip

_builtin_print = __builtins__.print if hasattr(__builtins__, 'print') else print
def print(*args, **kwargs):
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            new_args.append(arg.encode('ascii', errors='ignore').decode('ascii'))
        else:
            new_args.append(arg)
    _builtin_print(*new_args, **kwargs)

from detection import analyze_clip

# ── Smoothing ───────────────────────────────────────────────
def smooth_coordinates(values, window=51, poly=3):
    """Savitzky-Golay global smoothing for cinematic, fluid movement."""
    if len(values) < 5:
        return values
    w = min(window, len(values))
    if w % 2 == 0:
        w -= 1
    if w < 5:
        w = 5
    p = min(poly, w - 1)
    return savgol_filter(values, w, p).tolist()

# ── Crop Plan Builder ───────────────────────────────────────
def build_crop_plan(analysis, v_w, v_h, target_w, split_mode, engine_mode="opsi_a", speaker_timeline_data=None, content_type="gameplay"):
    """Convert raw analysis into a smoothed crop plan.
    
    Returns list of dicts: {time, mode, crops: [{x,y,w,h}, ...]}
    mode = 'single' | 'split2' | 'split3' | 'active_focus'
    """
    frames = analysis['frames']
    speakers = analysis['speakers']
    num_sp = analysis['num_speakers']
    speaker_ids = list(speakers.keys())
    duration = analysis['duration']

    if content_type == "gameplay":
        # Gameplay mode: absolute static center crop to preserve gaming interface and focus on central action!
        print("[PLAN] Gameplay mode active: Using 100% static action-centered crop.")
        plan = []
        for fr in frames:
            t = fr['time']
            crop = _calc_single_crop(0.5, 0.5, 0.4, v_w, v_h, target_w)
            plan.append({'time': t, 'mode': 'single', 'crops': [crop], 'active': None})
        return plan

    # Remove static mode decision, it will be dynamic
    print(f"[PLAN] Starting dynamic layout engine. Max requested split: {split_mode}")

    # Map Speaker 1, Speaker 2 from LLM dialogue to track IDs based on left-to-right positions
    speaker_id_mapping = {}
    if speaker_ids:
        sorted_speakers = sorted(speakers.items(), key=lambda x: x[1]['median_x'])
        for idx, (sid, sp_meta) in enumerate(sorted_speakers):
            speaker_id_mapping[f"Speaker {idx+1}"] = sid
            print(f"[PLAN] Mapped 'Speaker {idx+1}' to FaceTrack ID {sid} (median_x={sp_meta['median_x']:.2f})")

    # Build per-speaker smoothed position timelines
    sp_timelines = {}
    for sid in speaker_ids:
        sp = speakers[sid]
        xs_smooth = smooth_coordinates(sp['xs'], window=31)
        ys_smooth = smooth_coordinates(sp['ys'], window=31)
        # Eye_ys might not need smoothing if we just use bounding box, but let's smooth it too
        eye_ys_smooth = smooth_coordinates(sp.get('eye_ys', sp['ys']), window=31)
        sp_timelines[sid] = {
            'xs': xs_smooth, 'ys': ys_smooth, 'eye_ys': eye_ys_smooth,
            'times': sp['times']
        }

    # Build active speaker timeline (who is talking when)
    active_timeline = _build_active_speaker_timeline(frames, speaker_ids, speaker_timeline_data, speaker_id_mapping)

    # Generate crop plan per sample frame dynamically
    plan = []
    for i, fr in enumerate(frames):
        t = fr['time']
        
        # Get active speaker ID (if known) or fallback
        active_sid = None
        if active_timeline and i < len(active_timeline):
            active_sid = active_timeline[i]
        
        # Count visible speakers in this specific frame
        visible_faces = fr['faces']
        num_visible = len(visible_faces)
        
        # Sort faces from left to right
        visible_faces = sorted(visible_faces, key=lambda f: f['cx'])
        
        if split_mode and num_visible >= 3:
            crops = []
            for face in visible_faces[:3]:
                sx, sy, seye = face['cx'], face['cy'], face['eye_y']
                crops.append(_calc_split_crop(sx, sy, seye, v_w, v_h, target_w, v_h // 3))
            plan.append({'time': t, 'mode': 'split3', 'crops': crops, 'active': active_sid})
            
        elif split_mode and num_visible >= 2:
            crops = []
            for face in visible_faces[:2]:
                sx, sy, seye = face['cx'], face['cy'], face['eye_y']
                crops.append(_calc_split_crop(sx, sy, seye, v_w, v_h, target_w, v_h // 2))
            plan.append({'time': t, 'mode': 'split2', 'crops': crops, 'active': active_sid})
            
        else:
            # Single mode (fallback to active speaker if available, otherwise use visible face, otherwise center)
            if num_visible == 1:
                sx, sy, seye = visible_faces[0]['cx'], visible_faces[0]['cy'], visible_faces[0]['eye_y']
            else:
                sx, sy, seye = _get_speaker_pos(sp_timelines, active_sid, t, speakers) if active_sid else (0.5, 0.5, 0.4)
                
            crop = _calc_single_crop(sx, sy, seye, v_w, v_h, target_w)
            plan.append({'time': t, 'mode': 'single', 'crops': [crop], 'active': active_sid})

    # Smooth the crop coordinates globally
    plan = _smooth_plan(plan)
    return plan


def _build_active_speaker_timeline(frames, speaker_ids, speaker_timeline_data=None, speaker_id_mapping=None):
    """Determine who is actively speaking at each frame using audio, MAR, or LLM-timeline overrides."""
    timeline = []
    current_active = speaker_ids[0] if speaker_ids else None
    hysteresis = 0

    for fr in frames:
        rms = fr['audio_rms']
        best_sid = current_active
        best_score = 0
        abs_t = fr.get('abs_time', fr['time'])

        # Smart Hybrid Mode override: If LLM timeline segments are active, use them!
        found_active = False
        if speaker_timeline_data and speaker_id_mapping:
            for seg in speaker_timeline_data:
                if seg['start'] <= abs_t <= seg['end']:
                    sp_name = seg.get('speaker', 'Speaker 1')
                    mapped_sid = speaker_id_mapping.get(sp_name, None)
                    if mapped_sid is not None:
                        best_sid = mapped_sid
                        found_active = True
                        break

        if not found_active:
            if rms > 0.01:
                for face in fr['faces']:
                    tid = face['track_id']
                    if tid not in speaker_ids:
                        continue
                    
                    mar_score = face['mar']
                    score = mar_score * rms * 100
                    
                    if tid == current_active:
                        score *= 1.5  # Increased Hysteresis bonus
                        
                    if score > best_score:
                        best_score = score
                        best_sid = tid

            if best_sid != current_active and best_score > 0.05:
                hysteresis += 1
                # Require 12 consecutive frames (~1.5s at 8fps) to switch cameras
                if hysteresis >= 12:  
                    current_active = best_sid
                    hysteresis = 0
            else:
                # Decay hysteresis gradually rather than resetting instantly
                # This makes cuts feel more natural and intentional
                hysteresis = max(0, hysteresis - 1)

        timeline.append(best_sid)
    return timeline


def _get_speaker_pos(timelines, sid, t, speakers):
    """Get interpolated speaker position at time t."""
    if sid in timelines:
        tl = timelines[sid]
        times = tl['times']
        if not times:
            default_y = speakers[sid]['median_y']
            return speakers[sid]['median_x'], default_y, default_y - 0.05
        # Find nearest index
        idx = min(range(len(times)), key=lambda i: abs(times[i] - t))
        # eye_ys might not be present in old plans, fallback to ys
        eye_y = tl['eye_ys'][idx] if 'eye_ys' in tl else tl['ys'][idx] - 0.05
        return tl['xs'][idx], tl['ys'][idx], eye_y
    if sid in speakers:
        default_y = speakers[sid]['median_y']
        return speakers[sid]['median_x'], default_y, default_y - 0.05
    return 0.5, 0.5, 0.4


def _calc_single_crop(sx, sy, seye, v_w, v_h, target_w):
    """Calculate crop rect for single speaker mode with zoom using Rule of Thirds."""
    zoom = 1.15
    cw = target_w / zoom
    ch = v_h / zoom
    cx = sx * v_w
    
    # Cinematic Rule of Thirds: Place the eyes at exactly the upper 33% of the frame.
    eye_target = seye * v_h
    
    x1 = max(0, cx - cw / 2)
    if x1 + cw > v_w:
        x1 = max(0, v_w - cw)
        
    y1 = max(0, eye_target - ch * 0.33)
    if y1 + ch > v_h:
        y1 = max(0, v_h - ch)
    return {'x': x1, 'y': y1, 'w': cw, 'h': ch}


def _calc_split_crop(sx, sy, seye, v_w, v_h, target_w, panel_h):
    """Calculate crop rect for one panel of split screen using Rule of Thirds."""
    aspect = float(target_w) / panel_h
    crop_h = v_h * 0.65
    crop_w = crop_h * aspect
    if crop_w > v_w:
        crop_w = v_w
        crop_h = crop_w / aspect
    cx = sx * v_w
    eye_target = seye * v_h
    
    x1 = max(0, cx - crop_w / 2)
    if x1 + crop_w > v_w:
        x1 = max(0, v_w - crop_w)
        
    # Rule of Thirds for split screen panels
    y1 = max(0, eye_target - crop_h * 0.33)
    if y1 + crop_h > v_h:
        y1 = max(0, v_h - crop_h)
    return {'x': x1, 'y': y1, 'w': crop_w, 'h': crop_h}


def _smooth_plan(plan):
    """Apply Savitzky-Golay smoothing to contiguous segments of identical mode."""
    if not plan: return plan
    
    # Group plan into segments of the same mode
    segments = []
    current_segment = [plan[0]]
    for p in plan[1:]:
        if p['mode'] == current_segment[-1]['mode'] and len(p['crops']) == len(current_segment[-1]['crops']):
            current_segment.append(p)
        else:
            segments.append(current_segment)
            current_segment = [p]
    segments.append(current_segment)
    
    smoothed_plan = []
    for seg in segments:
        if len(seg) < 5:
            smoothed_plan.extend(seg)
            continue
            
        max_crops = len(seg[0]['crops'])
        for ci in range(max_crops):
            xs = [p['crops'][ci]['x'] for p in seg]
            ys = [p['crops'][ci]['y'] for p in seg]
            ws = [p['crops'][ci]['w'] for p in seg]
            hs = [p['crops'][ci]['h'] for p in seg]
            
            # Smooth coordinates for this segment (Strong window for cinematic feel)
            # 51 frames at 8fps = 6.3 seconds window
            w_size = min(51, len(seg))
            if w_size % 2 == 0: w_size -= 1
            if w_size >= 5:
                p_poly = min(3, w_size - 1)
                xs_s = savgol_filter(xs, w_size, p_poly).tolist()
                ys_s = savgol_filter(ys, w_size, p_poly).tolist()
                ws_s = savgol_filter(ws, w_size, p_poly).tolist()
                hs_s = savgol_filter(hs, w_size, p_poly).tolist()
                for i, p in enumerate(seg):
                    p['crops'][ci]['x'] = xs_s[i]
                    p['crops'][ci]['y'] = ys_s[i]
                    p['crops'][ci]['w'] = ws_s[i]
                    p['crops'][ci]['h'] = hs_s[i]
                    
        smoothed_plan.extend(seg)
        
    return smoothed_plan


# ── Renderer ────────────────────────────────────────────────
def render_clip(video_path, output_path, start_time, end_time, crop_plan, 
                transcript_path=None, watermark="", title="", intro_hook="", content_type="gameplay"):
    """PASS 2: Render the final clip using precomputed crop plan.
    Uses FFmpeg pipe for high-quality encoding."""
    
    print(f"[PASS 2] Rendering {start_time:.1f}s - {end_time:.1f}s ...")
    
    video = VideoFileClip(video_path)
    clip = video.subclipped(start_time, end_time)
    v_w, v_h = clip.size
    
    # Standard dynamic vertical HD / Full HD resolution
    if v_h >= 1080:
        target_h = 1920
        target_w = 1080
    else:
        target_h = 1280
        target_w = 720
        
    scale_factor = target_h / 1080.0
    
    src_fps = clip.fps or 30
    duration = clip.duration
    mode = crop_plan[0]['mode'] if crop_plan else 'single'

    # Precompute subtitle data
    sub_data = _load_subtitles(transcript_path, start_time) if transcript_path else None
    
    # Precompute font scaled proportionally
    try:
        font_sub = ImageFont.truetype("arialbd.ttf", int(32 * scale_factor))
    except:
        font_sub = ImageFont.load_default()
    try:
        font_title = ImageFont.truetype("arialbd.ttf", int(18 * scale_factor))
    except:
        font_title = ImageFont.load_default()
    try:
        font_hook = ImageFont.truetype("Inkfree.ttf", int(45 * scale_factor))
    except:
        try:
            font_hook = ImageFont.truetype("arialbd.ttf", int(40 * scale_factor))
        except:
            font_hook = ImageFont.load_default()

    def get_crop_at_time(t):
        """Interpolate crop plan at time t for ultra-smooth movement."""
        if not crop_plan:
            return [{'x': 0, 'y': 0, 'w': v_w, 'h': v_h}], 'single'
        
        # 1. Find the bracketing keyframes (p1 <= t < p2)
        idx1 = 0
        for i, p in enumerate(crop_plan):
            if p['time'] <= t:
                idx1 = i
            else:
                break
        
        p1 = crop_plan[idx1]
        
        # If we're at the very last keyframe, no interpolation possible
        if idx1 + 1 >= len(crop_plan):
            return p1['crops'], p1['mode']
            
        p2 = crop_plan[idx1 + 1]
        
        # 2. Safety Check: If modes differ or number of crops differ, it's a hard cut
        if p1['mode'] != p2['mode'] or len(p1['crops']) != len(p2['crops']):
            return p1['crops'], p1['mode']
            
        # 3. Linear Interpolation
        t1 = p1['time']
        t2 = p2['time']
        if t2 <= t1:
            return p1['crops'], p1['mode']
            
        alpha = (t - t1) / (t2 - t1)
        
        interp_crops = []
        for c1, c2 in zip(p1['crops'], p2['crops']):
            interp_crops.append({
                'x': c1['x'] + alpha * (c2['x'] - c1['x']),
                'y': c1['y'] + alpha * (c2['y'] - c1['y']),
                'w': c1['w'] + alpha * (c2['w'] - c1['w']),
                'h': c1['h'] + alpha * (c2['h'] - c1['h'])
            })
        return interp_crops, p1['mode']

    def make_frame(t):
        frame_rgb = clip.get_frame(t)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        crops, m = get_crop_at_time(t)

        if m == 'split2':
            half_h = target_h // 2
            panels = []
            for cr in crops[:2]:
                panel = _crop_and_resize(frame_bgr, cr, target_w, half_h)
                panels.append(panel)
            while len(panels) < 2:
                panels.append(np.zeros((half_h, target_w, 3), dtype=np.uint8))
            combined = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            combined[0:half_h, :] = panels[0]
            combined[half_h:target_h, :] = panels[1]
            # Divider lines
            cv2.line(combined, (0, half_h), (target_w, half_h), (255, 255, 255), 2)
            result = combined

        elif m == 'split3':
            third_h = target_h // 3
            panels = []
            for cr in crops[:3]:
                panel = _crop_and_resize(frame_bgr, cr, target_w, third_h)
                panels.append(panel)
            while len(panels) < 3:
                panels.append(np.zeros((third_h, target_w, 3), dtype=np.uint8))
            combined = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            combined[0:third_h, :] = panels[0]
            combined[third_h:2*third_h, :] = panels[1]
            combined[2*third_h:3*third_h, :] = panels[2]
            # Handle remainder pixels
            remainder = target_h - 3 * third_h
            if remainder > 0:
                combined[3*third_h:, :] = panels[2][-remainder:, :]
            cv2.line(combined, (0, third_h), (target_w, third_h), (255, 255, 255), 2)
            cv2.line(combined, (0, 2*third_h), (target_w, 2*third_h), (255, 255, 255), 2)
            result = combined

        else:  # single
            cr = crops[0] if crops else {'x': 0, 'y': 0, 'w': v_w, 'h': v_h}
            result = _crop_and_resize(frame_bgr, cr, target_w, target_h)

        # Overlays
        result = _draw_overlays(result, t, duration, target_w, target_h, 
                                sub_data, title, intro_hook, watermark,
                                font_sub, font_title, font_hook, start_time, scale_factor,
                                content_type=content_type)
        return cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    # Create VideoClip and export with high quality settings
    final_clip = VideoClip(make_frame, duration=duration).with_fps(src_fps)
    if clip.audio:
        final_clip = final_clip.with_audio(clip.audio)

    print("[PASS 2] Encoding with high quality settings (CRF 18, preset medium)...")
    final_clip.write_videofile(
        output_path, codec="libx264", audio_codec="aac",
        fps=src_fps,
        threads=4,
        preset="medium",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger=None
    )

    # Thumbnail
    thumb_path = output_path.replace('.mp4', '.jpg')
    final_clip.save_frame(thumb_path, t=duration / 2)
    print(f"[PASS 2] Thumbnail: {thumb_path}")

    # Cleanup
    video.close()
    final_clip.close()
    del video, clip, final_clip
    gc.collect()
    print(f"[+] Final clip ready: {output_path}")


def _crop_and_resize(frame_bgr, crop, out_w, out_h, sharpen=True):
    """Crop frame and resize with Lanczos interpolation (sharper than bilinear) and optional unsharp mask."""
    fh, fw = frame_bgr.shape[:2]
    x1 = int(max(0, crop['x']))
    y1 = int(max(0, crop['y']))
    x2 = int(min(fw, x1 + crop['w']))
    y2 = int(min(fh, y1 + crop['h']))
    
    if x2 <= x1 or y2 <= y1:
        return np.zeros((out_h, out_w, 3), dtype=np.uint8)
    
    cropped = frame_bgr[y1:y2, x1:x2]
    resized = cv2.resize(cropped, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)
    
    if sharpen:
        # High quality subtle Gaussian unsharp mask to make the video look extremely crisp and clear ("jernih")
        blurred = cv2.GaussianBlur(resized, (0, 0), 1.5)
        # alpha = 1.3, beta = -0.3 -> output = resized * 1.3 - blurred * 0.3
        resized = cv2.addWeighted(resized, 1.3, blurred, -0.3, 0)
        
    return resized


def _load_subtitles(transcript_path, start_time):
    """Load word-level subtitle data from transcript."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # If it's the new structured JSON from clipper.py
        if 'subtitle_mode' in data:
            subtitle_mode = data.get('subtitle_mode', 'id')
            detected_language = data.get('detected_language', 'id')
            raw_segments = data.get('segments', [])
            
            processed_segments = []
            for seg in raw_segments:
                start = float(seg.get('start', 0.0))
                end = float(seg.get('end', 0.0))
                text_en = seg.get('text_en', '')
                text_id = seg.get('text_id', '')
                
                # Check for words_en
                words_en = seg.get('words_en', [])
                if not words_en:
                    wl_en = text_en.split()
                    dur = end - start
                    for j, w in enumerate(wl_en):
                        words_en.append({
                            'word': w,
                            'start': start + (j * dur / max(1, len(wl_en))),
                            'end': start + ((j + 1) * dur / max(1, len(wl_en)))
                        })
                
                # Check for words_id
                words_id = seg.get('words_id', [])
                if not words_id:
                    wl_id = text_id.split()
                    dur = end - start
                    for j, w in enumerate(wl_id):
                        words_id.append({
                            'word': w,
                            'start': start + (j * dur / max(1, len(wl_id))),
                            'end': start + ((j + 1) * dur / max(1, len(wl_id)))
                        })
                
                processed_segments.append({
                    'start': start,
                    'end': end,
                    'text_en': text_en,
                    'text_id': text_id,
                    'words_en': words_en,
                    'words_id': words_id
                })
            
            return {
                'subtitle_mode': subtitle_mode,
                'detected_language': detected_language,
                'segments': processed_segments,
                'offset': start_time
            }
        
        # Backward compatibility for old style transcript.json
        words = []
        for seg in data.get('segments', []):
            if 'words' in seg:
                words.extend(seg['words'])
            else:
                wl = seg['text'].split()
                dur = seg['end'] - seg['start']
                for i, w in enumerate(wl):
                    words.append({
                        'word': w,
                        'start': seg['start'] + (i * dur / len(wl)),
                        'end': seg['start'] + ((i + 1) * dur / len(wl))
                    })
        chunks = [words[i:i+3] for i in range(0, len(words), 3)]
        
        segments = []
        for chunk in chunks:
            if not chunk: continue
            txt = " ".join([w['word'] for w in chunk])
            segments.append({
                'start': chunk[0]['start'],
                'end': chunk[-1]['end'],
                'text_en': txt,
                'text_id': txt,
                'words_en': chunk,
                'words_id': chunk
            })
            
        return {
            'subtitle_mode': 'id',
            'detected_language': 'id',
            'segments': segments,
            'offset': start_time
        }
    except Exception as e:
        print(f"Warning: Failed to load subtitles: {e}")
        return None


def _draw_single_line_subtitle(draw, words_list, abs_t, tw, y_center, default_fs=32, style="gameplay"):
    """Draw a single line of subtitles with word-by-word karaoke highlighting and auto-scaling font size."""
    if not words_list:
        return
    
    font_size = default_fs
    font_to_use = None
    
    while font_size >= 14:
        try:
            font_to_use = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            try:
                font_to_use = ImageFont.truetype("arial.ttf", font_size)
            except:
                font_to_use = ImageFont.load_default()
            
        words_text = [w['word'].strip().upper() for w in words_list]
        try:
            total_w = sum(draw.textlength(w + " ", font=font_to_use) for w in words_text)
        except AttributeError:
            total_w = sum(draw.textbbox((0,0), w + " ", font=font_to_use)[2] for w in words_text)
        
        if total_w <= tw - 40 or font_size == 14:
            break
        font_size -= 2
        
    words_text = [w['word'].strip().upper() for w in words_list]
    try:
        total_w = sum(draw.textlength(w + " ", font=font_to_use) for w in words_text)
    except AttributeError:
        total_w = sum(draw.textbbox((0,0), w + " ", font=font_to_use)[2] for w in words_text)
        
    curr_x = (tw - total_w) / 2
    
    active_idx = -1
    for idx, w in enumerate(words_list):
        if w['start'] <= abs_t <= w['end']:
            active_idx = idx
            break
            
    if active_idx == -1 and words_list:
        if abs_t < words_list[0]['start']:
            active_idx = 0
        elif abs_t > words_list[-1]['end']:
            active_idx = len(words_list) - 1
        else:
            closest_idx = 0
            min_diff = float('inf')
            for idx, w in enumerate(words_list):
                diff = min(abs(abs_t - w['start']), abs(abs_t - w['end']))
                if diff < min_diff:
                    min_diff = diff
                    closest_idx = idx
            active_idx = closest_idx
            
    for i, wt in enumerate(words_text):
        if style == "gameplay":
            color = (0, 255, 255) if i == active_idx else (255, 255, 255)  # Neon cyan for active gameplay
        else:
            color = (255, 255, 0) if i == active_idx else (255, 255, 255)  # Yellow for other modes
        
        # Dynamic outline size relative to font size
        outline_px = max(1, int(font_size * 0.07))
        offsets = [(dx, dy) for dx in range(-outline_px, outline_px + 1)
                   for dy in range(-outline_px, outline_px + 1)
                   if dx*dx + dy*dy <= outline_px*outline_px and (dx != 0 or dy != 0)]
        for dx, dy in offsets:
            draw.text((curr_x+dx, y_center+dy), wt, font=font_to_use, fill="black", anchor="lm")
            
        draw.text((curr_x, y_center), wt, font=font_to_use, fill=color, anchor="lm")
        try:
            curr_x += draw.textlength(wt + " ", font=font_to_use)
        except AttributeError:
            curr_x += draw.textbbox((0,0), wt + " ", font=font_to_use)[2]


def _draw_centered_text(draw, text, tw, y_center, default_fs=18, color=(255, 255, 255), style="gameplay"):
    """Draw centered static text with auto-scaling font size and wrapping."""
    if not text:
        return
        
    text_str = text.strip().upper()
    font_size = default_fs
    font_to_use = None
    
    while font_size >= 12:
        try:
            font_to_use = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            try:
                font_to_use = ImageFont.truetype("arial.ttf", font_size)
            except:
                font_to_use = ImageFont.load_default()
            
        try:
            text_w = draw.textlength(text_str, font=font_to_use)
        except AttributeError:
            text_w = draw.textbbox((0,0), text_str, font=font_to_use)[2]
            
        if text_w <= tw - 40 or font_size == 12:
            break
        font_size -= 1
        
    try:
        final_w = draw.textlength(text_str, font=font_to_use)
    except AttributeError:
        final_w = draw.textbbox((0,0), text_str, font=font_to_use)[2]
        
    if final_w > tw - 40:
        wrapped_lines = textwrap.wrap(text_str, width=35)
        lc = len(wrapped_lines)
        y_offset = y_center - (lc - 1) * (font_size + 4) / 2
        outline_px = max(1, int(font_size * 0.07))
        offsets = [(dx, dy) for dx in range(-outline_px, outline_px + 1)
                   for dy in range(-outline_px, outline_px + 1)
                   if dx*dx + dy*dy <= outline_px*outline_px and (dx != 0 or dy != 0)]
        for line in wrapped_lines:
            try:
                line_w = draw.textlength(line, font=font_to_use)
            except AttributeError:
                line_w = draw.textbbox((0,0), line, font=font_to_use)[2]
            line_x = (tw - line_w) / 2
            for dx, dy in offsets:
                draw.text((line_x+dx, y_offset+dy), line, font=font_to_use, fill="black", anchor="lm")
            draw.text((line_x, y_offset), line, font=font_to_use, fill=color, anchor="lm")
            y_offset += font_size + 4
    else:
        outline_px = max(1, int(font_size * 0.07))
        offsets = [(dx, dy) for dx in range(-outline_px, outline_px + 1)
                   for dy in range(-outline_px, outline_px + 1)
                   if dx*dx + dy*dy <= outline_px*outline_px and (dx != 0 or dy != 0)]
        line_x = (tw - final_w) / 2
        for dx, dy in offsets:
            draw.text((line_x+dx, y_center+dy), text_str, font=font_to_use, fill="black", anchor="lm")
        draw.text((line_x, y_center), text_str, font=font_to_use, fill=color, anchor="lm")


def _draw_overlays(frame, t, duration, tw, th, sub_data, title, intro_hook, 
                   watermark, font_sub, font_title, font_hook, start_time, scale_factor=1.0,
                   content_type="gameplay"):
    """Draw subtitle, title, intro hook, progress bar onto frame.
    scale_factor: 1.0 = 1080p (1080x1920), 0.667 = 720p (720x1280)
    All pixel values are proportionally scaled from their 1080p baseline.
    """
    # Progress bar (bottom, after 3s) - scaled height
    if t > 3.0:
        bar_h = max(4, int(6 * scale_factor))
        progress = t / duration
        frame[th - bar_h:th, :] = [50, 50, 50]
        end_x = int(progress * tw)
        frame[th - bar_h:th, :end_x] = [0, 255, 255]  # Cyan in BGR

    # Solid black frame and smooth cross-fade between 2.5s and 3.0s
    if t < 3.0:
        video_fade = min(1.0, (3.0 - t) / 0.5) if t > 2.5 else 1.0
        frame[:, :] = (frame[:, :] * (1.0 - video_fade)).astype(np.uint8)

    # Intro Hook (first 3 seconds) - all coordinates scaled
    if intro_hook and t < 3.0:
        alpha = min(1.0, (3.0 - t) / 0.5) if t > 2.5 else 1.0
        hook_text = intro_hook.strip().upper()
        wrapped = "\n".join(textwrap.wrap(hook_text, width=12))
        img = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Scaled thick black outline
        outline_thickness = max(2, int(4 * scale_factor))
        for dx in range(-outline_thickness, outline_thickness + 1):
            for dy in range(-outline_thickness, outline_thickness + 1):
                if dx*dx + dy*dy <= outline_thickness*outline_thickness:
                    draw.text((tw/2+dx, th/2+dy), wrapped, font=font_hook, fill="black", anchor="mm", align="center")
                    
        # Gold text
        draw.text((tw/2, th/2), wrapped, font=font_hook, fill=(255, 215, 0, 255), anchor="mm", align="center")
        
        overlay = np.array(img)
        mask = (overlay[:,:,3] > 0).astype(np.float32) * alpha
        for c in range(3):
            frame[:,:,c] = (frame[:,:,c] * (1 - mask) + overlay[:,:,2-c] * mask).astype(np.uint8)

    # Title (after 3s) - box height and stroke scaled
    if title and t >= 3.0:
        ttxt = title.strip().upper()
        wrapped_t = "\n".join(textwrap.wrap(ttxt, width=24))
        lc = wrapped_t.count('\n') + 1
        hh = int((40 + lc * 20) * scale_factor)
        img = Image.new('RGBA', (tw, hh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Scaled stroke/outline
        stroke_w = max(1, int(3 * scale_factor))
        for dx in range(-stroke_w, stroke_w + 1):
            for dy in range(-stroke_w, stroke_w + 1):
                if dx*dx + dy*dy <= stroke_w*stroke_w:
                    draw.text((tw/2+dx, hh/2+dy), wrapped_t, font=font_title, fill="black", anchor="mm", align="center")
                    
        # Gold text
        draw.text((tw/2, hh/2), wrapped_t, font=font_title, fill=(255, 215, 0, 255), anchor="mm", align="center")
        
        overlay = np.array(img)
        mask = (overlay[:,:,3] > 0).astype(np.float32)
        y_start = max(0, int(5 * scale_factor))
        y_end = min(y_start + hh, th)
        for c in range(3):
            frame[y_start:y_end, :, c] = (
                frame[y_start:y_end, :, c] * (1 - mask[:y_end-y_start]) + 
                overlay[:y_end-y_start, :, 2-c] * mask[:y_end-y_start]
            ).astype(np.uint8)

    # Subtitles (after 3s) - box height and positions scaled
    if sub_data and t >= 3.0:
        abs_t = t + start_time
        subtitle_mode = sub_data.get('subtitle_mode', 'id')
        detected_language = sub_data.get('detected_language', 'id')
        segments = sub_data.get('segments', [])
        
        active_segment = None
        for seg in segments:
            if seg['start'] <= abs_t <= seg['end']:
                active_segment = seg
                break
                
        if active_segment:
            sub_h = int(200 * scale_factor)
            img = Image.new('RGBA', (tw, sub_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            y_center_main = int(80 * scale_factor)
            y_center_dual1 = int(60 * scale_factor)
            y_center_dual2 = int(130 * scale_factor)
            fs_main = int(32 * scale_factor)
            fs_dual1 = int(24 * scale_factor)
            fs_dual2 = int(18 * scale_factor)
            
            if subtitle_mode == 'en':
                _draw_single_line_subtitle(draw, active_segment['words_en'], abs_t, tw,
                                           y_center=y_center_main, default_fs=fs_main, style=content_type)
            elif subtitle_mode == 'id':
                _draw_single_line_subtitle(draw, active_segment['words_id'], abs_t, tw,
                                           y_center=y_center_main, default_fs=fs_main, style=content_type)
            elif subtitle_mode == 'dual':
                if detected_language == 'en':
                    _draw_single_line_subtitle(draw, active_segment['words_en'], abs_t, tw,
                                               y_center=y_center_dual1, default_fs=fs_dual1, style=content_type)
                    _draw_centered_text(draw, active_segment['text_id'], tw,
                                        y_center=y_center_dual2, default_fs=fs_dual2, color=(255, 255, 255), style=content_type)
                else:
                    _draw_single_line_subtitle(draw, active_segment['words_id'], abs_t, tw,
                                               y_center=y_center_dual1, default_fs=fs_dual1, style=content_type)
                    _draw_centered_text(draw, active_segment['text_en'], tw,
                                        y_center=y_center_dual2, default_fs=fs_dual2, color=(255, 255, 255), style=content_type)
            
            overlay = np.array(img)
            mask = (overlay[:,:,3] > 0).astype(np.float32)
            y_pos = th - int(300 * scale_factor)
            y_end = min(y_pos + sub_h, th)
            if y_pos >= 0:
                h_slice = y_end - y_pos
                for c in range(3):
                    frame[y_pos:y_end, :, c] = (
                        frame[y_pos:y_end, :, c] * (1 - mask[:h_slice]) +
                        overlay[:h_slice, :, 2-c] * mask[:h_slice]
                    ).astype(np.uint8)

    # Watermark - scaled height, font size and position
    if watermark and t > 3.0:
        wm_h = int(50 * scale_factor)
        wm_font_size = max(12, int(20 * scale_factor))
        img = Image.new('RGBA', (tw, wm_h), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        try:
            font_wm = ImageFont.truetype("arial.ttf", wm_font_size)
        except:
            font_wm = ImageFont.load_default()
        draw.text((tw/2, wm_h/2), watermark, font=font_wm, fill=(255,255,255,80), anchor="mm")
        overlay = np.array(img)
        mask = (overlay[:,:,3] > 0).astype(np.float32)
        y_pos = th // 2 + int(50 * scale_factor)
        y_end = min(y_pos + wm_h, th)
        if y_pos >= 0:
            h_s = y_end - y_pos
            for c in range(3):
                frame[y_pos:y_end, :, c] = (
                    frame[y_pos:y_end, :, c] * (1 - mask[:h_s]) +
                    overlay[:h_s, :, 2-c] * mask[:h_s]
                ).astype(np.uint8)

    return frame


# ── Main Entry Point ────────────────────────────────────────
def reframe_and_subtitle(video_path, output_path, start_time, end_time,
                         transcript_path=None, watermark="", title="",
                         intro_hook="", split_screen=0, engine_mode="opsi_a", speaker_timeline_data=None,
                         content_type="gameplay"):
    """Main entry: 2-pass pipeline for high-quality clip generation."""
    print(f"[*] === 2-PASS PIPELINE START (Content Type: {content_type}) ===")
    print(f"[*] Clip: {start_time}s - {end_time}s | Split: {split_screen} | Engine Mode: {engine_mode}")

    # Get video dimensions
    cap = cv2.VideoCapture(video_path)
    v_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    v_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    target_w = int(v_h * (9 / 16))
    if target_w % 2 != 0:
        target_w += 1

    # PASS 1: Analysis (Pass engine_mode for sparse downsampling optimization in Opsi B)
    analysis = analyze_clip(video_path, start_time, end_time, sample_fps=8, engine_mode=engine_mode)
    if not analysis:
        print("[!] Analysis failed, using fallback")
        analysis = {
            'speakers': {0: {'median_x': 0.5, 'median_y': 0.3, 'xs': [0.5], 'ys': [0.3], 'mars': [0], 'times': [0]}},
            'frames': [{'time': 0, 'abs_time': start_time, 'faces': [], 'audio_rms': 0}],
            'num_speakers': 1, 'src_fps': 30, 'duration': end_time - start_time
        }

    # BUILD CROP PLAN with global smoothing
    is_split = int(split_screen) == 1
    crop_plan = build_crop_plan(analysis, v_w, v_h, target_w, is_split, engine_mode, speaker_timeline_data, content_type)
    print(f"[*] Crop plan: {len(crop_plan)} keyframes, mode={crop_plan[0]['mode'] if crop_plan else 'single'}")

    # PASS 2: Render
    render_clip(video_path, output_path, start_time, end_time, crop_plan,
                transcript_path, watermark, title, intro_hook, content_type)

    print(f"[*] === 2-PASS PIPELINE COMPLETE ===")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(1)
    transcript = sys.argv[5] if len(sys.argv) > 5 else None
    watermark = sys.argv[6] if len(sys.argv) > 6 else ""
    title = sys.argv[7] if len(sys.argv) > 7 else ""
    intro_hook = sys.argv[8] if len(sys.argv) > 8 else ""
    split_screen = sys.argv[9] if len(sys.argv) > 9 else 0
    engine_mode = sys.argv[10] if len(sys.argv) > 10 else "opsi_a"
    
    speaker_timeline_data = None
    if len(sys.argv) > 11 and sys.argv[11]:
        try:
            speaker_timeline_data = json.loads(sys.argv[11])
            print(f"[*] Loaded speaker timeline override data successfully: {len(speaker_timeline_data)} segments")
        except Exception as e:
            print(f"[!] Error parsing speaker timeline JSON: {e}")
            
    content_type = sys.argv[12] if len(sys.argv) > 12 else "gameplay"
            
    reframe_and_subtitle(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]),
                         transcript, watermark, title, intro_hook, split_screen, engine_mode, speaker_timeline_data, content_type)

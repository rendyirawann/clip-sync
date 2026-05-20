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
def build_crop_plan(analysis, v_w, v_h, target_w, split_mode, engine_mode="opsi_a", speaker_timeline_data=None):
    """Convert raw analysis into a smoothed crop plan.
    
    Returns list of dicts: {time, mode, crops: [{x,y,w,h}, ...]}
    mode = 'single' | 'split2' | 'split3' | 'active_focus'
    """
    frames = analysis['frames']
    speakers = analysis['speakers']
    num_sp = analysis['num_speakers']
    speaker_ids = list(speakers.keys())
    duration = analysis['duration']

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
                transcript_path=None, watermark="", title="", intro_hook=""):
    """PASS 2: Render the final clip using precomputed crop plan.
    Uses FFmpeg pipe for high-quality encoding."""
    
    print(f"[PASS 2] Rendering {start_time:.1f}s - {end_time:.1f}s ...")
    
    video = VideoFileClip(video_path)
    clip = video.subclipped(start_time, end_time)
    v_w, v_h = clip.size
    target_w = int(v_h * (9 / 16))
    if target_w % 2 != 0:
        target_w += 1
    src_fps = clip.fps or 30
    duration = clip.duration
    mode = crop_plan[0]['mode'] if crop_plan else 'single'

    # Precompute subtitle data
    sub_data = _load_subtitles(transcript_path, start_time) if transcript_path else None
    
    # Precompute font
    try:
        font_sub = ImageFont.truetype("arialbd.ttf", 32)
    except:
        font_sub = ImageFont.load_default()
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 24)
    except:
        font_title = ImageFont.load_default()
    try:
        font_hook = ImageFont.truetype("Inkfree.ttf", 45)
    except:
        try:
            font_hook = ImageFont.truetype("arialbd.ttf", 40)
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
            half_h = v_h // 2
            panels = []
            for cr in crops[:2]:
                panel = _crop_and_resize(frame_bgr, cr, target_w, half_h)
                panels.append(panel)
            while len(panels) < 2:
                panels.append(np.zeros((half_h, target_w, 3), dtype=np.uint8))
            combined = np.zeros((v_h, target_w, 3), dtype=np.uint8)
            combined[0:half_h, :] = panels[0]
            combined[half_h:v_h, :] = panels[1]
            # Divider lines
            cv2.line(combined, (0, half_h), (target_w, half_h), (255, 255, 255), 2)
            result = combined

        elif m == 'split3':
            third_h = v_h // 3
            panels = []
            for cr in crops[:3]:
                panel = _crop_and_resize(frame_bgr, cr, target_w, third_h)
                panels.append(panel)
            while len(panels) < 3:
                panels.append(np.zeros((third_h, target_w, 3), dtype=np.uint8))
            combined = np.zeros((v_h, target_w, 3), dtype=np.uint8)
            combined[0:third_h, :] = panels[0]
            combined[third_h:2*third_h, :] = panels[1]
            combined[2*third_h:3*third_h, :] = panels[2]
            # Handle remainder pixels
            remainder = v_h - 3 * third_h
            if remainder > 0:
                combined[3*third_h:, :] = panels[2][-remainder:, :]
            cv2.line(combined, (0, third_h), (target_w, third_h), (255, 255, 255), 2)
            cv2.line(combined, (0, 2*third_h), (target_w, 2*third_h), (255, 255, 255), 2)
            result = combined

        else:  # single
            cr = crops[0] if crops else {'x': 0, 'y': 0, 'w': v_w, 'h': v_h}
            result = _crop_and_resize(frame_bgr, cr, target_w, v_h)

        # Overlays
        result = _draw_overlays(result, t, duration, target_w, v_h, 
                                sub_data, title, intro_hook, watermark,
                                font_sub, font_title, font_hook, start_time)
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


def _crop_and_resize(frame_bgr, crop, out_w, out_h):
    """Crop frame and resize with Lanczos interpolation (sharper than bilinear)."""
    fh, fw = frame_bgr.shape[:2]
    x1 = int(max(0, crop['x']))
    y1 = int(max(0, crop['y']))
    x2 = int(min(fw, x1 + crop['w']))
    y2 = int(min(fh, y1 + crop['h']))
    
    if x2 <= x1 or y2 <= y1:
        return np.zeros((out_h, out_w, 3), dtype=np.uint8)
    
    cropped = frame_bgr[y1:y2, x1:x2]
    return cv2.resize(cropped, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)


def _load_subtitles(transcript_path, start_time):
    """Load word-level subtitle data from transcript."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
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
        # Group into 3-word chunks
        chunks = [words[i:i+3] for i in range(0, len(words), 3)]
        return {'chunks': chunks, 'offset': start_time}
    except:
        return None


def _draw_overlays(frame, t, duration, tw, th, sub_data, title, intro_hook, 
                   watermark, font_sub, font_title, font_hook, start_time):
    """Draw subtitle, title, intro hook, progress bar onto frame."""
    # Progress bar (bottom, after 3s)
    if t > 3.0:
        bar_h = 6
        progress = t / duration
        frame[th - bar_h:th, :] = [50, 50, 50]
        end_x = int(progress * tw)
        frame[th - bar_h:th, :end_x] = [0, 255, 255]  # Yellow in BGR

    # Intro Hook (first 3 seconds)
    if intro_hook and t < 3.0:
        alpha = min(1.0, (3.0 - t) / 0.5) if t > 2.5 else 1.0
        hook_text = intro_hook.strip().upper()
        wrapped = "\n".join(textwrap.wrap(hook_text, width=12))
        img = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        for dx, dy in [(-3,-3),(-3,3),(3,-3),(3,3),(0,-3),(0,3),(-3,0),(3,0)]:
            draw.text((tw/2+dx, th/2+dy), wrapped, font=font_hook, fill="black", anchor="mm", align="center")
        draw.text((tw/2, th/2), wrapped, font=font_hook, fill="white", anchor="mm", align="center")
        overlay = np.array(img)
        mask = (overlay[:,:,3] > 0).astype(np.float32) * alpha
        for c in range(3):
            frame[:,:,c] = (frame[:,:,c] * (1 - mask) + overlay[:,:,2-c] * mask).astype(np.uint8)

    # Title (after 3s)
    if title and t >= 3.0:
        ttxt = title.strip().upper()
        wrapped_t = "\n".join(textwrap.wrap(ttxt, width=15))
        lc = wrapped_t.count('\n') + 1
        hh = 60 + lc * 25
        img = Image.new('RGBA', (tw, hh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx*dx + dy*dy <= 9:
                    draw.text((tw/2+dx, hh/2+dy), wrapped_t, font=font_title, fill="black", anchor="mm", align="center")
        draw.text((tw/2, hh/2), wrapped_t, font=font_title, fill=(255, 215, 0, 255), anchor="mm", align="center")
        overlay = np.array(img)
        mask = (overlay[:,:,3] > 0).astype(np.float32)
        y_start = 5
        y_end = min(y_start + hh, th)
        for c in range(3):
            frame[y_start:y_end, :, c] = (
                frame[y_start:y_end, :, c] * (1 - mask[:y_end-y_start]) + 
                overlay[:y_end-y_start, :, 2-c] * mask[:y_end-y_start]
            ).astype(np.uint8)

    # Subtitles (after 3s)
    if sub_data and t >= 3.0:
        abs_t = t + start_time
        chunks = sub_data['chunks']
        active_chunk = None
        active_idx = -1
        for chunk in chunks:
            if chunk[0]['start'] <= abs_t <= chunk[-1]['end']:
                active_chunk = chunk
                for j, w in enumerate(chunk):
                    if w['start'] <= abs_t <= w['end']:
                        active_idx = j
                        break
                if active_idx == -1:
                    active_idx = 0
                break
        
        if active_chunk:
            sub_h = 200
            img = Image.new('RGBA', (tw, sub_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            words_text = [w['word'].strip().upper() for w in active_chunk]
            total_w = sum(draw.textlength(w + " ", font=font_sub) for w in words_text)
            curr_x = (tw - total_w) / 2
            for i, wt in enumerate(words_text):
                color = (255, 255, 0) if i == active_idx else (255, 255, 255)
                for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2)]:
                    draw.text((curr_x+dx, 80+dy), wt, font=font_sub, fill="black", anchor="lm")
                draw.text((curr_x, 80), wt, font=font_sub, fill=color, anchor="lm")
                curr_x += draw.textlength(wt + " ", font=font_sub)
            
            overlay = np.array(img)
            mask = (overlay[:,:,3] > 0).astype(np.float32)
            y_pos = th - 300
            y_end = min(y_pos + sub_h, th)
            if y_pos >= 0:
                h_slice = y_end - y_pos
                for c in range(3):
                    frame[y_pos:y_end, :, c] = (
                        frame[y_pos:y_end, :, c] * (1 - mask[:h_slice]) +
                        overlay[:h_slice, :, 2-c] * mask[:h_slice]
                    ).astype(np.uint8)

    # Watermark
    if watermark and t > 3.0:
        wm_h = 50
        img = Image.new('RGBA', (tw, wm_h), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        try:
            font_wm = ImageFont.truetype("arial.ttf", 20)
        except:
            font_wm = ImageFont.load_default()
        draw.text((tw/2, wm_h/2), watermark, font=font_wm, fill=(255,255,255,80), anchor="mm")
        overlay = np.array(img)
        mask = (overlay[:,:,3] > 0).astype(np.float32)
        y_pos = th // 2 + 50
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
                         intro_hook="", split_screen=0, engine_mode="opsi_a", speaker_timeline_data=None):
    """Main entry: 2-pass pipeline for high-quality clip generation."""
    print(f"[*] === 2-PASS PIPELINE START ===")
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
    crop_plan = build_crop_plan(analysis, v_w, v_h, target_w, is_split, engine_mode, speaker_timeline_data)
    print(f"[*] Crop plan: {len(crop_plan)} keyframes, mode={crop_plan[0]['mode'] if crop_plan else 'single'}")

    # PASS 2: Render
    render_clip(video_path, output_path, start_time, end_time, crop_plan,
                transcript_path, watermark, title, intro_hook)

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
            
    reframe_and_subtitle(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]),
                         transcript, watermark, title, intro_hook, split_screen, engine_mode, speaker_timeline_data)

import os
import sys
import argparse
import json
import subprocess
import re
import time

def check_dependencies(ffmpeg_path):
    """Check if ffmpeg exists at the given path or in the system PATH."""
    try:
        subprocess.run([ffmpeg_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        # Try checking in standard PATH
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return "ffmpeg"
        except FileNotFoundError:
            return False

def format_vtt_timestamp(seconds):
    """Format seconds into HH:MM:SS.mmm for WebVTT."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{ms:03d}"

def format_srt_timestamp(seconds):
    """Format seconds into HH:MM:SS,mmm for SRT."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

def seconds_to_hms(seconds):
    """Format seconds to HH:MM:SS."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

def download_youtube(url, output_dir, ytdlp_path):
    """Download a YouTube video using yt-dlp."""
    print(f"Downloading YouTube video from: {url}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as source_video.mp4
    output_template = os.path.join(output_dir, "source_video.%(ext)s")
    
    cmd = [
        ytdlp_path,
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", output_template,
        url
    ]
    
    # Fallback to standard PATH if path is just 'yt-dlp'
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError:
        # Try running using python -m yt_dlp if yt-dlp.exe is not found
        print("yt-dlp executable not found, trying python -m yt_dlp...")
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_template,
            url
        ]
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
    # Find the downloaded file
    for file in os.listdir(output_dir):
        if file.startswith("source_video.") and file.endswith(".mp4"):
            return os.path.join(output_dir, file)
            
    raise FileNotFoundError("Downloaded YouTube video file not found.")

def extract_audio(video_path, output_dir, ffmpeg_path):
    """Extract audio from video file to MP3 format for transcription."""
    print(f"Extracting audio from: {video_path}")
    audio_path = os.path.join(output_dir, "extracted_audio.mp3")
    
    # Check if file exists and delete it
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    cmd = [
        ffmpeg_path,
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]
    
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return audio_path

def analyze_audio_with_gemini(audio_path, api_key):
    """Upload audio to Gemini API, transcribe and extract 3 highlight clips."""
    print("Uploading audio to Gemini for transcription and highlight clipping...")
    
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    
    # Upload the file using File API (recommended for audio files)
    audio_file = genai.upload_file(path=audio_path)
    print(f"Audio file uploaded to Gemini: {audio_file.name}")
    
    # Wait for the file to be processed
    while audio_file.state.name == "PROCESSING":
        print("Gemini is processing the audio file...")
        time.sleep(2)
        audio_file = genai.get_file(audio_file.name)
        
    if audio_file.state.name == "FAILED":
        raise Exception("Gemini audio file processing failed.")
        
    prompt = """
    You are an expert video clipper assistant. Your objective is to analyze the attached audio file and perform the following tasks:
    1. Transcribe the dialogue carefully. The audio might be in Indonesian or English.
    2. Translate the transcript into Indonesian.
       - If the audio is in English, you MUST provide BOTH the original English text ('text_en') and the Indonesian translation ('text_id').
       - If the audio is in Indonesian, you should fill both 'text_en' and 'text_id' with the Indonesian transcript (or leave 'text_en' blank/null).
    3. Identify exactly 3 highly engaging, viral, or interesting highlight segments/clips. Each segment should be between 30 to 90 seconds. These are the peak moments.
    4. Provide the exact start and end seconds relative to the audio file.
    5. Generate a catchy, highly engaging, viral title for each clip, and an extremely appealing social media description (captions) in natural Indonesian explaining what makes this clip amazing, followed by a list of trending/viral hashtags (like #fyp, #viral, #foryou, #podcast, etc.) optimized for TikTok, Instagram Reels, and YouTube Shorts so the user can easily copy-paste and post directly.
    6. For each clip, extract the list of subtitle lines with precise start and end times in seconds, relative to the main video.

    You MUST output your response strictly as a JSON object, with no markdown code blocks or extra text. Use the following JSON schema:
    {
      "clips": [
        {
          "title": "Viral Catchy Title",
          "description": "Engaging Indonesian caption summarizing the clip... \n\n#fyp #viral #foryou #podcast",
          "start_seconds": 45,
          "end_seconds": 95,
          "subtitles": [
            {
              "start": 45.5,
              "end": 49.2,
              "text_en": "Original English sentence",
              "text_id": "Indonesian translation"
            }
          ]
        }
      ]
    }
    """
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Request JSON output
    response = model.generate_content(
        [audio_file, prompt],
        generation_config={"response_mime_type": "application/json"}
    )
    
    # Clean up the file from Gemini cloud
    try:
        genai.delete_file(audio_file.name)
        print("Cleaned up audio file from Gemini Cloud.")
    except Exception as e:
        print(f"Error deleting file from Gemini: {e}")
        
    return json.loads(response.text)

def analyze_audio_locally(audio_path, whisper_model_size, ollama_model):
    """Transcribe audio offline using faster-whisper and detect highlights using local Ollama API."""
    print(f"Loading local Whisper model ({whisper_model_size}) on CPU/RAM...")
    
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError("Library 'faster-whisper' tidak ditemukan. Silakan jalankan 'pip install faster-whisper' di cmd/terminal.")

    try:
        import requests
    except ImportError:
        raise ImportError("Library 'requests' tidak ditemukan. Silakan jalankan 'pip install requests' di cmd/terminal.")

    # 1. Transcribe locally using Whisper
    # Auto-detect Nvidia GPU (CUDA) for extremely fast processing, fallback to CPU
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        device = "cpu"
        
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"Loading local Whisper model ({whisper_model_size}) on: {device.upper()} with {compute_type} precision...")
    
    model = WhisperModel(whisper_model_size, device=device, compute_type=compute_type)
    
    print("Transcribing audio locally... ini akan memakan waktu tergantung spesifikasi RAM laptop Anda.")
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    transcript_segments = []
    full_transcript_text = ""
    
    for segment in segments:
        text = segment.text.strip()
        transcript_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": text
        })
        full_transcript_text += f"[{segment.start:.2f}s - {segment.end:.2f}s]: {text}\n"

    print(f"Transcription completed! Detected language: {info.language}")
    print("Sending transcript to local Ollama LLM for semantic highlight detection...")

    # 2. Call local Ollama API to detect clips
    ollama_url = "http://localhost:11434/api/chat"
    
    prompt = f"""
    You are an expert video clipper assistant. Your objective is to analyze the following transcript text and perform the tasks:
    1. Analyze the transcript dialogue and identify exactly 3 highly engaging, viral, or interesting highlight segments/clips. Each segment should be between 30 to 90 seconds.
    2. Provide the exact start and end seconds relative to the audio file.
    3. Generate a catchy, highly engaging, viral title for each clip, and an extremely appealing social media description (captions) in natural Indonesian explaining what makes this clip amazing, followed by a list of trending/viral hashtags (like #fyp, #viral, #foryou, #podcast, etc.) optimized for TikTok, Instagram Reels, and YouTube Shorts so the user can easily copy-paste and post directly.
    4. Provide the exact subtitles for each clip.
       - If the dialogue is in English, you MUST provide BOTH the original English text ('text_en') and the Indonesian translation ('text_id').
       - If the dialogue is in Indonesian, you should fill both 'text_en' and 'text_id' with the Indonesian transcript.

    Transcript Dialogue:
    {full_transcript_text}

    You MUST output your response strictly as a JSON object, with no markdown code blocks, backticks, or extra text. Use the following JSON schema:
    {{
      "clips": [
        {{
          "title": "Viral Catchy Title",
          "description": "Engaging Indonesian caption summarizing the clip... \n\n#fyp #viral #foryou #podcast",
          "start_seconds": 45,
          "end_seconds": 95,
          "subtitles": [
            {{
              "start": 45.5,
              "end": 49.2,
              "text_en": "Original English sentence",
              "text_id": "Indonesian translation"
            }}
          ]
        }}
      ]
    }}
    """

    payload = {
        "model": ollama_model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "format": "json" # Forces Ollama to return structured JSON
    }

    try:
        response = requests.post(ollama_url, json=payload, timeout=300)
        response.raise_for_status()
        ollama_response = response.json()
        raw_content = ollama_response['message']['content']
        
        # Clean any accidental markdown output
        raw_content = re.sub(r'^```json\s*|\s*```$', '', raw_content.strip(), flags=re.MULTILINE)
        
        return json.loads(raw_content)
    except requests.exceptions.ConnectionError:
        raise Exception(f"Gagal terhubung ke Ollama di http://localhost:11434. Pastikan aplikasi Ollama sudah dinyalakan di laptop Anda dan model '{ollama_model}' sudah di-download.")
    except Exception as e:
        raise Exception(f"Error calling local Ollama LLM: {str(e)}")

def generate_subtitles(subtitles, clip_start, clip_end, output_prefix):
    """Generate SRT and WebVTT subtitle files for a clip."""
    srt_lines = []
    vtt_lines = ["WEBVTT\n"]
    dual_sub_data = []
    
    index = 1
    for sub in subtitles:
        start_sec = sub['start']
        end_sec = sub['end']
        
        # Check if the subtitle lies within the clip
        if start_sec >= clip_start and end_sec <= clip_end:
            # Calculate relative offset
            rel_start = max(0.0, start_sec - clip_start)
            rel_end = max(0.0, end_sec - clip_start)
            
            text_en = sub.get('text_en', '')
            text_id = sub.get('text_id', '')
            
            # Formulate dual subtitles line
            if text_en and text_id and text_en != text_id:
                # English top, Indonesian bottom
                text = f"{text_en}\n{text_id}"
            else:
                text = text_id or text_en
                
            # SRT
            srt_lines.append(f"{index}")
            srt_lines.append(f"{format_srt_timestamp(rel_start)} --> {format_srt_timestamp(rel_end)}")
            srt_lines.append(f"{text}\n")
            
            # VTT
            vtt_lines.append(f"{index}")
            vtt_lines.append(f"{format_vtt_timestamp(rel_start)} --> {format_vtt_timestamp(rel_end)}")
            vtt_lines.append(f"{text}\n")
            
            dual_sub_data.append({
                'index': index,
                'start_seconds': rel_start,
                'end_seconds': rel_end,
                'text_en': text_en,
                'text_id': text_id
            })
            
            index += 1
            
    srt_content = "\n".join(srt_lines)
    vtt_content = "\n".join(vtt_lines)
    
    # Save files
    with open(f"{output_prefix}.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)
        
    with open(f"{output_prefix}.vtt", "w", encoding="utf-8") as f:
        f.write(vtt_content)
        
    return srt_content, vtt_content, dual_sub_data

def slice_video(video_path, start_sec, end_sec, output_path, ffmpeg_path):
    """Slice a video into a smaller clip using FFmpeg."""
    print(f"Slicing clip from {start_sec}s to {end_sec}s...")
    
    if os.path.exists(output_path):
        os.remove(output_path)
        
    cmd = [
        ffmpeg_path,
        "-y",
        "-ss", str(start_sec),
        "-to", str(end_sec),
        "-i", video_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        output_path
    ]
    
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def main():
    parser = argparse.ArgumentParser(description="AI Video Clipper Engine (Hybrid Cloud & Local)")
    parser.add_argument("--source", required=True, help="Video file path or YouTube URL")
    parser.add_argument("--type", choices=["upload", "youtube"], required=True, help="Type of source")
    parser.add_argument("--output-dir", required=True, help="Directory to save the results")
    parser.add_argument("--provider", choices=["gemini", "local"], default="gemini", help="AI Provider: gemini or local")
    parser.add_argument("--api-key", default="", help="Gemini API Key (required for gemini provider)")
    parser.add_argument("--ollama-model", default="llama3", help="Ollama LLM Model name (required for local provider)")
    parser.add_argument("--whisper-model", default="base", help="Local Whisper model: tiny, base, small, medium")
    parser.add_argument("--ffmpeg-path", default="ffmpeg", help="Path to FFmpeg executable")
    parser.add_argument("--ytdlp-path", default="yt-dlp", help="Path to yt-dlp executable")
    
    args = parser.parse_args()
    
    # Check dependencies
    dep_check = check_dependencies(args.ffmpeg_path)
    if not dep_check:
        print(json.dumps({"error": f"FFmpeg not found at '{args.ffmpeg_path}'. Please install FFmpeg."}))
        sys.exit(1)
    elif dep_check == "ffmpeg":
        # FFmpeg is in PATH, use default 'ffmpeg'
        args.ffmpeg_path = "ffmpeg"
        
    # Resolve absolute paths
    os.makedirs(args.output_dir, exist_ok=True)
    
    video_path = None
    video_title = "Video Project"
    
    try:
        # Step 1: Download YouTube if applicable
        if args.type == "youtube":
            # Extract YouTube title using yt-dlp first
            try:
                print("Querying YouTube metadata for video title...")
                title_cmd = [args.ytdlp_path, "--get-title", args.source]
                try:
                    res = subprocess.run(title_cmd, capture_output=True, text=True, check=True)
                    video_title = res.stdout.strip()
                except FileNotFoundError:
                    title_cmd = [sys.executable, "-m", "yt_dlp", "--get-title", args.source]
                    res = subprocess.run(title_cmd, capture_output=True, text=True, check=True)
                    video_title = res.stdout.strip()
                print(f"Extracted YouTube title: {video_title}")
            except Exception as e:
                print(f"Warning: Failed to extract YouTube title: {e}")
                video_title = "YouTube Video"

            video_path = download_youtube(args.source, args.output_dir, args.ytdlp_path)
        else:
            video_path = args.source
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Uploaded source video not found at: {video_path}")
            
            # Extract clean upload title
            raw_title = os.path.splitext(os.path.basename(video_path))[0]
            clean_title = re.sub(r'^\d+_[a-f0-9]+_', '', raw_title)
            clean_title = re.sub(r'^\d+_[a-zA-Z0-9]+_', '', clean_title)
            clean_title = re.sub(r'^\d+_', '', clean_title)
            video_title = clean_title.replace('_', ' ').replace('-', ' ').title()
            print(f"Extracted uploaded file title: {video_title}")
                
        # Step 2: Extract audio
        audio_path = extract_audio(video_path, args.output_dir, args.ffmpeg_path)
        
        # Step 3: Call AI to transcribe and detect highlights (Gemini or Local Offline)
        if args.provider == "gemini":
            if not args.api_key:
                raise ValueError("API Key Gemini diperlukan jika menggunakan provider 'gemini'. Tambahkan di file .env")
            ai_analysis = analyze_audio_with_gemini(audio_path, args.api_key)
        else:
            # Local Offline Mode
            ai_analysis = analyze_audio_locally(audio_path, args.whisper_model, args.ollama_model)
        
        clips_data = []
        
        # Step 4: Cut the 3 clips and write subtitles
        for i, clip in enumerate(ai_analysis.get('clips', [])):
            clip_title = clip.get('title', f"Clip {i+1}")
            clip_desc = clip.get('description', '')
            start_sec = clip.get('start_seconds', 0)
            end_sec = clip.get('end_seconds', start_sec + 30)
            
            clip_filename = f"clip_{i+1}.mp4"
            clip_output_path = os.path.join(args.output_dir, clip_filename)
            
            # Slice video
            slice_video(video_path, start_sec, end_sec, clip_output_path, args.ffmpeg_path)
            
            # Subtitle prefix
            sub_prefix = os.path.join(args.output_dir, f"clip_{i+1}_sub")
            
            # Generate SRT/VTT for this clip
            srt_content, vtt_content, dual_subs = generate_subtitles(
                clip.get('subtitles', []),
                start_sec,
                end_sec,
                sub_prefix
            )
            
            clips_data.append({
                'title': clip_title,
                'description': clip_desc,
                'start_time': seconds_to_hms(start_sec),
                'end_time': seconds_to_hms(end_sec),
                'start_seconds': start_sec,
                'end_seconds': end_sec,
                'clip_filename': clip_filename,
                'vtt_filename': f"clip_{i+1}_sub.vtt",
                'srt_content': srt_content,
                'vtt_content': vtt_content,
                'subtitles_dual': dual_subs
            })
            
        # Output final result back as JSON for Laravel
        output_result = {
            'status': 'success',
            'video_title': video_title,
            'source_video_downloaded': video_path if args.type == "youtube" else None,
            'clips': clips_data
        }
        print("SUCCESS_MARKER_JSON_START")
        print(json.dumps(output_result))
        print("SUCCESS_MARKER_JSON_END")
        
    except Exception as e:
        print("ERROR_MARKER_JSON_START")
        print(json.dumps({"error": str(e)}))
        print("ERROR_MARKER_JSON_END")
        sys.exit(1)

if __name__ == "__main__":
    main()

import os
import sys
import argparse
import json
import subprocess
import re
import time

def clean_and_parse_json(raw_str):
    """Clean and parse a JSON string from LLM robustly, supporting single-quoted formats, markdown blocks, etc."""
    raw_str = raw_str.strip()
    
    # 1. Clean markdown json codeblock wrapping
    raw_str = re.sub(r'^```(?:json)?\s*', '', raw_str, flags=re.IGNORECASE)
    raw_str = re.sub(r'\s*```$', '', raw_str)
    raw_str = raw_str.strip()
    
    # 2. Try standard json loads
    try:
        return json.loads(raw_str)
    except json.JSONDecodeError:
        pass
        
    # 3. Fallback to ast.literal_eval if it contains single quotes or trailing commas
    # We substitute JSON null/true/false with Python None/True/False
    try:
        import ast
        py_str = re.sub(r'\btrue\b', 'True', raw_str)
        py_str = re.sub(r'\bfalse\b', 'False', py_str)
        py_str = re.sub(r'\bnull\b', 'None', py_str)
        
        parsed = ast.literal_eval(py_str)
        if isinstance(parsed, (dict, list)):
            return parsed
    except Exception as e:
        print(f"ast.literal_eval fallback failed: {e}")
        
    # 4. Fallback: Search for any JSON dictionary or list inside the string
    try:
        match = re.search(r'(\{.*\}|\[.*\])', raw_str, re.DOTALL)
        if match:
            candidate = match.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                try:
                    import ast
                    py_candidate = re.sub(r'\btrue\b', 'True', candidate)
                    py_candidate = re.sub(r'\bfalse\b', 'False', py_candidate)
                    py_candidate = re.sub(r'\bnull\b', 'None', py_candidate)
                    parsed = ast.literal_eval(py_candidate)
                    if isinstance(parsed, (dict, list)):
                        return parsed
                except Exception:
                    pass
    except Exception:
        pass
        
    # If all fallbacks fail, do a final try or raise the original error
    return json.loads(raw_str)

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

def _decompose_seconds(seconds):
    """Decompose seconds into (hours, minutes, seconds, milliseconds)."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return hrs, mins, secs, ms

def format_vtt_timestamp(seconds):
    """Format seconds into HH:MM:SS.mmm for WebVTT."""
    h, m, s, ms = _decompose_seconds(seconds)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

def format_srt_timestamp(seconds):
    """Format seconds into HH:MM:SS,mmm for SRT."""
    h, m, s, ms = _decompose_seconds(seconds)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def seconds_to_hms(seconds):
    """Format seconds to HH:MM:SS."""
    h, m, s, _ = _decompose_seconds(seconds)
    return f"{h:02d}:{m:02d}:{s:02d}"

def _build_watermark_filter(watermark):
    """Build FFmpeg drawtext filter for watermark, handling Windows font paths."""
    if not watermark:
        return None
    font_arg = "fontfile='C\\:/Windows/Fonts/arial.ttf':" if os.name == 'nt' else ""
    return f"drawtext=text='{watermark}':{font_arg}fontcolor=white@0.3:fontsize=28:x=(w-text_w)/2:y=(h-text_h)/2"

def _try_refresh_cookies_via_edge():
    """Try to extract fresh Edge cookies using rookiepy. Returns path or None."""
    out_path = os.path.join(os.path.dirname(__file__), "cookies_auto.txt")
    try:
        import rookiepy
        cookies = rookiepy.edge([".youtube.com", "youtube.com"])
        if not cookies:
            return None
        
        lines = ["# Netscape HTTP Cookie File", "# Auto-extracted from Edge by Clip-Sync", ""]
        for c in cookies:
            domain = c.get("domain", "")
            flag = "TRUE" if domain.startswith(".") else "FALSE"
            path = c.get("path", "/")
            secure = "TRUE" if c.get("secure", False) else "FALSE"
            expires = int(c.get("expires", 0) or (time.time() + 31536000))
            name = c.get("name", "")
            value = c.get("value", "")
            lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}")
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"Auto-refreshed {len(cookies)} Edge cookies to {out_path}")
        return out_path
    except Exception as e:
        print(f"Note: Auto-refresh Edge cookies skipped ({e})")
        return None

def get_active_cookies_path():
    """Find the best available cookies file. Priority: cookies_auto.txt > cookies.txt (with JSON conversion)."""
    base_dir = os.path.dirname(__file__)
    
    # Priority 1: cookies_auto.txt (from Edge via rookiepy / refresh_cookies.bat)
    auto_path = os.path.join(base_dir, "cookies_auto.txt")
    if os.path.exists(auto_path):
        age_seconds = time.time() - os.path.getmtime(auto_path)
        if age_seconds < 1800:  # Less than 30 minutes old = still fresh
            print(f"Using auto-extracted Edge cookies (age: {int(age_seconds)}s)")
            return auto_path
        else:
            # Try to refresh automatically
            print(f"Edge cookies are {int(age_seconds/60)} min old, attempting auto-refresh...")
            refreshed = _try_refresh_cookies_via_edge()
            if refreshed:
                return refreshed
            # If refresh failed, still use the old file as fallback
            print("Auto-refresh failed, using existing cookies_auto.txt as fallback.")
            return auto_path
    
    # Priority 2: Try auto-extract from Edge (first time)
    refreshed = _try_refresh_cookies_via_edge()
    if refreshed:
        return refreshed
    
    # Priority 3: Manual cookies.txt (with JSON auto-conversion)
    cookies_path = os.path.join(base_dir, "cookies.txt")
    if not os.path.exists(cookies_path):
        return None
        
    try:
        with open(cookies_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
    except Exception:
        return None
        
    if not content:
        return None
        
    # Auto-convert JSON to Netscape if needed
    if content.startswith("[") and content.endswith("]"):
        print("Detected JSON formatted cookies. Converting to Netscape format...")
        try:
            cookies_json = json.loads(content)
            netscape_lines = ["# Netscape HTTP Cookie File", ""]
            for cookie in cookies_json:
                domain = cookie.get("domain", "")
                flag = "TRUE" if domain.startswith(".") else "FALSE"
                path = cookie.get("path", "/")
                secure = "TRUE" if cookie.get("secure", False) else "FALSE"
                expiration = int(cookie.get("expirationDate") or cookie.get("expiry") or (time.time() + 31536000))
                name = cookie.get("name", "")
                value = cookie.get("value", "")
                netscape_lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}")
            converted_path = os.path.join(base_dir, "cookies_netscape.txt")
            with open(converted_path, "w", encoding="utf-8") as out:
                out.write("\n".join(netscape_lines) + "\n")
            return converted_path
        except Exception:
            pass
            
    return cookies_path

def _run_ytdlp_download(cmd):
    """Run a yt-dlp command and return (success, error_message)."""
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, ""
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "") + (e.stdout or "")
        return False, stderr
    except FileNotFoundError:
        return False, "yt-dlp executable not found"

def download_youtube(url, output_dir, ytdlp_path, ffmpeg_path="ffmpeg"):
    """Download a YouTube video using yt-dlp with multi-strategy fallback.

    Strategy order:
    1. --cookies-from-browser edge (user's primary browser)
    2. --cookies-from-browser chrome
    3. cookies file (cookies_auto.txt / cookies.txt)
    4. Plain download (no cookies)
    Each strategy is retried up to 2 times with a delay.
    """
    print(f"Downloading YouTube video from: {url}")
    os.makedirs(output_dir, exist_ok=True)

    # Check if already downloaded
    for file in os.listdir(output_dir):
        if file.startswith("source_video.") and file.endswith(".mp4"):
            print("YouTube video already downloaded, skipping...")
            return os.path.join(output_dir, file)

    output_template = os.path.join(output_dir, "source_video.%(ext)s")

    base_args = [
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        "--merge-output-format", "mp4",
        "--ffmpeg-location", ffmpeg_path,
        "-o", output_template,
        "--js-runtimes", "node",
        "--retries", "3",
        "--fragment-retries", "3",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    ]

    # Build list of strategies to try
    strategies = []

    # Strategy 1: cookies-from-browser edge (user's primary browser)
    strategies.append({
        "name": "cookies-from-browser (Edge)",
        "extra_args": ["--cookies-from-browser", "edge"],
    })

    # Strategy 2: cookies-from-browser chrome
    strategies.append({
        "name": "cookies-from-browser (Chrome)",
        "extra_args": ["--cookies-from-browser", "chrome"],
    })

    # Strategy 3: cookies file (cookies_auto.txt / cookies.txt)
    cookies_path = get_active_cookies_path()
    if cookies_path:
        strategies.append({
            "name": f"cookies file ({os.path.basename(cookies_path)})",
            "extra_args": ["--cookies", cookies_path],
        })

    # Strategy 4: plain download (no cookies)
    strategies.append({
        "name": "tanpa cookies (plain)",
        "extra_args": [],
    })

    last_error = ""
    for strategy in strategies:
        for attempt in range(1, 3):  # max 2 attempts per strategy
            cmd = [ytdlp_path] + base_args + strategy["extra_args"] + [url]

            print(f"[Attempt {attempt}] Strategy: {strategy['name']}...")
            success, error = _run_ytdlp_download(cmd)

            if success:
                # Find the downloaded file
                for file in os.listdir(output_dir):
                    if file.startswith("source_video.") and file.endswith(".mp4"):
                        print(f"Download berhasil dengan strategy: {strategy['name']}")
                        return os.path.join(output_dir, file)

            last_error = error

            # If DPAPI / appbound encryption error, skip this browser strategy
            if "DPAPI" in error or "appbound" in error.lower() or "cannot be decrypted" in error.lower():
                print(f"  Browser cookies tidak bisa dibaca (enkripsi). Mencoba strategi berikutnya...")
                break

            # If "not a bot" / sign-in error, wait before retry
            if "not a bot" in error.lower() or "sign in" in error.lower() or "429" in error:
                if attempt < 2:
                    wait_time = 15 * attempt
                    print(f"  YouTube bot-detection terdeteksi. Menunggu {wait_time} detik sebelum retry...")
                    time.sleep(wait_time)
                continue

            # Other errors - don't retry this strategy
            break

    # All strategies failed
    raise RuntimeError(
        f"Gagal mendownload video YouTube setelah mencoba semua strategi. "
        f"Kemungkinan IP Anda sedang di-rate-limit oleh YouTube. "
        f"Solusi: (1) Ganti jaringan (hotspot HP), "
        f"atau (2) Upload video secara manual via 'Upload PC'. "
        f"Detail error terakhir: {last_error[:300]}"
    )

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

def analyze_audio_with_gemini(audio_path, api_key, clip_count=3, duration_min=30, duration_max=90, language="id"):
    """Upload audio to Gemini API, transcribe and extract highlight clips."""
    print("Uploading audio to Gemini for transcription and highlight clipping...")

    from google import genai
    from google.genai import types

    try:
        client = genai.Client(api_key=api_key)

        # Upload the file using File API (recommended for large audio files)
        print("Uploading audio file to Gemini Files API...")
        with open(audio_path, "rb") as f:
            audio_file = client.files.upload(
                file=f,
                config=types.UploadFileConfig(mime_type="audio/mpeg", display_name="clip_audio")
            )
        print(f"Audio file uploaded: {audio_file.name}")

        # Wait for the file to be processed
        import time as _time
        while audio_file.state.name == "PROCESSING":
            print("Gemini is processing the audio file...")
            _time.sleep(2)
            audio_file = client.files.get(name=audio_file.name)

        if audio_file.state.name == "FAILED":
            raise Exception("Gemini audio file processing failed.")

        lang_desc = "natural English" if language == "en" else "natural Indonesian"

        prompt = f"""
        You are an expert video clipper assistant. Your objective is to analyze the attached audio file and perform the following tasks:
        1. Transcribe the dialogue carefully. The audio might be in Indonesian or English. Ensure the transcribed text has proper, clean punctuation (periods, commas, capitalization, question marks) and format spoken numbers/digits cleanly as digits (e.g., '10.000', '90', '100%') instead of clumsy spelled-out words.
        2. Translate the transcript to support the target language ({language}). Provide BOTH English ('text_en') and Indonesian ('text_id') translations in the 'subtitles' array.
        3. Identify exactly {clip_count} highly engaging, viral, or interesting highlight segments/clips. Each segment should be between {duration_min} to {duration_max} seconds. These are the peak moments.
        4. Provide the exact start and end seconds relative to the audio file.

           CRITICAL TIMESTAMP RULES (PREVENT ABRUPT CUTS):
           - The 'start_seconds' MUST align exactly with the beginning of a complete, natural sentence. Do not start a clip mid-sentence or mid-phrase!
           - The 'end_seconds' MUST align exactly with the end of a complete sentence or when a speaker naturally finishes talking.
           - NEVER cut the video off in the middle of a sentence, word, or clause!
           - If the target duration is e.g. 90 seconds, and at 90s the speaker is in the middle of a sentence, you MUST adjust 'end_seconds' (either cut it slightly earlier e.g. at 82s or extend slightly e.g. at 96s) so that the clip finishes exactly when a sentence or thought naturally ends.
           - The final video MUST feel complete and resolve cleanly, rather than cutting off abruptly.

        5. Generate a catchy, highly engaging, viral title for each clip, and an extremely appealing social media description (captions) in {lang_desc} explaining what makes this clip amazing, followed by a list of trending/viral hashtags (like #fyp, #viral, #foryou, #podcast, etc.) optimized for TikTok, Instagram Reels, and YouTube Shorts so the user can easily copy-paste and post directly.
        6. For each clip, extract the list of subtitle lines with precise start and end times in seconds, relative to the main video.
        7. Generate a catchy, clickbaity overall title for the entire video project ('project_title') in {lang_desc} summarizing the whole conversation context.

        You MUST output your response strictly as a JSON object, with no markdown code blocks or extra text. Use the following JSON schema:
        {{
          "project_title": "Catchy Overall Video Project Title",
          "clips": [
            {{
              "title": "Viral Catchy Title",
              "description": "Engaging caption summarizing the clip... \\n\\n#fyp #viral #foryou #podcast",
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

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_uri(file_uri=audio_file.uri, mime_type="audio/mpeg"),
                prompt
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )

        # Clean up the file from Gemini cloud
        try:
            client.files.delete(name=audio_file.name)
            print("Cleaned up audio file from Gemini Cloud.")
        except Exception as e:
            print(f"Error deleting file from Gemini: {e}")

        return json.loads(response.text)

    except Exception as e:
        print("\n" + "="*80)
        print("ERROR: Gagal memproses audio dengan Gemini API!")
        print(f"Detail Kesalahan: {e}")
        print("="*80)
        
        # Check for Quota Exceeded or Invalid API Key
        err_str = str(e).upper()
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "QUOTA" in err_str:
            print("\n>>> PENTING: Kuota/Limit API Key Gemini Anda telah HABIS (429 Resource Exhausted) oleh Google.")
            print(">>> Silakan buat API Key baru yang segar di: https://aistudio.google.com/apikey")
            print(">>> Setelah itu, update nilai GEMINI_API_KEY di file .env Anda.")
        elif "400" in err_str or "API_KEY_INVALID" in err_str or "INVALID_ARGUMENT" in err_str:
            print("\n>>> PENTING: API Key Gemini Anda TIDAK VALID atau SALAH.")
            print(">>> Silakan periksa kembali dan pastikan GEMINI_API_KEY di file .env sudah sesuai.")
        else:
            print("\n>>> Silakan periksa koneksi internet Anda atau coba lagi beberapa saat lagi.")
        print("="*80 + "\n")
        raise

def transcribe_audio_locally(audio_path, whisper_model_size, device="cpu", target_language="id"):
    """Transcribe audio locally using faster-whisper."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError("Library 'faster-whisper' tidak ditemukan. Silakan jalankan 'pip install faster-whisper' di cmd/terminal.")

    compute_type = "float16" if device == "cuda" else "int8"
    print(f"Loading local Whisper model ({whisper_model_size}) on: {device.upper()} with {compute_type} precision...")
    
    # Run Whisper model
    model = WhisperModel(whisper_model_size, device=device, compute_type=compute_type)
    
    # Select initial prompt based on target language
    if target_language == "en":
        initial_prompt = "Hello! This is a clean transcript of a podcast. Use proper spelling, capitalization, commas, periods, question marks, clean numbers like 10, 5000, 100%, and clear quotes."
    elif target_language == "id":
        initial_prompt = "Halo! Ini adalah transkrip rekaman audio podcast Indonesia. Gunakan ejaan resmi, huruf kapital, tanda baca koma, titik, tanda tanya, angka seperti 10, 5000, 100%, serta kutipan yang jelas dan benar."
    else:
        initial_prompt = "Halo! This is a clean transcript. Gunakan ejaan resmi, capitalization, punctuation, numbers like 10, 5000, 100% cleanly."

    print("Transcribing audio locally... ini akan memakan waktu tergantung spesifikasi RAM laptop Anda.")
    segments, info = model.transcribe(
        audio_path, 
        beam_size=5, 
        language=None, # Let Whisper auto-detect the spoken language
        word_timestamps=True,
        initial_prompt=initial_prompt
    )
    
    transcript_segments = []
    full_transcript_text = ""
    
    for segment in segments:
        text = segment.text.strip()
        words_data = []
        if segment.words:
            for w in segment.words:
                words_data.append({
                    'start': w.start,
                    'end': w.end,
                    'word': w.word
                })
                
        transcript_segments.append({
            'start': segment.start,
            'end': segment.end,
            'text': text,
            'words': words_data if words_data else None
        })
        full_transcript_text += f"[{segment.start:.1f}s - {segment.end:.1f}s] {text}\n"
        
    print(f"Transcription completed! Detected language: {info.language}")
    return transcript_segments, full_transcript_text, info.language

def get_compact_transcript(segments, group_size=8):
    """Group multiple small whisper segments into a single compact paragraph to reduce LLM tokens."""
    compact_lines = []
    current_group = []
    
    for i, seg in enumerate(segments):
        current_group.append(seg)
        if len(current_group) >= group_size or i == len(segments) - 1:
            start_t = current_group[0]['start']
            end_t = current_group[-1]['end']
            merged_text = " ".join([s['text'].strip() for s in current_group])
            compact_lines.append(f"[{start_t:.1f}s - {end_t:.1f}s] {merged_text}")
            current_group = []
            
    return "\n".join(compact_lines)

def translate_subtitles(segments, provider, api_key="", ollama_model="llama3", from_lang="en", to_lang="id"):
    """Translate subtitle segments between English and Indonesian and return dual subtitle list."""
    if not segments:
        return []
        
    print(f"Translating {len(segments)} subtitle segments from {from_lang} to {to_lang} using {provider}...")
    
    # Prepare text lines to translate
    lines_to_translate = []
    for i, seg in enumerate(segments):
        lines_to_translate.append(f"{i} ||| {seg['text']}")
        
    payload_text = "\n".join(lines_to_translate)
    
    from_name = "English" if from_lang == "en" else "Indonesian"
    to_name = "Indonesian" if to_lang == "id" else "English"
    
    prompt = f"""
    You are a professional translator. Translate each of the following numbered {from_name} subtitle lines into natural, expressive {to_name}.
    Keep the number prefix intact. Output only the translated lines, one per line. Do not add any introductory or concluding text.

    Format:
    [Number] ||| [{to_name} Translation]

    {from_name} lines:
    {payload_text}
    """
    
    translations = {}
    
    try:
        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            result_text = response.text.strip()
        else:
            import requests
            ollama_url = "http://localhost:11434/api/chat"
            payload = {
                "model": ollama_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
            res = requests.post(ollama_url, json=payload, timeout=60)
            res.raise_for_status()
            result_text = res.json()['message']['content'].strip()
            
        # Parse translations
        for line in result_text.split('\n'):
            if "|||" in line:
                parts = line.split("|||", 1)
                try:
                    num = int(parts[0].strip().replace('[','').replace(']',''))
                    translations[num] = parts[1].strip()
                except ValueError:
                    continue
    except Exception as e:
        print(f"Warning: Subtitle translation failed ({e}). Falling back to untranslated subtitles.")
        
    # Build final dual subtitles list
    dual_subs = []
    for i, seg in enumerate(segments):
        text_from = seg['text']
        text_to = translations.get(i, text_from)
        
        words_from = seg.get('words', [])
        if not words_from:
            words_list = text_from.split()
            dur = seg['end'] - seg['start']
            for j, w in enumerate(words_list):
                words_from.append({
                    'word': w,
                    'start': seg['start'] + (j * dur / len(words_list)),
                    'end': seg['start'] + ((j + 1) * dur / len(words_list))
                })
                
        # Synthesize words for translated text
        words_to = []
        words_to_list = text_to.split()
        dur = seg['end'] - seg['start']
        for j, w in enumerate(words_to_list):
            words_to.append({
                'word': w,
                'start': seg['start'] + (j * dur / max(1, len(words_to_list))),
                'end': seg['start'] + ((j + 1) * dur / max(1, len(words_to_list)))
            })
            
        if from_lang == "en":
            text_en = text_from
            text_id = text_to
            words_en = words_from
            words_id = words_to
        else:
            text_en = text_to
            text_id = text_from
            words_en = words_to
            words_id = words_from
            
        dual_subs.append({
            'start': seg['start'],
            'end': seg['end'],
            'text_en': text_en,
            'text_id': text_id,
            'words_en': words_en,
            'words_id': words_id
        })
        
    return dual_subs

def analyze_transcript_with_gemini(transcript_text, api_key, clip_count=3, duration_min=30, duration_max=90, language="id"):
    """Send transcript to Gemini API and extract highlight clips (start and end seconds).

    Uses gemini-2.0-flash via the new google-genai SDK for best speed and quality.
    Handles very long transcripts (> 1M tokens) natively without chunking.
    """
    print("Sending transcript to Gemini API for highlight clipping...")

    from google import genai
    from google.genai import types

    try:
        client = genai.Client(api_key=api_key)

        lang_desc = "natural English" if language == "en" else "natural Indonesian"

        prompt = f"""
        You are an expert video clipper assistant. Your objective is to analyze the following transcript dialogue and identify exactly {clip_count} highly engaging, viral, or interesting highlight segments/clips.
        Each segment should be between {duration_min} to {duration_max} seconds. These should represent the peak moments of the video.

        CRITICAL TIMESTAMP RULES (PREVENT ABRUPT CUTS):
        - The 'start_seconds' MUST align exactly with the beginning of a complete, natural sentence. Do not start a clip mid-sentence or mid-phrase!
        - The 'end_seconds' MUST align exactly with the end of a complete sentence or when a speaker naturally finishes talking.
        - NEVER cut the video off in the middle of a sentence, word, or clause!
        - If the target duration is e.g. 90 seconds, and at 90s the speaker is in the middle of a sentence, you MUST adjust 'end_seconds' (either cut it slightly earlier e.g. at 82s or extend slightly e.g. at 96s) so that the clip finishes exactly when a sentence or thought naturally ends.
        - The final video MUST feel complete and resolve cleanly, rather than cutting off abruptly.

        Transcript Dialogue:
        {transcript_text}

        You MUST output your response strictly as a JSON object, with no markdown code blocks or extra text. Use the following JSON schema:
        {{
          "project_title": "Catchy Overall Video Project Title in {lang_desc} summarizing the video context",
          "clips": [
            {{
              "title": "Viral Catchy Title in {lang_desc}",
              "description": "Engaging {lang_desc} caption summarizing the clip... \\n\\n#fyp #viral #foryou #podcast",
              "start_seconds": 45,
              "end_seconds": 95
            }}
          ]
        }}
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )

        return json.loads(response.text)

    except Exception as e:
        print("\n" + "="*80)
        print("ERROR: Gagal menganalisis transkrip dengan Gemini API!")
        print(f"Detail Kesalahan: {e}")
        print("="*80)
        
        # Check for Quota Exceeded or Invalid API Key
        err_str = str(e).upper()
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "QUOTA" in err_str:
            print("\n>>> PENTING: Kuota/Limit API Key Gemini Anda telah HABIS (429 Resource Exhausted) oleh Google.")
            print(">>> Silakan buat API Key baru yang segar di: https://aistudio.google.com/apikey")
            print(">>> Setelah itu, update nilai GEMINI_API_KEY di file .env Anda.")
        elif "400" in err_str or "API_KEY_INVALID" in err_str or "INVALID_ARGUMENT" in err_str:
            print("\n>>> PENTING: API Key Gemini Anda TIDAK VALID atau SALAH.")
            print(">>> Silakan periksa kembali dan pastikan GEMINI_API_KEY di file .env sudah sesuai.")
        else:
            print("\n>>> Silakan periksa koneksi internet Anda atau coba lagi beberapa saat lagi.")
        print("="*80 + "\n")
        raise

def analyze_transcript_locally(transcript_text, ollama_model, clip_count=3, duration_min=30, duration_max=90, is_podcast=False, language="id"):
    """Send transcript to local Ollama API for highlight clipping (start and end seconds).

    Special behaviour for Qwen models on long transcripts (> 30,000 chars):
      - Transcript is split into ~18-minute time-window chunks.
      - Each chunk is sent separately asking for 1 best clip.
      - Results are merged and the top clip_count clips are returned.
      - Llama3 and all other models use the original single-pass path, unchanged.
    """
    print(f"Sending transcript to local Ollama LLM ({ollama_model}) for highlight clipping...")

    import requests
    ollama_url = "http://localhost:11434/api/chat"

    lang_desc = "natural English" if language == "en" else "natural Indonesian"

    if "qwen" in ollama_model.lower():
        schema_desc = f"""{{
      "project_title": "Video Highlights",
      "clips": [
        {{
          "title": "Viral Catchy Title in {lang_desc}",
          "description": "Engaging {lang_desc} caption summarizing the clip... \\n\\n#fyp",
          "start_seconds": 45,
          "end_seconds": 95
        }}
      ]
    }}"""
        podcast_instruction = ""
    else:
        schema_desc = f"""{{
          "project_title": "Catchy Overall Video Project Title in {lang_desc} summarizing the video context",
          "clips": [
            {{
              "title": "Viral Catchy Title in {lang_desc}",
              "description": "Engaging {lang_desc} caption summarizing the clip... \\n\\n#fyp #viral #foryou #podcast",
              "start_seconds": 45,
              "end_seconds": 95
            }}
          ]
        }}"""

        if is_podcast:
            schema_desc = f"""{{
          "project_title": "Catchy Overall Video Project Title in {lang_desc} summarizing the video context",
          "clips": [
            {{
              "title": "Viral Catchy Title in {lang_desc}",
              "description": "Engaging {lang_desc} caption... \\n\\n#fyp #podcast",
              "start_seconds": 45,
              "end_seconds": 95,
              "speaker_timeline": [
                {{"start": 45, "end": 60, "speaker": 1}},
                {{"start": 60, "end": 75, "speaker": 2}},
                {{"start": 75, "end": 95, "speaker": 1}}
              ]
            }}
          ]
        }}"""

        podcast_instruction = ""
        if is_podcast:
            podcast_instruction = """
        4. DETECT SPEAKERS: Analyze the dialogue flow and assign speaker turns. In your 'speaker_timeline' array, break down the clip into sub-segments where 'speaker': 1 is the main speaker/host, and 'speaker': 2 is the guest/responder. Keep timelines sequential covering the entire range from 'start_seconds' to 'end_seconds'.
        """

    # Helper to parse start time from transcript line
    def parse_start_time(line):
        match = re.search(r'\[([\d\.]+)s\s*-\s*([\d\.]+)s\]', line)
        if match:
            return float(match.group(1))
        return None

    # Parse all lines and find total duration
    lines = [l.strip() for l in transcript_text.strip().split('\n') if l.strip()]
    first_time = 0.0
    last_time = 0.0
    for line in lines:
        t_start = parse_start_time(line)
        if t_start is not None:
            if first_time == 0.0:
                first_time = t_start
            last_time = t_start

    # If we couldn't parse any timestamps, fallback to single-pass
    if last_time == 0.0:
        last_time = 300.0 # fallback

    total_duration = last_time
    print(f"[Local LLM] Video total duration parsed from transcript: {total_duration:.1f}s")

    # Overlapping window strategy for local provider with multiple clips
    if clip_count > 1 and total_duration >= (clip_count * duration_min) and "qwen" not in ollama_model.lower():
        print(f"[Local LLM] Activating robust multi-clip overlapping window strategy for {clip_count} clips...")
        
        all_clips = []
        project_title = "Video Highlights"
        
        # Calculate windows with generous overlapping span
        span = max(duration_max * 1.5, total_duration * 1.5 / clip_count)
        if "qwen" in ollama_model.lower():
            span = min(400.0, span)
        
        for i in range(clip_count):
            center = total_duration * (i + 0.5) / clip_count
            win_start = max(0.0, center - span / 2)
            win_end = min(total_duration, center + span / 2)
            
            # Extract transcript lines for this window
            win_lines = []
            for line in lines:
                t_start = parse_start_time(line)
                if t_start is not None and win_start <= t_start <= win_end:
                    win_lines.append(line)
                    
            if not win_lines:
                # If window is empty, fallback to entire transcript lines in range
                win_lines = lines
                
            win_text = "\n".join(win_lines)
            print(f"[Local LLM] Window {i+1}/{clip_count}: {win_start:.1f}s - {win_end:.1f}s ({len(win_lines)} lines)...")
            
            chunk_prompt = f"""
            You are an expert video clipper assistant. Analyze the following transcript segment (which has timestamps '[start - end]' for each line) and identify exactly 1 highly engaging highlight clip.
            The clip MUST be between {duration_min} to {duration_max} seconds long — the single BEST peak moment in this segment.
            
            CRITICAL RULES:
            1. DO NOT include intros, silent parts, or non-speech segments.
            2. 'start_seconds' MUST align with the beginning of a complete sentence — never mid-sentence.
            3. 'end_seconds' MUST align with the end of a complete sentence or when the speaker finishes naturally.
            4. NEVER cut off mid-sentence. Adjust slightly if needed.
            5. Focus on emotionally impactful, thought-provoking, surprising, or highly informative moments.{podcast_instruction}
            
            Transcript Segment ({win_start:.1f}s - {win_end:.1f}s):
                res = requests.post(ollama_url, json={
                    "model": ollama_model,
                    "messages": [{"role": "user", "content": chunk_prompt}],
                    "stream": False,
                    "format": "json",
                    "options": {"num_ctx": 4096, "num_predict": 2048, "temperature": 0.1}
                }, timeout=180)
                res.raise_for_status()
                
                raw = res.json()['message']['content'].strip()
                parsed = clean_and_parse_json(raw)
                
                if parsed.get('project_title') and project_title == "Video Highlights":
                    project_title = parsed['project_title']
                    
                clips_found = parsed.get('clips', [])
                if clips_found:
                    # Keep only the first clip returned for this window
                    c = clips_found[0]
                    all_clips.append(c)
                    print(f"  [Success] Window {i+1} found clip: '{c.get('title')}' from {c.get('start_seconds')}s to {c.get('end_seconds')}s.")
                else:
                    print(f"  [Warning] Window {i+1} returned empty clips array.")
            except Exception as err:
                print(f"  [Error] Window {i+1} query failed: {err}")
                continue
                
        # If we found at least one clip, return it!
        if all_clips:
            # Ensure we have up to clip_count clips
            return {"project_title": project_title, "clips": all_clips[:clip_count]}
            
        print("[Local LLM] Overlapping window strategy failed to extract clips, falling back to single-pass...")

    # ===========================================================================
    # QWEN AUTO-CHUNKING — Only for "qwen" models on long transcripts (>30k chars)
    # Llama3 and ALL other models skip this block entirely.
    # ===========================================================================
    # Activating chunking for local LLMs on long transcripts to prevent context truncation and severe CPU slowdown
    if "qwen" in ollama_model.lower() or len(transcript_text) > 25000:
        print(f"[Local LLM] Long transcript ({len(transcript_text)} chars) or Qwen model active. "
              "Activating focused window chunking to prevent context truncation and ensure rapid inference...")

        if "qwen" in ollama_model.lower():
            CHUNK_WINDOW_SEC = min(180, max(120, duration_max))
        else:
            CHUNK_WINDOW_SEC = max(300, int(duration_max * 1.5))

        def _ts(line):
            """Parse leading timestamp [X.Xs - Y.Ys] -> float seconds, or None."""
            try:
                return float(line.split("[")[1].split("s")[0].strip())
            except Exception:
                return None

        # Build chunks by time window
        chunks, buf, win_start = [], [], None
        for line in transcript_text.strip().split("\n"):
            t = _ts(line)
            if t is None:
                if buf:
                    buf.append(line)
                continue
            if win_start is None:
                win_start = t
            buf.append(line)
            if t - win_start >= CHUNK_WINDOW_SEC:
                chunks.append(("\n".join(buf), win_start, t))
                buf, win_start = [], None
        if buf:
            last_t = _ts(buf[-1]) or (win_start or 0)
            chunks.append(("\n".join(buf), win_start or 0, last_t))

        print(f"[Local LLM] {len(chunks)} chunk(s) created. Querying 1 clip per chunk...")

        all_clips, project_title = [], "Video Highlights"

        for i, (chunk_text, c_start, c_end) in enumerate(chunks):
            print(f"[Local LLM Chunk {i+1}/{len(chunks)}] {c_start:.0f}s - {c_end:.0f}s ...")
            if "qwen" in ollama_model.lower():
                # ---------------------------------------------------------------
                # Qwen line-number-picker strategy.
                # Qwen always copies numeric examples from prompts verbatim,
                # so we NEVER show it any seconds. We give a numbered list of
                # sentences (timestamps stripped) and ask Qwen to output only
                # start/end LINE NUMBERS. We then map those back to real
                # timestamps ourselves — Qwen never sees the actual seconds.
                # ---------------------------------------------------------------
                _ts_rx2 = re.compile(r'\[([\d\.]+)s\s*-\s*([\d\.]+)s\]')
                numbered_lines = []   # list of (line_num, start_sec, end_sec, text)
                for ln in chunk_text.strip().split("\n"):
                    m2 = _ts_rx2.search(ln)
                    if m2:
                        text_part = ln[m2.end():].strip()
                        numbered_lines.append((len(numbered_lines) + 1,
                                               float(m2.group(1)),
                                               float(m2.group(2)),
                                               text_part))

                if len(numbered_lines) < 3:
                    print(f"  [Qwen Chunk {i+1}] Too few lines ({len(numbered_lines)}), skipping.")
                    continue

                nl_text = "\n".join(f"{n}. {txt}" for n, _, _, txt in numbered_lines)
                n_lines = len(numbered_lines)
                chunk_dur = max(c_end - c_start, 1)
                target_sec = (duration_min + duration_max) / 2
                lines_per_sec = n_lines / chunk_dur
                target_lines = max(3, min(n_lines - 1, int(target_sec * lines_per_sec)))

                chunk_prompt = f"""Baca daftar kalimat video berikut:

{nl_text}

Dari daftar di atas (total {n_lines} kalimat), pilih 1 bagian yang paling menarik dan emosional.
Bagian yang dipilih harus mencakup sekitar {target_lines} kalimat berurutan.

Balas HANYA dengan JSON objek. Field:
- title: string
- description: string
- start_line: integer (nomor baris mulai)
- end_line: integer (nomor baris selesai)

Pastikan format JSON valid."""

                try:
                    payload = {
                        "model": ollama_model,
                        "messages": [{"role": "user", "content": chunk_prompt}],
                        "stream": False,
                        "options": {"num_ctx": 4096, "num_predict": 256, "temperature": 0.3}
                    }
                    res = requests.post(ollama_url, json=payload, timeout=600)
                    res.raise_for_status()
                    raw = res.json()['message']['content'].strip()
                    print(f"  [Qwen Chunk {i+1}] Raw: {raw[:200]}")

                    parsed = clean_and_parse_json(raw)
                    sl = int(parsed.get("start_line", 1))
                    el = int(parsed.get("end_line", target_lines))

                    # Clamp to valid range
                    sl = max(1, min(sl, n_lines))
                    el = max(sl + 1, min(el, n_lines))

                    # Map line numbers -> real timestamps
                    real_start = numbered_lines[sl - 1][1]
                    real_end   = numbered_lines[el - 1][2]
                    dur = real_end - real_start

                    # Extend if too short
                    if dur < duration_min:
                        for ext in range(el, n_lines + 1):
                            real_end = numbered_lines[ext - 1][2]
                            if real_end - real_start >= duration_min:
                                break
                    # Shrink if too long
                    elif dur > duration_max * 1.5:
                        for shr in range(el, sl, -1):
                            real_end = numbered_lines[shr - 1][2]
                            if real_end - real_start <= duration_max * 1.2:
                                break

                    dur = real_end - real_start
                    title = parsed.get("title", "Highlight")
                    desc  = parsed.get("description", "")
                    print(f"  [Qwen Chunk {i+1}] Lines {sl}-{el} -> {real_start:.1f}s-{real_end:.1f}s ({dur:.1f}s): {title}")

                    if duration_min * 0.7 <= dur <= duration_max * 1.5:
                        all_clips.append({
                            "title": title,
                            "description": desc,
                            "start_seconds": real_start,
                            "end_seconds": real_end
                        })
                    else:
                        print(f"  [Qwen Chunk {i+1}] Duration {dur:.1f}s out of range, skipped.")
                except Exception as err:
                    print(f"  [Qwen Chunk {i+1}] Skipped: {err}")
                continue  # skip the else block below

            # Non-Qwen models
            else:
                chunk_prompt = f"""
    You are an expert video clipper assistant. Analyze this transcript segment and identify exactly 1 highly engaging, viral, or interesting highlight clip.
    The clip MUST be between {duration_min} to {duration_max} seconds long — the single BEST peak moment in this segment.

    CRITICAL RULES:
    1. DO NOT include intros, silent parts, or non-speech segments.
    2. 'start_seconds' MUST align with the beginning of a complete sentence — never mid-sentence.
    3. 'end_seconds' MUST align with the end of a complete sentence or when the speaker finishes naturally.
    4. NEVER cut off mid-sentence. Adjust slightly if needed.
    5. Focus on emotionally impactful, thought-provoking, surprising, or highly informative moments.{podcast_instruction}

    Transcript Segment ({c_start:.0f}s - {c_end:.0f}s):
    {chunk_text}

    Output ONLY a JSON object — no markdown, no backticks. Schema:
    {schema_desc}
    """
            try:
                payload = {
                    "model": ollama_model,
                    "messages": [{"role": "user", "content": chunk_prompt}],
                    "stream": False,
                    "format": "json",
                    "options": {"num_ctx": 4096, "num_predict": 2048, "temperature": 0.1}
                }
                res = requests.post(ollama_url, json=payload, timeout=600)
                res.raise_for_status()
                raw = res.json()['message']['content'].strip()
                print(f"[Local LLM Chunk {i+1}] Preview: {raw[:180]}...")
                parsed = clean_and_parse_json(raw)
                if parsed.get('project_title') and project_title == "Video Highlights":
                    project_title = parsed['project_title']
                clips_found = parsed.get('clips', [])
                all_clips.extend(clips_found)
            except Exception as err:
                print(f"[Local LLM Chunk {i+1}] Skipped: {err}")
                continue

        def _score(c):
            try:
                d = float(c.get('end_seconds', 0)) - float(c.get('start_seconds', 0))
                return -abs(d - (duration_min + duration_max) / 2)
            except Exception:
                return -9999

        all_clips.sort(key=_score, reverse=True)
        selected = all_clips[:clip_count]
        print(f"[Local LLM] Done — {len(all_clips)} candidates, returning top {len(selected)}.")
        return {"project_title": project_title, "clips": selected}

    # ===========================================================================
    # ORIGINAL SINGLE-PASS PATH — Llama3, all other models, or short Qwen transcripts
    # This block is 100% unchanged from the original implementation.
    # ===========================================================================
    prompt = f"""
    You are an expert video clipper assistant. Your objective is to analyze the following transcript dialogue which contains speech timestamps in the format '[start_seconds - end_seconds]' next to each spoken line.
    Using these timestamps, identify exactly {clip_count} highly engaging, viral, or interesting highlight segments/clips.
    
    CRITICAL DURATION RULES:
    - EACH selected segment/clip MUST be between {duration_min} to {duration_max} seconds long!
    - DO NOT choose any clip shorter than {duration_min} seconds! (For example, if you are asked for {duration_min} seconds, the difference 'end_seconds - start_seconds' MUST be at least {duration_min} seconds).
    - If a specific engaging topic is short, you MUST continue and merge consecutive adjacent sentences until the segment reaches at least {duration_min} seconds.

    CRITICAL RULES:
    1. DO NOT include video intros, B-roll, silent parts, or non-speech segments at the beginning or end of your selected timestamps.
    2. The 'start_seconds' MUST point exactly to the timestamp of the first word where the speaker actually starts talking in the clip.
    3. Focus on continuous, high-energy, information-dense dialogue. Skip segments with long pauses or background music without dialogue.
    4. CRITICAL TIMESTAMP RULES (PREVENT ABRUPT CUTS):
       - The 'start_seconds' MUST align exactly with the beginning of a complete, natural sentence. Do not start a clip mid-sentence or mid-phrase!
       - The 'end_seconds' MUST align exactly with the end of a complete sentence or when a speaker naturally finishes talking.
       - NEVER cut the video off in the middle of a sentence, word, or clause! 
       - If the target duration is e.g. 90 seconds, and at 90s the speaker is in the middle of a sentence, you MUST adjust 'end_seconds' (either cut it slightly earlier e.g. at 82s or extend slightly e.g. at 96s) so that the clip finishes exactly when a sentence or thought naturally ends.
       - The final video MUST feel complete and resolve cleanly, rather than cutting off abruptly.{podcast_instruction}

    Transcript Dialogue:
    {transcript_text}

    You MUST output your response strictly as a JSON object, with no markdown code blocks, backticks, or extra text. Use the following JSON schema:
    {schema_desc}
    """

    payload = {
        "model": ollama_model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "num_ctx": 4096,
            "num_predict": 2048,
            "temperature": 0.1
        }
    }
    if "qwen" not in ollama_model.lower():
        payload["format"] = "json"

    try:
        response = requests.post(ollama_url, json=payload, timeout=300)
        response.raise_for_status()
        ollama_response = response.json()
        raw_content = ollama_response['message']['content']

        print("DEBUG_RAW_OLLAMA_RESPONSE_START")
        print(raw_content)
        print("DEBUG_RAW_OLLAMA_RESPONSE_END")

        try:
            return clean_and_parse_json(raw_content)
        except Exception as json_err:
            print(f"JSON_PARSE_ERROR_ON_CONTENT: {raw_content}")
            raise Exception(f"Failed to parse JSON from local LLM: {str(json_err)}")
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

def slice_video(video_path, start_sec, end_sec, output_path, ffmpeg_path, watermark="", orientation="16:9", is_podcast=False, speaker_timeline=None, engine_mode="standard", transcript_path=None, title="", intro_hook="", burn_subtitles=True):
    """Slice a video into a smaller clip using FFmpeg, optionally cropping to 9:16 vertical."""
    print(f"Slicing clip from {start_sec}s to {end_sec}s with {orientation} orientation (Podcast: {is_podcast}, Engine: {engine_mode}, Burn Subtitles: {burn_subtitles})...")
    
    if os.path.exists(output_path):
        os.remove(output_path)

    if engine_mode in ["opsi_a", "opsi_b"]:
        # Execute the computer vision reframe and subtitle generator!
        # Runs: python processor.py <video_path> <output_path> <start_sec> <end_sec> <transcript_path> <watermark> <title> <intro_hook> <split_screen> <engine_mode> <speaker_timeline_json>
        import sys
        
        split_screen = "1" if is_podcast else "0"
        speaker_timeline_json = ""
        if speaker_timeline:
            speaker_timeline_json = json.dumps(speaker_timeline)
            
        processor_script = os.path.join(os.path.dirname(__file__), "processor.py")
        
        # If subtitles are disabled, we do not pass the transcript file so it skips burning subtitles!
        transcript_arg = transcript_path if burn_subtitles else ""
        
        cmd = [
            sys.executable,
            processor_script,
            video_path,
            output_path,
            str(start_sec),
            str(end_sec),
            transcript_arg or "",
            watermark or "",
            title or "",
            intro_hook or "",
            split_screen,
            engine_mode,
            speaker_timeline_json
        ]
        
        print(f"Running Computer Vision Reframer (Engine Mode: {engine_mode}): {' '.join(cmd)}")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Warning: CV Reframer failed.\nStdout: {res.stdout}\nStderr: {res.stderr}")
            print("Falling back to FFmpeg-based static slice...")
        else:
            print("CV Reframer completed successfully!")
            return output_path

    # Podcast dynamic speaker switching logic
    if is_podcast and (speaker_timeline or []):
        try:
            print(f"Running experimental podcast speaker timeline slices for: {speaker_timeline}")
            temp_files = []
            out_dir = os.path.dirname(output_path)
            
            # Crop specs
            # Speaker 1: Left side. Speaker 2: Right side.
            crop_spec_1 = "crop=ih*9/16:ih:iw*0.15:0" if orientation == "9:16" else "crop=iw/2:ih:0:0"
            crop_spec_2 = "crop=ih*9/16:ih:iw*0.50:0" if orientation == "9:16" else "crop=iw/2:ih:iw/2:0"
            
            for idx, seg in enumerate(speaker_timeline):
                seg_start = max(start_sec, float(seg.get('start', start_sec)))
                seg_end = min(end_sec, float(seg.get('end', end_sec)))
                
                if seg_start >= seg_end:
                    continue
                    
                speaker = int(seg.get('speaker', 1))
                crop_filter = crop_spec_1 if speaker == 1 else crop_spec_2
                
                # Apply watermark if defined
                filters = [crop_filter]
                if orientation == "9:16":
                    filters.append("scale=720:1280:flags=lanczos")
                    filters.append("unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=1.0")
                elif orientation == "16:9":
                    filters.append("scale=1280:720:flags=lanczos")
                    filters.append("unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=1.0")
                wm_filter = _build_watermark_filter(watermark)
                if wm_filter:
                    filters.append(wm_filter)
                
                temp_filename = f"temp_seg_{idx}_{int(seg_start)}_{int(seg_end)}.mp4"
                temp_path = os.path.join(out_dir, temp_filename)
                
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
                # Slice and crop this speaker turn
                cmd = [
                    ffmpeg_path, "-y",
                    "-ss", str(seg_start),
                    "-to", str(seg_end),
                    "-i", video_path,
                    "-vf", ",".join(filters),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-strict", "experimental",
                    temp_path
                ]
                
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                temp_files.append(temp_path)
                
            if temp_files:
                # Create a concat list file
                list_file_path = os.path.join(out_dir, "concat_list.txt")
                with open(list_file_path, "w", encoding="utf-8") as f:
                    for temp_file in temp_files:
                        # FFmpeg needs forward slashes or escaped paths in the concat list
                        normalized_path = os.path.abspath(temp_file).replace('\\', '/')
                        f.write(f"file '{normalized_path}'\n")
                
                # Concatenate all speaker turns into the final clip file
                concat_cmd = [
                    ffmpeg_path, "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", list_file_path,
                    "-c", "copy",
                    "-movflags", "+faststart",
                    output_path
                ]
                subprocess.run(concat_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Cleanup temp segment files
                try:
                    os.remove(list_file_path)
                    for tf in temp_files:
                        os.remove(tf)
                except Exception as clean_err:
                    print(f"Warning cleaning temp segments: {clean_err}")
                    
                return output_path
                
        except Exception as e:
            print(f"Warning: Podcast switching failed ({e}). Falling back to static center crop.")
            # Fall through to default static crop below

    # Default static slicing code
    cmd = [
        ffmpeg_path,
        "-y",
        "-ss", str(start_sec),
        "-to", str(end_sec),
        "-i", video_path
    ]
    
    filters = []
    
    # 9:16 Mobile Portrait Center-Crop Filter
    if orientation == "9:16":
        filters.append("crop=ih*9/16:ih:(iw-ih*9/16)/2:0")
        filters.append("scale=720:1280:flags=lanczos")
        filters.append("unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=1.0")
    elif orientation == "16:9":
        filters.append("scale=1280:720:flags=lanczos")
        filters.append("unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=1.0")
        
    wm_filter = _build_watermark_filter(watermark)
    if wm_filter:
        filters.append(wm_filter)
        
    # Add smooth 1-second Fade In and Fade Out transitions
    duration = end_sec - start_sec
    filters.append("fade=t=in:st=0:d=1")
    filters.append(f"fade=t=out:st={duration - 1}:d=1")
    
    # Process audio fades
    audio_filters = [
        "afade=t=in:st=0:d=1",
        f"afade=t=out:st={duration - 1}:d=1"
    ]
        
    if filters:
        vf_filter = ",".join(filters)
        cmd.extend(["-vf", vf_filter])
        
    if audio_filters:
        af_filter = ",".join(audio_filters)
        cmd.extend(["-af", af_filter])
        
    cmd.extend([
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        "-movflags", "+faststart",
        output_path
    ])
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def main():
    parser = argparse.ArgumentParser(description="AI Video Clipper Engine (Hybrid Cloud & Local)")
    parser.add_argument("--source", required=True, help="Video file path or YouTube URL")
    parser.add_argument("--type", choices=["upload", "youtube", "local_path"], required=True, help="Type of source")
    parser.add_argument("--output-dir", required=True, help="Directory to save the results")
    parser.add_argument("--provider", choices=["gemini", "local"], default="gemini", help="AI Provider: gemini or local")
    parser.add_argument("--api-key", default="", help="Gemini API Key (required for gemini provider)")
    parser.add_argument("--ollama-model", default="llama3", help="Ollama LLM Model name (required for local provider)")
    parser.add_argument("--whisper-model", default="base", help="Local Whisper model: tiny, base, small, medium")
    parser.add_argument("--ffmpeg-path", default="ffmpeg", help="Path to FFmpeg executable")
    parser.add_argument("--ytdlp-path", default="yt-dlp", help="Path to yt-dlp executable")
    parser.add_argument("--whisper-device", default="cpu", help="Device to run Whisper (cpu or cuda)")
    parser.add_argument("--clip-count", type=int, default=3, help="Number of clips to generate")
    parser.add_argument("--clip-duration-min", type=int, default=30, help="Minimum duration of each clip in seconds")
    parser.add_argument("--clip-duration-max", type=int, default=90, help="Maximum duration of each clip in seconds")
    parser.add_argument("--watermark", default="", help="Text watermark to apply to clips")
    parser.add_argument("--orientation", default="16:9", choices=["16:9", "9:16"], help="Output video aspect ratio")
    parser.add_argument("--engine-mode", default="standard", choices=["standard", "opsi_a", "opsi_b"], help="Layout / CV Engine Mode: standard, opsi_a, or opsi_b")
    parser.add_argument("--disable-burn-subtitles", action="store_true", help="Disable burning/hardcoding subtitles into video frames")
    parser.add_argument("--is-podcast", action="store_true", help="Flag if the video is a podcast")
    parser.add_argument("--language", choices=["id", "en", "dual"], default="id", help="Subtitle/caption target language")
    
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
    original_title = "Video Project"
    youtube_channel = None
    
    try:
        # Step 1: Download YouTube if applicable
        if args.type == "youtube":
            # Extract YouTube title and channel name using yt-dlp
            try:
                print("Querying YouTube metadata for video title and channel name...")
                
                # Try multiple strategies for metadata extraction
                meta_strategies = [
                    ("cookies-from-browser", ["--cookies-from-browser", "chrome"]),
                ]
                cookies_path = get_active_cookies_path()
                if cookies_path:
                    meta_strategies.append(("cookies-file", ["--cookies", cookies_path]))
                meta_strategies.append(("plain", []))
                
                metadata_ok = False
                for strat_name, strat_args in meta_strategies:
                    try:
                        print_cmd = [
                            args.ytdlp_path,
                            "--print", "%(title)s",
                            "--print", "%(uploader)s",
                            "--js-runtimes", "node",
                        ] + strat_args + [args.source]
                        
                        res = subprocess.run(print_cmd, capture_output=True, text=True, check=True)
                        lines = [line.strip() for line in res.stdout.strip().split('\n') if line.strip()]
                        if len(lines) >= 2:
                            original_title = lines[0]
                            youtube_channel = lines[1]
                        elif len(lines) == 1:
                            original_title = lines[0]
                        metadata_ok = True
                        break
                    except Exception as e:
                        err_str = str(e)
                        if "DPAPI" in err_str:
                            continue  # Skip to next strategy
                        if "not a bot" in err_str.lower():
                            continue  # Skip to next strategy
                        continue
                
                if not metadata_ok:
                    print("Warning: Could not extract metadata via any strategy, using fallback title.")
                    original_title = "YouTube Video"
                    
                print(f"Extracted YouTube title: {original_title}")
                print(f"Extracted YouTube channel: {youtube_channel}")
            except Exception as e:
                print(f"Warning: Failed to extract YouTube title: {e}")
                original_title = "YouTube Video"

            video_path = download_youtube(args.source, args.output_dir, args.ytdlp_path, args.ffmpeg_path)
        else:
            video_path = args.source
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Uploaded source video not found at: {video_path}")
            
            # Extract clean upload title
            raw_title = os.path.splitext(os.path.basename(video_path))[0]
            clean_title = re.sub(r'^\d+_[a-f0-9]+_', '', raw_title)
            clean_title = re.sub(r'^\d+_[a-zA-Z0-9]+_', '', clean_title)
            clean_title = re.sub(r'^\d+_', '', clean_title)
            original_title = clean_title.replace('_', ' ').replace('-', ' ').title()
            print(f"Extracted uploaded file title: {original_title}")
                
        # Step 2: Extract audio
        audio_path = extract_audio(video_path, args.output_dir, args.ffmpeg_path)
        
        # Step 3: Run local Whisper transcription
        whisper_success = False
        transcript_segments = []
        full_transcript_text = ""
        detected_language = "id"
        
        transcript_cache_path = os.path.join(args.output_dir, "transcript_cache.json")
        
        if os.path.exists(transcript_cache_path):
            try:
                print("Loading transcript from cache...")
                with open(transcript_cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    transcript_segments = cache_data['segments']
                    full_transcript_text = cache_data['full_text']
                    detected_language = cache_data.get('language', 'id')
                whisper_success = True
            except Exception as e:
                print(f"Warning: Failed to load transcript from cache: {e}")
                
        if not whisper_success:
            try:
                transcript_segments, full_transcript_text, detected_language = transcribe_audio_locally(
                    audio_path,
                    args.whisper_model,
                    device=args.whisper_device,
                    target_language=args.language
                )
                whisper_success = True
                
                # Save cache
                with open(transcript_cache_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'segments': transcript_segments,
                        'full_text': full_transcript_text,
                        'language': detected_language
                    }, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Warning: Local Whisper transcription failed: {e}")
                print("Falling back to cloud-based Gemini audio analysis if provider is gemini...")

        # Step 4: Call AI to transcribe and detect highlights (Gemini or Local Offline)
        if whisper_success:
            # We have local transcript, use it!
            if args.provider == "gemini":
                if not args.api_key:
                    raise ValueError("API Key Gemini diperlukan jika menggunakan provider 'gemini'. Tambahkan di file .env")
                ai_analysis = analyze_transcript_with_gemini(
                    full_transcript_text,
                    args.api_key,
                    clip_count=args.clip_count,
                    duration_min=args.clip_duration_min,
                    duration_max=args.clip_duration_max,
                    language=args.language
                )
            else:
                # Use high-resolution uncompacted transcript for shorter videos (< 350 segments, which is ~10-15 mins)
                # to give local offline LLMs maximum time resolution and correct duration selections.
                if len(transcript_segments) < 350:
                    formatted_transcript = "\n".join([f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text'].strip()}" for seg in transcript_segments])
                else:
                    # Group adjacent segments to heavily optimize context size for larger files
                    # Adjust group size dynamically based on requested duration to avoid tiny isolated paragraphs
                    dyn_group_size = max(8, int(args.clip_duration_min / 5))
                    formatted_transcript = get_compact_transcript(transcript_segments, group_size=dyn_group_size)
                    
                ai_analysis = analyze_transcript_locally(
                    formatted_transcript,
                    args.ollama_model,
                    clip_count=args.clip_count,
                    duration_min=args.clip_duration_min,
                    duration_max=args.clip_duration_max,
                    is_podcast=args.is_podcast,
                    language=args.language
                )
        else:
            # Fallback: if local Whisper failed, upload file to Gemini if using gemini
            if args.provider == "gemini":
                if not args.api_key:
                    raise ValueError("API Key Gemini diperlukan jika menggunakan provider 'gemini'. Tambahkan di file .env")
                ai_analysis = analyze_audio_with_gemini(
                    audio_path,
                    args.api_key,
                    clip_count=args.clip_count,
                    duration_min=args.clip_duration_min,
                    duration_max=args.clip_duration_max,
                    language=args.language
                )
            else:
                raise Exception("Local transcription failed and provider is local. Cannot continue.")
        
        print("DEBUG_AI_ANALYSIS_START")
        print(json.dumps(ai_analysis))
        print("DEBUG_AI_ANALYSIS_END")
        
        clips_data = []
        
        # Cleanup any stale clip files from previous runs to avoid confusion/leftovers
        for f_name in os.listdir(args.output_dir):
            if (f_name.startswith("clip_") and 
                (f_name.endswith(".mp4") or f_name.endswith(".jpg") or 
                 f_name.endswith(".srt") or f_name.endswith(".vtt") or 
                 f_name.endswith("_subs_render.json"))):
                try:
                    os.remove(os.path.join(args.output_dir, f_name))
                except Exception as clean_err:
                    print(f"Warning: Failed to delete stale file {f_name}: {clean_err}")
        
        # Step 5: Cut the clips and write subtitles
        for i, clip in enumerate(ai_analysis.get('clips', [])):
            clip_title = clip.get('title', f"Clip {i+1}")
            clip_desc = clip.get('description', '')
            
            try:
                start_sec = float(clip.get('start_seconds', 0))
            except (ValueError, TypeError):
                start_sec = 0.0
                
            try:
                end_sec = float(clip.get('end_seconds', start_sec + 30))
            except (ValueError, TypeError):
                end_sec = start_sec + 30.0

            # Auto-correction for short clips to meet requested duration_min
            duration = end_sec - start_sec
            req_min = float(args.clip_duration_min)
            req_max = float(args.clip_duration_max)
            
            if duration < req_min:
                print(f"[Auto-Correction] Clip '{clip_title}' duration is {duration:.1f}s, which is below the minimum requested {req_min}s.")
                # Extend end_sec so that end_sec - start_sec >= req_min
                target_end = start_sec + req_min
                
                # Find the closest transcript segment end time that is >= target_end
                best_end = target_end
                if whisper_success and transcript_segments:
                    # Filter segments that end after start_sec
                    valid_segs = [s for s in transcript_segments if s['end'] > start_sec]
                    if valid_segs:
                        # Find the segment whose end is closest to target_end
                        # Prefer segments that end >= target_end, but fallback to closest
                        segs_after_target = [s for s in valid_segs if s['end'] >= target_end]
                        if segs_after_target:
                            best_end = segs_after_target[0]['end']
                        else:
                            best_end = valid_segs[-1]['end']
                
                # Ensure we don't exceed the source video duration or clip_duration_max
                if best_end - start_sec > req_max:
                    best_end = start_sec + req_max
                    
                end_sec = best_end
                print(f"[Auto-Correction] Clip extended to {end_sec - start_sec:.1f}s (new end_sec: {end_sec:.1f}s) to align with natural sentence boundaries.")
            # Extract subtitles
            if whisper_success:
                # Find all transcript segments that overlap with this clip
                clip_segments = []
                for seg in transcript_segments:
                    if 'words' in seg and seg['words'] is not None:
                        current_words = []
                        for w in seg['words']:
                            if w['start'] >= start_sec and w['end'] <= end_sec:
                                current_words.append(w)
                                if len(current_words) >= 3 or (w['end'] - current_words[0]['start']) >= 1.5:
                                    chunk_text = " ".join([x['word'].strip() for x in current_words])
                                    clip_segments.append({
                                        'start': current_words[0]['start'],
                                        'end': w['end'],
                                        'text': chunk_text,
                                        'words': list(current_words)
                                    })
                                    current_words = []
                        if current_words:
                            chunk_text = " ".join([x['word'].strip() for x in current_words])
                            clip_segments.append({
                                'start': current_words[0]['start'],
                                'end': current_words[-1]['end'],
                                'text': chunk_text,
                                'words': list(current_words)
                            })
                    else:
                        if seg['start'] >= start_sec and seg['end'] <= end_sec:
                            clip_segments.append(seg)
                        elif seg['start'] < start_sec and seg['end'] > start_sec:
                            clip_segments.append({
                                'start': start_sec,
                                'end': seg['end'],
                                'text': seg['text']
                            })
                        elif seg['start'] < end_sec and seg['end'] > end_sec:
                            clip_segments.append({
                                'start': seg['start'],
                                'end': end_sec,
                                'text': seg['text']
                            })
                
                # Determine translation direction
                target_lang = args.language
                if detected_language == "en" and target_lang in ["id", "dual"]:
                    clip_subtitles = translate_subtitles(
                        clip_segments, 
                        args.provider, 
                        api_key=args.api_key, 
                        ollama_model=args.ollama_model,
                        from_lang="en",
                        to_lang="id"
                    )
                elif detected_language == "id" and target_lang in ["en", "dual"]:
                    clip_subtitles = translate_subtitles(
                        clip_segments, 
                        args.provider, 
                        api_key=args.api_key, 
                        ollama_model=args.ollama_model,
                        from_lang="id",
                        to_lang="en"
                    )
                else:
                    clip_subtitles = []
                    for seg in clip_segments:
                        words = seg.get('words', [])
                        if not words:
                            words_list = seg['text'].split()
                            dur = seg['end'] - seg['start']
                            for j, w in enumerate(words_list):
                                words.append({
                                    'word': w,
                                    'start': seg['start'] + (j * dur / len(words_list)),
                                    'end': seg['start'] + ((j + 1) * dur / len(words_list))
                                })
                        clip_subtitles.append({
                            'start': seg['start'],
                            'end': seg['end'],
                            'text_en': seg['text'],
                            'text_id': seg['text'],
                            'words_en': words,
                            'words_id': words
                        })
            else:
                # Use subtitles returned directly by Gemini in fallback mode
                raw_subs = clip.get('subtitles', [])
                clip_subtitles = []
                for sub in raw_subs:
                    t_en = sub.get('text_en', '')
                    t_id = sub.get('text_id', '')
                    start = float(sub.get('start', start_sec))
                    end = float(sub.get('end', start + 3))
                    dur = end - start
                    
                    # Synthesize words_en
                    words_en = []
                    en_list = t_en.split()
                    for j, w in enumerate(en_list):
                        words_en.append({
                            'word': w,
                            'start': start + (j * dur / max(1, len(en_list))),
                            'end': start + ((j + 1) * dur / max(1, len(en_list)))
                        })
                        
                    # Synthesize words_id
                    words_id = []
                    id_list = t_id.split()
                    for j, w in enumerate(id_list):
                        words_id.append({
                            'word': w,
                            'start': start + (j * dur / max(1, len(id_list))),
                            'end': start + ((j + 1) * dur / max(1, len(id_list)))
                        })
                        
                    clip_subtitles.append({
                        'start': start,
                        'end': end,
                        'text_en': t_en,
                        'text_id': t_id,
                        'words_en': words_en,
                        'words_id': words_id
                    })
                
            clip_filename = f"clip_{i+1}.mp4"
            clip_output_path = os.path.join(args.output_dir, clip_filename)
            
            # Save tailored clip subtitle JSON file
            clip_subs_render_path = os.path.join(args.output_dir, f"clip_{i+1}_subs_render.json")
            render_sub_data = {
                "subtitle_mode": args.language,
                "detected_language": detected_language,
                "segments": clip_subtitles
            }
            with open(clip_subs_render_path, "w", encoding="utf-8") as rf:
                json.dump(render_sub_data, rf, indent=2, ensure_ascii=False)
            
            # Slice video with optional podcast speaker switching and premium auto-reframing
            speaker_timeline = clip.get('speaker_timeline', [])
            slice_video(
                video_path, 
                start_sec, 
                end_sec, 
                clip_output_path, 
                args.ffmpeg_path, 
                watermark=args.watermark, 
                orientation=args.orientation,
                is_podcast=args.is_podcast,
                speaker_timeline=speaker_timeline,
                engine_mode=args.engine_mode,
                transcript_path=clip_subs_render_path if not args.disable_burn_subtitles else None,
                title=clip_title,
                intro_hook=clip_desc,
                burn_subtitles=not args.disable_burn_subtitles
            )
            
            # Subtitle prefix
            sub_prefix = os.path.join(args.output_dir, f"clip_{i+1}_sub")
            
            # Generate SRT/VTT for this clip
            srt_content, vtt_content, dual_subs = generate_subtitles(
                clip_subtitles,
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
            'video_title': ai_analysis.get('project_title', original_title),
            'original_title': original_title,
            'youtube_channel': youtube_channel,
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

import json
import requests
import re

# Load transcript cache
with open('storage/app/public/clipper/44/transcript_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

transcript_segments = cache['segments']

def get_compact_transcript(segments, max_duration=300, group_size=8):
    compact_lines = []
    current_group = []
    
    for i, seg in enumerate(segments):
        if seg['start'] > max_duration:
            break
        current_group.append(seg)
        if len(current_group) >= group_size or i == len(segments) - 1:
            start_t = current_group[0]['start']
            end_t = current_group[-1]['end']
            merged_text = " ".join([s['text'].strip() for s in current_group])
            compact_lines.append(f"[{start_t:.1f}s - {end_t:.1f}s] {merged_text}")
            current_group = []
            
    return "\n".join(compact_lines)

transcript_text = get_compact_transcript(transcript_segments, max_duration=240)

print("Transcript text length:", len(transcript_text))
print("Transcript text sample:\n", transcript_text[:500])

clip_count = 1
duration_min = 30
duration_max = 90
is_podcast = True

schema_desc = """{
  "project_title": "Video Highlights",
  "clips": [
    {
      "title": "Viral Catchy Title in natural Indonesian",
      "description": "Engaging Indonesian caption summarizing the clip... \\n\\n#fyp",
      "start_seconds": 45,
      "end_seconds": 95
    }
  ]
}"""

prompt = f"""Tugas: Temukan 1 bagian (klip) video paling menarik dari transkrip di bawah ini dengan durasi antara {duration_min} sampai {duration_max} detik.

Transkrip:
{transcript_text}

Kamu HARUS mengembalikan output dalam format JSON seperti ini:
{{
  "project_title": "Judul Highlight Video",
  "clips": [
    {{
      "title": "Judul Klip Menarik",
      "description": "Deskripsi klip menarik #fyp",
      "start_seconds": 45,
      "end_seconds": 95
    }}
  ]
}}

Berikan output dalam bentuk JSON saja tanpa teks percakapan tambahan lainnya.
"""

payload = {
    "model": "qwen",
    "messages": [
        {"role": "system", "content": "You are a precise JSON extractor. You must output valid JSON matching the exact keys requested."},
        {"role": "user", "content": prompt}
    ],
    "stream": False,
    "format": "json",
    "options": {
        "num_ctx": 4096,
        "num_predict": 2048,
        "temperature": 0.1
    }
}

print("\nSending request to Ollama (qwen)...")
response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=300)
print("Status code:", response.status_code)
ollama_response = response.json()
raw_content = ollama_response['message']['content']
print("Raw Content Length:", len(raw_content))
print("Raw Content:\n", raw_content)

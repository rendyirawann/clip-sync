import json
import requests
import re
import os

# Load transcript cache
with open('storage/app/public/clipper/44/transcript_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

transcript_text = ""
segments = cache['segments']
group_size = 8
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
        
transcript_text = "\n".join(compact_lines)

print("Full Transcript text length (chars):", len(transcript_text))

ollama_url = "http://localhost:11434/api/chat"
ollama_model = "qwen"
duration_min = 90
duration_max = 140

def clean_and_parse_json(raw_str):
    raw_str = raw_str.strip()
    raw_str = re.sub(r'^```(?:json)?\s*', '', raw_str, flags=re.IGNORECASE)
    raw_str = re.sub(r'\s*```$', '', raw_str)
    raw_str = raw_str.strip()
    try:
        return json.loads(raw_str)
    except json.JSONDecodeError:
        pass
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
    return json.loads(raw_str)

CHUNK_WINDOW_SEC = max(180, int(duration_max * 1.5))
print("CHUNK_WINDOW_SEC calculation:", CHUNK_WINDOW_SEC)

def _ts(line):
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

# Let's query only 2 chunks to keep it fast
print(f"{len(chunks)} chunks created. Querying first 2 chunks as a test...")

all_clips = []
for i, (chunk_text, c_start, c_end) in enumerate(chunks[:2]):
    print(f"\n[Chunk {i+1}] {c_start:.0f}s - {c_end:.0f}s ...")
    chunk_prompt = f"""Tugas: Temukan 1 bagian (klip) percakapan paling menarik dari transkrip di bawah ini dengan durasi antara {duration_min} sampai {duration_max} detik.

Transkrip Segment ({c_start:.0f}s - {c_end:.0f}s):
{chunk_text}

Kembalikan output berupa JSON object dengan kunci berikut:
- "project_title": Judul topik bahasan utama (string)
- "clips": Daftar/array berisi 1 objek klip yang memiliki:
  - "title": Judul klip yang menarik (string)
  - "description": Deskripsi singkat klip tersebut untuk media sosial (string)
  - "start_seconds": Waktu mulai klip dalam angka detik (misalnya 15.4 atau 25.0) yang diambil dari timestamp transkrip di atas (float/int)
  - "end_seconds": Waktu selesai klip dalam angka detik (misalnya 115.4 atau 125.0) yang diambil dari timestamp transkrip di atas (float/int)

Pastikan start_seconds dan end_seconds berupa angka detik riil yang sesuai dengan transkrip di atas (antara {c_start:.0f} dan {c_end:.0f}). Jangan kembalikan teks tambahan selain objek JSON.
"""
    
    payload = {
        "model": ollama_model,
        "messages": [{"role": "user", "content": chunk_prompt}],
        "stream": False,
        "options": {
            "num_ctx": 4096,
            "num_predict": 2048,
            "temperature": 0.1
        }
    }
    
    try:
        res = requests.post(ollama_url, json=payload, timeout=120)
        res.raise_for_status()
        raw = res.json()['message']['content'].strip()
        print(f"[Chunk {i+1}] Preview:\n{raw[:300]}")
        parsed = clean_and_parse_json(raw)
        clips_found = parsed.get('clips', [])
        print(f"[Chunk {i+1}] Parsed clips found: {len(clips_found)}")
        all_clips.extend(clips_found)
    except Exception as e:
        print(f"[Chunk {i+1}] Error: {e}")

print(f"\nTotal clips gathered: {len(all_clips)}")
for c in all_clips:
    print("- Clip:", c)

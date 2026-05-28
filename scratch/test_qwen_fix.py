"""
Test Qwen dengan pendekatan berbeda:
1. Kirim prompt dengan contoh angka nyata DARI transkrip itu sendiri (bukan placeholder abstract)
2. Ekstrak timestamp pertama dan terakhir dari transkrip, pakai sebagai contoh dalam template
"""
import requests
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen"

sample_transcript = """[10.5s - 15.2s] Jadi, saya mau cerita tentang hal yang paling mengubah hidup saya.
[15.2s - 22.1s] Waktu itu saya baru saja keluar dari pekerjaan, tidak punya tabungan sama sekali.
[22.1s - 30.8s] Banyak orang bilang saya gila, tapi saya percaya dengan keputusan saya sendiri.
[30.8s - 40.3s] Ternyata memulai bisnis dari nol itu jauh lebih susah dari yang saya bayangkan.
[40.3s - 52.7s] Tapi justru karena itu, saya belajar hal-hal yang tidak bisa saya pelajari dari buku manapun.
[52.7s - 63.4s] Momen paling kritis adalah ketika uang sudah hampir habis dan saya hampir menyerah.
[63.4s - 75.1s] Tapi waktu itu ada satu customer yang membeli produk saya dan bilang produk saya mengubah hidupnya.
[75.1s - 85.6s] Dari situ saya sadar bahwa yang saya lakukan ada nilainya, dan saya terus berjuang.
[85.6s - 98.2s] Sekarang bisnis saya sudah berjalan 3 tahun dan kami sudah punya 20 karyawan.
[98.2s - 110.5s] Pesan saya: jangan takut gagal, karena kegagalan adalah guru terbaik yang pernah ada."""

duration_min = 30
duration_max = 60
c_start = 10.5
c_end = 110.5

# Ekstrak semua timestamp dari transkrip secara programatik
ts_pattern = re.compile(r'\[(\d+\.?\d*)s\s*-\s*(\d+\.?\d*)s\]')
all_timestamps = []
for line in sample_transcript.strip().split('\n'):
    m = ts_pattern.search(line)
    if m:
        all_timestamps.append((float(m.group(1)), float(m.group(2)), line))

print(f"Found {len(all_timestamps)} timestamps in transcript")
print(f"Range: {all_timestamps[0][0]}s to {all_timestamps[-1][1]}s")

# Cari timestamp yang cocok untuk mid-point clip
mid_idx = len(all_timestamps) // 2
example_start = all_timestamps[mid_idx][0]
example_end = min(example_start + (duration_min + duration_max) / 2, c_end)

print(f"Example start: {example_start}, example end: {example_end}")

# Buat prompt dengan CONTOH NYATA dari transkrip ini
prompt = f"""Baca transkrip berikut. Setiap baris punya timestamp [mulai_detik - akhir_detik].

TRANSKRIP:
{sample_transcript}

Pilih 1 bagian paling menarik. Durasi bagian = end_seconds - start_seconds, harus antara {duration_min} dan {duration_max} detik.

Contoh: jika bagian terbaik dimulai di baris "[{example_start}s - ...]" dan berakhir di sekitar detik {example_end:.1f}, maka:
- start_seconds: {example_start}
- end_seconds: {example_end:.1f}

Balas dengan JSON ini (ganti angka sesuai pilihan terbaik dari transkrip):
{{"project_title": "Perjuangan Bisnis dari Nol", "clips": [{{"title": "Momen Paling Kritis", "description": "Kisah nyata membangun bisnis", "start_seconds": {example_start}, "end_seconds": {example_end:.1f}}}]}}"""

print("\n" + "="*60)
print("Test: Qwen dengan contoh angka nyata dari transkrip")
print("="*60)

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": prompt}],
    "stream": False,
    "options": {"num_ctx": 4096, "num_predict": 512, "temperature": 0.1}
}

try:
    res = requests.post(OLLAMA_URL, json=payload, timeout=120)
    res.raise_for_status()
    raw = res.json()['message']['content'].strip()
    
    print(f"\nRAW OUTPUT:")
    print(raw[:600])
    
    # Clean and parse
    cleaned = re.sub(r'```(?:json)?\s*', '', raw)
    cleaned = re.sub(r'```\s*', '', cleaned).strip()
    
    # Try to extract JSON object
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
    
    parsed = json.loads(cleaned)
    clips = parsed.get('clips', [])
    
    print(f"\nResult: {len(clips)} clip(s)")
    for c in clips:
        s = float(c.get('start_seconds', 0))
        e = float(c.get('end_seconds', 0))
        dur = e - s
        ts_values = [t[0] for t in all_timestamps] + [t[1] for t in all_timestamps]
        min_ts = min(ts_values)
        max_ts = max(ts_values)
        
        print(f"  start={s}, end={e}, dur={dur:.1f}s")
        
        is_real = (min_ts <= s <= max_ts) and (min_ts <= e <= max_ts)
        is_valid_dur = duration_min <= dur <= duration_max
        
        if is_real and is_valid_dur:
            print("  [SUCCESS] Real timestamps + valid duration!")
        elif is_real:
            print(f"  [PARTIAL] Real timestamps but duration {dur:.1f}s out of range")
        else:
            print(f"  [FAIL] Not using real timestamps (range: {min_ts:.1f}-{max_ts:.1f})")
            
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print(f"Content that failed: {cleaned[:300]}")
except Exception as e:
    print(f"Error: {e}")

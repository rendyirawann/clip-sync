"""
Test line-number-picker strategy for Qwen.
Qwen sees numbered sentences (no timestamps), picks start/end line numbers.
We map those back to real timestamps ourselves.
"""
import requests, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen"

# Build fake 10-minute transcript
sentences = [
    "Saya mau cerita tentang hal yang mengubah hidup saya.",
    "Waktu itu saya baru keluar dari pekerjaan tanpa tabungan.",
    "Banyak yang bilang saya gila tapi saya tetap percaya diri.",
    "Memulai bisnis dari nol jauh lebih susah dari bayangan saya.",
    "Tapi justru itu yang membuat saya belajar hal luar biasa.",
    "Momen paling kritis adalah saat uang hampir habis total.",
    "Tapi satu customer bilang produk saya mengubah hidupnya.",
    "Dari situ saya dapat kekuatan untuk terus berjuang maju.",
    "Sekarang bisnis sudah berjalan 3 tahun dengan 20 karyawan.",
    "Pesan saya: jangan takut gagal karena itu adalah guru terbaik.",
    "Pertanyaan yang sering masuk: bagaimana cara dapat modal awal?",
    "Ada tiga cara yang sudah saya coba sendiri dan berhasil.",
    "Pertama, bootstrapping dari tabungan sendiri walau kecil.",
    "Kedua, cari angel investor yang visinya sama dengan kita.",
    "Ketiga, revenue-based financing yang banyak tidak tahu.",
    "Ini tidak ada equity yang hilang dan bayar sesuai revenue.",
    "Kalau bulan ini sepi bayarnya juga sedikit, adil kan?",
    "Cara ini jauh lebih manusiawi dari pinjaman bank konvensional.",
    "Oke sekarang kita masuk ke sesi tanya jawab bersama.",
    "Silakan tanya apa saja yang ingin kalian ketahui.",
]

lines_data = []
t = 5.0
for s in sentences:
    dur = len(s) * 0.09 + 3.0
    lines_data.append((t, t + dur, s))
    t += dur + 0.5

# Build numbered list WITHOUT timestamps (what Qwen sees)
numbered_lines = [(i+1, s, e, txt) for i, (s, e, txt) in enumerate(lines_data)]
nl_text = "\n".join(f"{n}. {txt}" for n, _, _, txt in numbered_lines)
n_lines = len(numbered_lines)

duration_min, duration_max = 30, 90
target_sec = (duration_min + duration_max) / 2
chunk_dur = lines_data[-1][1] - lines_data[0][0]
lines_per_sec = n_lines / chunk_dur
target_lines = max(3, min(n_lines - 1, int(target_sec * lines_per_sec)))

print(f"Transcript: {n_lines} lines, {chunk_dur:.1f}s, target_lines={target_lines}")
print("="*55)

prompt = (
    "Baca daftar kalimat video berikut:\n\n"
    + nl_text
    + f"\n\nDari daftar di atas (total {n_lines} kalimat), pilih 1 bagian yang paling menarik dan emosional."
    + f"\nBagian yang dipilih harus mencakup sekitar {target_lines} kalimat berurutan."
    + 'Balas HANYA dengan JSON objek. Field:\n'
    + '- title: string\n'
    + '- description: string\n'
    + '- start_line: integer (nomor baris mulai)\n'
    + '- end_line: integer (nomor baris selesai)\n\n'
    + 'Pastikan format JSON valid.'
)

print("Sending to Qwen...")
res = requests.post(OLLAMA_URL, json={
    "model": MODEL,
    "messages": [{"role": "user", "content": prompt}],
    "stream": False,
    "options": {"num_ctx": 4096, "num_predict": 256, "temperature": 0.3}
}, timeout=120)
raw = res.json()['message']['content'].strip()
print(f"RAW: {raw[:300]}\n")

# Parse JSON
cleaned = re.sub(r'```(?:json)?\s*', '', raw)
cleaned = re.sub(r'```\s*', '', cleaned).strip()
m = re.search(r'\{.*\}', cleaned, re.DOTALL)
if m:
    cleaned = m.group(0)
parsed = json.loads(cleaned)

sl = max(1, min(int(parsed.get("start_line", 1)), n_lines))
el = max(sl + 1, min(int(parsed.get("end_line", target_lines)), n_lines))

real_start = numbered_lines[sl - 1][1]
real_end   = numbered_lines[el - 1][2]
dur = real_end - real_start

# Adjust duration
if dur < duration_min:
    for ext in range(el, n_lines + 1):
        real_end = numbered_lines[ext - 1][2]
        if real_end - real_start >= duration_min:
            break
elif dur > duration_max * 1.5:
    for shr in range(el, sl, -1):
        real_end = numbered_lines[shr - 1][2]
        if real_end - real_start <= duration_max * 1.2:
            break

dur = real_end - real_start
print(f"Lines {sl}-{el} -> {real_start:.1f}s - {real_end:.1f}s ({dur:.1f}s)")
print(f"Title: {parsed.get('title')}")
print(f"Description: {parsed.get('description')}")

if duration_min * 0.7 <= dur <= duration_max * 1.5:
    print(f"\n[SUCCESS] Valid clip: {real_start:.1f}s - {real_end:.1f}s ({dur:.1f}s)")
else:
    print(f"\n[FAIL] Duration {dur:.1f}s out of range {duration_min}-{duration_max}s")

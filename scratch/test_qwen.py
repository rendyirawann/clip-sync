import json
import requests
import re

# Load transcript cache
with open('storage/app/public/clipper/44/transcript_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

transcript_segments = cache['segments']

def get_compact_transcript(segments, group_size=8):
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

transcript_text = get_compact_transcript(transcript_segments)

print("Transcript text length:", len(transcript_text))

clip_count = 3
duration_min = 90
duration_max = 140
is_podcast = True

schema_desc = """{
  "project_title": "Catchy Overall Video Project Title in natural Indonesian summarizing the video context",
  "clips": [
    {
      "title": "Viral Catchy Title in natural Indonesian",
      "description": "Engaging Indonesian caption... \\n\\n#fyp #podcast",
      "start_seconds": 45,
      "end_seconds": 95,
      "speaker_timeline": [
        {"start": 45, "end": 60, "speaker": 1},
        {"start": 60, "end": 75, "speaker": 2},
        {"start": 75, "end": 95, "speaker": 1}
      ]
    }
  ]
}"""

podcast_instruction = """
4. DETECT SPEAKERS: Analyze the dialogue flow and assign speaker turns. In your 'speaker_timeline' array, break down the clip into sub-segments where 'speaker': 1 is the main speaker/host, and 'speaker': 2 is the guest/responder. Keep timelines sequential covering the entire range from 'start_seconds' to 'end_seconds'.
"""

prompt = f"""
You are an expert video clipper assistant. Your objective is to analyze the following transcript dialogue which contains speech timestamps in the format '[start_seconds - end_seconds]' next to each spoken line.
Using these timestamps, identify exactly {clip_count} highly engaging, viral, or interesting highlight segments/clips.
Each segment should be between {duration_min} to {duration_max} seconds. These should represent the peak moments of the video.

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
    "model": "qwen",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "stream": False,
    "format": "json",
    "options": {
        "num_ctx": 8192,
        "temperature": 0.1
    }
}

print("Sending request to Ollama (qwen)...")
response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=300)
print("Status code:", response.status_code)
ollama_response = response.json()
raw_content = ollama_response['message']['content']
print("Raw Content Length:", len(raw_content))
print("Raw Content:\n", raw_content)

import json
import re

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

# Run tests
test_cases = [
    # 1. Standard double-quoted JSON
    '{"project_title": "Video Highlights", "clips": [{"title": "Awesome Moments", "start_seconds": 10.5, "end_seconds": 45.0}]}',
    
    # 2. Single-quoted JSON (Common with Qwen local model)
    "{'project_title': 'Video Highlights', 'clips': [{'title': 'Awesome Moments', 'start_seconds': 10.5, 'end_seconds': 45.0}]}",
    
    # 3. JSON wrapped in markdown codeblock
    """```json
    {"project_title": "Video Highlights", "clips": [{"title": "Awesome Moments", "start_seconds": 10.5, "end_seconds": 45.0}]}
    ```""",
    
    # 4. Single-quoted JSON wrapped in markdown
    """```
    {'project_title': 'Video Highlights', 'clips': [{'title': 'Awesome Moments', 'start_seconds': 10.5, 'end_seconds': 45.0}]}
    ```""",
    
    # 5. JSON with trailing comma (valid in Python ast but invalid in JSON)
    '{"project_title": "Video Highlights", "clips": [{"title": "Awesome Moments", "start_seconds": 10.5, "end_seconds": 45.0},],}',
    
    # 6. JSON with true/false/null in single quotes
    "{'project_title': 'Video Highlights', 'is_podcast': true, 'watermark': null, 'clips': [{'title': 'Awesome Moments', 'start_seconds': 10.5, 'end_seconds': 45.0}]}",
    
    # 7. JSON surrounded by chatty model conversations
    "Here is the result of my analysis:\n```json\n{'project_title': 'Video Highlights', 'clips': [{'title': 'Awesome Moments', 'start_seconds': 10.5, 'end_seconds': 45.0}]}\n```\nHope you like it!"
]

print("Running JSON helper unit tests...\n")
success_count = 0
for idx, case in enumerate(test_cases, 1):
    print(f"--- Test Case {idx} ---")
    print(f"Raw Input (truncated):\n{case[:100]}...")
    try:
        parsed = clean_and_parse_json(case)
        print("Parsed Successfully!")
        print(f"Result type: {type(parsed)}")
        print(f"Project Title: {parsed.get('project_title')}")
        print(f"Clips Count: {len(parsed.get('clips', []))}")
        if 'is_podcast' in parsed:
            print(f"Is Podcast: {parsed.get('is_podcast')} (type: {type(parsed.get('is_podcast'))})")
        if 'watermark' in parsed:
            print(f"Watermark: {parsed.get('watermark')} (type: {type(parsed.get('watermark'))})")
        success_count += 1
    except Exception as e:
        print(f"FAILED with error: {e}")
    print()

print(f"Summary: {success_count}/{len(test_cases)} tests passed.")
if success_count == len(test_cases):
    print("ALL TESTS PASSED! The helper function is extremely robust!")
else:
    print("SOME TESTS FAILED! Needs investigation.")

"""Extract Edge cookies for YouTube using rookiepy and save as Netscape format."""
import rookiepy
import time

OUT_PATH = r"C:\xampp\htdocs\myProject\clip-sync\cookies_auto.txt"

try:
    cookies = rookiepy.edge([".youtube.com", "youtube.com"])
    
    lines = [
        "# Netscape HTTP Cookie File",
        "# Extracted automatically by Clip-Sync via rookiepy (Edge)",
        ""
    ]
    
    for c in cookies:
        domain = c.get("domain", "")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure", False) else "FALSE"
        expires = int(c.get("expires", 0) or (time.time() + 31536000))
        name = c.get("name", "")
        value = c.get("value", "")
        lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}")
    
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    
    with open(OUT_PATH + ".log", "w") as f:
        f.write(f"OK: {len(cookies)} cookies extracted from Edge\n")
except Exception as e:
    with open(OUT_PATH + ".log", "w") as f:
        f.write(f"ERROR: {e}\n")

import os
import urllib.request

def download_file(url, dest_path):
    print(f"Downloading {url} to {dest_path}...")
    try:
        # User-agent header to avoid 403 Forbidden
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req) as response:
            with open(dest_path, 'wb') as out_file:
                out_file.write(response.read())
        print(f"Downloaded successfully: {dest_path}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def main():
    bgm_dir = r"c:\xampp\htdocs\myProject\clip-sync\storage\app\public\bgm\phonk"
    os.makedirs(bgm_dir, exist_ok=True)
    
    tracks = [
        ("https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", "phonk_drift_hype.mp3"),
        ("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "cowbell_eclipse.mp3"),
        ("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", "memphis_shadow.mp3")
    ]
    
    for url, filename in tracks:
        dest = os.path.join(bgm_dir, filename)
        if not os.path.exists(dest):
            download_file(url, dest)
        else:
            print(f"File already exists: {dest}")

if __name__ == "__main__":
    main()

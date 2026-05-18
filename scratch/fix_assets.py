import os
import glob

dir_path = 'c:/xampp/htdocs/myProject/lms-sync/resources/views/backend/layout/*.blade.php'
files = glob.glob(dir_path)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the escaped single quotes
    content = content.replace("\\'", "'")
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Escaped quotes fixed successfully!")

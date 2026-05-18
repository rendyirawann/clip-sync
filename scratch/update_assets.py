import os
import glob
import re

dir_path = 'c:/xampp/htdocs/myProject/lms-sync/resources/views/backend/layout/*.blade.php'
files = glob.glob(dir_path)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace href="assets/...
    content = re.sub(r'href="assets/([^"]+)"', r'href="{{ asset(\'assets/\1\') }}"', content)
    # Replace src="assets/...
    content = re.sub(r'src="assets/([^"]+)"', r'src="{{ asset(\'assets/\1\') }}"', content)
    # Replace var hostUrl = "assets/";
    content = content.replace('var hostUrl = "assets/";', 'var hostUrl = "{{ asset(\'assets/\') }}";')
    # Replace src="https://... (keep as is)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Asset paths updated successfully in all layout files!")

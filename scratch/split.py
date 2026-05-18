import os

file_path = 'c:/xampp/htdocs/myProject/lms-sync/resources/views/backend/layout/app.blade.php'
dir_path = 'c:/xampp/htdocs/myProject/lms-sync/resources/views/backend/layout'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Menu (Lines 54 to 3292) -> 0-indexed: 53 to 3292
menu_lines = lines[53:3292]
with open(os.path.join(dir_path, 'menu.blade.php'), 'w', encoding='utf-8') as f:
    f.writelines(menu_lines)

# Sidebar (Lines 52 to 53, include menu, Lines 3293 to 3305) -> 0-indexed: 51:53, 3292:3305
sidebar_lines = lines[51:53] + ['\t\t\t\t\t@include(\'backend.layout.menu\')\n'] + lines[3292:3305]
with open(os.path.join(dir_path, 'sidebar.blade.php'), 'w', encoding='utf-8') as f:
    f.writelines(sidebar_lines)

# Navbar (Lines 3308 to 4291) -> 0-indexed: 3307:4291
navbar_lines = lines[3307:4291]
with open(os.path.join(dir_path, 'navbar.blade.php'), 'w', encoding='utf-8') as f:
    f.writelines(navbar_lines)

# Footer (Lines 7294 to 7320) -> 0-indexed: 7293:7320
footer_lines = lines[7293:7320]
with open(os.path.join(dir_path, 'footer.blade.php'), 'w', encoding='utf-8') as f:
    f.writelines(footer_lines)

# Main App (Lines 1 to 51, sidebar, Lines 3306 to 3307, navbar, Lines 4292 to 4295, yield, Lines 7291 to 7293, footer, Lines 7321 to end)
app_lines = lines[0:51] + \
            ['\t\t\t\t@include(\'backend.layout.sidebar\')\n'] + \
            lines[3305:3307] + \
            ['\t\t\t\t\t@include(\'backend.layout.navbar\')\n'] + \
            lines[4291:4295] + \
            ['\t\t\t\t\t\t\t@yield(\'content\')\n'] + \
            lines[7290:7293] + \
            ['\t\t\t\t\t@include(\'backend.layout.footer\')\n'] + \
            lines[7320:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(app_lines)

print("Successfully split the files!")

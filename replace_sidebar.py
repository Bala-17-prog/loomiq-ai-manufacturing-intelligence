import os
import re

html_files = [f for f in os.listdir('frontend') if f.endswith('.html')]
sidebar_pattern = re.compile(r'<aside class="sidebar">.*?</aside>', re.DOTALL)

for f in html_files:
    path = os.path.join('frontend', f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = sidebar_pattern.sub('<aside id="sidebar-mount" class="sidebar collapsed"></aside>', content)
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    print(f'Updated {f}')

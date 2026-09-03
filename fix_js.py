import os

for f in os.listdir('frontend'):
    if f.endswith('.html'):
        path = os.path.join('frontend', f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        if 'js/common.js' not in content:
            new_content = content.replace('</body>', '    <script src="js/common.js"></script>\n</body>')
            with open(path, 'w', encoding='utf-8') as outfile:
                outfile.write(new_content)
            print(f'Injected common.js into {f}')

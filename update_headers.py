import os
import re

header_actions = '''<div class="header-actions">
                    <span>Main Plant</span>
                    <span>•</span>
                    <span id="current-date">Updated Just Now</span>
                    <button class="btn btn-secondary" onclick="location.reload()" aria-label="Refresh" style="padding: 6px; height: 32px; width: 32px;">
                        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                    </button>
                </div>'''

html_files = [f for f in os.listdir('frontend') if f.endswith('.html')]

# We'll use a regex to replace <div class="header-actions">...</div> with the new one
actions_pattern = re.compile(r'<div class="header-actions">.*?</div>', re.DOTALL)

for f in html_files:
    path = os.path.join('frontend', f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if '<div class="header-actions">' in content:
        new_content = actions_pattern.sub(header_actions, content)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f'Updated headers in {f}')
    else:
        # If it doesn't have header-actions, inject it into the top-header
        top_header_pattern = re.compile(r'(<header class="top-header">.*?</div>\s*)(</header>)', re.DOTALL)
        if top_header_pattern.search(content):
            new_content = top_header_pattern.sub(r'\1' + header_actions + r'\n            \2', content)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f'Injected headers in {f}')

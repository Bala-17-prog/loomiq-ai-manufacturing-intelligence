import os, re
frontend_dir = r'd:\loomiq-ai-manufacturing-intelligence\frontend'
files = ['index.html', 'production.html', 'machines.html', 'quality.html', 'copilot.html', 'simulator.html', 'data.html', 'about.html']
menu_map = {
    'index.html': 'Dashboard', 
    'production.html': 'Production', 
    'machines.html': 'Machines', 
    'quality.html': 'Quality Inspection', 
    'copilot.html': 'AI Copilot', 
    'simulator.html': 'What-If Simulator', 
    'data.html': 'Data', 
    'about.html': 'About'
}
nav_pattern = re.compile(r'<nav class="nav-menu">.*?</nav>', re.DOTALL)
for fname in files:
    path = os.path.join(frontend_dir, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_nav = '<nav class="nav-menu">\n'
    for k, v in menu_map.items():
        active = ' active' if k == fname else ''
        new_nav += f'                <a href="{k}" class="nav-item{active}">{v}</a>\n'
    new_nav += '            </nav>'
    content = nav_pattern.sub(new_nav, content)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
print("Navigation updated successfully.")

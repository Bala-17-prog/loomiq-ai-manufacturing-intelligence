import os

def update_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


# Quality.html
quality_reps = [
    ('background: rgba(255,255,255,0.02);', 'background: var(--bg-main);'),
    ('background: rgba(59, 130, 246, 0.05);', 'background: var(--accent-blue-light);'),
    ('border: 1px solid var(--success); color: var(--success);', 'background: var(--success-light); color: var(--success);'),
    ('border: 1px solid var(--warning); color: var(--warning);', 'background: var(--warning-light); color: var(--warning);'),
    ('border: 1px solid #f97316; color: #f97316;', 'background: var(--warning-light); color: var(--warning);'),
    ('border: 1px solid var(--danger); color: var(--danger);', 'background: var(--danger-light); color: var(--danger);'),
    ('rgba(16, 185, 129, 0.1)', 'var(--success-light)'),
    ('rgba(239, 68, 68, 0.1)', 'var(--danger-light)'),
    ('DETECTION SIGNAL STRENGTH', 'DETECTION SIGNAL STRENGTH'), # Make sure it's correct
    ('background: var(--bg-dark);', 'background: white;'),
    ('background: #222;', 'background: var(--border-color);'),
    ('background: rgba(0,0,0,0.2);', 'background: var(--card-bg);'),
    ('color: white;', 'color: white;'),
    ('id="res-confidence"', 'id="res-confidence"'),
]

# Copilot.html
copilot_reps = [
    ('background: rgba(59, 130, 246, 0.1);', 'background: var(--accent-blue-light);'),
    ('background: rgba(255, 255, 255, 0.03);', 'background: var(--bg-main);'),
    ('background: var(--bg-dark);', 'background: var(--bg-main);'),
    ('background: rgba(255,255,255,0.05);', 'background: white;'),
    ('color: white;', 'color: var(--text-primary);'),
    ('.chat-message.ai strong { color: white; }', '.chat-message.ai strong { color: var(--text-primary); }'),
    ('background: var(--accent-blue);\\n            color: white;', 'background: var(--accent-blue);\\n            color: white;'),
]

# Simulator.html
simulator_reps = [
    ('background: rgba(255,255,255,0.1);', 'background: var(--border-color);'),
    ('background: rgba(16, 185, 129, 0.05);', 'background: var(--success-light);'),
    ('border: 1px solid rgba(16, 185, 129, 0.2);', 'border: 1px solid var(--success);'),
    ('background: rgba(239, 68, 68, 0.05);', 'background: var(--danger-light);'),
    ('border: 1px solid rgba(239, 68, 68, 0.2);', 'border: 1px solid var(--danger);'),
    ('color: var(--text-secondary); margin-bottom: 12px;', 'color: var(--text-primary); font-weight: 500; margin-bottom: 12px;'),
    ('color: var(--text-secondary);', 'color: var(--text-secondary);'),
]

# Data.html
data_reps = [
    ('color: white;', 'color: var(--text-primary);'),
]

update_file('frontend/quality.html', quality_reps)
update_file('frontend/copilot.html', copilot_reps)
update_file('frontend/simulator.html', simulator_reps)
update_file('frontend/data.html', data_reps)
print('Applied enterprise design to remaining files')

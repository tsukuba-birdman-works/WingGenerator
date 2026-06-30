import re

with open('/home/akihito-kasai/.config/Code/User/History/50b3bc30/EYfi.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'Tab ' in line or 'tab_' in line or 'LabelFrame' in line or 'ttk.Label' in line:
        if 'text=' in line:
            m = re.search(r'text="([^"]+)"', line)
            if m:
                print(f"{i+1}: {m.group(1)}")

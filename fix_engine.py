import re

with open('core/engine.py', 'r') as f:
    text = f.read()

target1 = "chord = p['chord_root'] * (1 - t) + p['chord_tip'] * t"
replacement1 = "chord = max(p['chord_root'] * (1 - t) + p['chord_tip'] * t, 1.0)  # Prevent extremely small/zero chords"

if target1 in text:
    text = text.replace(target1, replacement1)
    with open('core/engine.py', 'w') as f:
        f.write(text)
    print("Patched chord calculation in get_local_params")
else:
    print("Target 1 not found!")


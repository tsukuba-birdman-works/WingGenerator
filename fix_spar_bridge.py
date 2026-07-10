import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

target = """            'cam_milling_dir': getattr(self, 'cam_milling_dir', tk.StringVar(value="Conventional (Outer CW)")).get(),
        }"""

replacement = """            'cam_milling_dir': getattr(self, 'cam_milling_dir', tk.StringVar(value="Conventional (Outer CW)")).get(),
            'spar_bridge_padding': getattr(self, 'safe_float')(getattr(self, 'spar_bridge_padding', tk.StringVar(value="0.5")), 0.5),
            'spar_bridge_thickness': getattr(self, 'safe_float')(getattr(self, 'spar_bridge_thickness', tk.StringVar(value="3.0")), 3.0),
        }"""

if target in text:
    text = text.replace(target, replacement)
    with open('ui/batch_mode.py', 'w') as f:
        f.write(text)
    print("Successfully patched batch_mode.py")
else:
    print("Target string not found!")


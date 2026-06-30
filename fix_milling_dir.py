import re

for filename in ["ui/base_mode.py"]:
    with open(filename, "r") as f:
        code = f.read()
    
    # Replace the OptionMenu definition
    code = code.replace(
        'dir_menu = tk.OptionMenu(lf_cam, self.cam_milling_dir, "Conventional", "Climb")',
        'dir_menu = tk.OptionMenu(lf_cam, self.cam_milling_dir, "Conventional (Outer CW)", "Climb (Outer CCW)")'
    )
    code = code.replace(
        'self.cam_milling_dir = tk.StringVar(value="Conventional")',
        'self.cam_milling_dir = tk.StringVar(value="Conventional (Outer CW)")'
    )
    
    with open(filename, "w") as f:
        f.write(code)

with open("core/cam_engine.py", "r") as f:
    code = f.read()

code = code.replace("target_ccw = (milling_dir == 'Climb')", "target_ccw = milling_dir.startswith('Climb')")
code = code.replace("target_ccw = (milling_dir == 'Conventional')", "target_ccw = milling_dir.startswith('Conventional')")

with open("core/cam_engine.py", "w") as f:
    f.write(code)

print("Milling direction clarified.")

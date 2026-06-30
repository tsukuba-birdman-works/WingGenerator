import re

with open("ui/base_mode.py", "r") as f:
    code = f.read()

# Change create_stringers_tab to create_stringers_ui
code = code.replace("def create_stringers_tab(self, notebook):", "def create_stringers_ui(self, parent_frame):")
code = code.replace("tab = tk.Frame(notebook)", "tab = tk.LabelFrame(parent_frame, text='Stringers')")
code = code.replace("notebook.add(tab, text=\"Stringers\")", "tab.pack(fill=tk.X, padx=10, pady=5)")

# Change create_cam_tab to create_cam_ui
code = code.replace("def create_cam_tab(self, notebook):", "def create_cam_ui(self, parent_frame):")
code = code.replace("tab = tk.Frame(notebook)", "tab = tk.Frame(parent_frame)")
code = code.replace("notebook.add(tab, text=\"CNC CAM & Tabs\")", "tab.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)")

with open("ui/base_mode.py", "w") as f:
    f.write(code)

with open("ui/batch_mode.py", "r") as f:
    bcode = f.read()

bcode = bcode.replace("self.create_stringers_tab(notebook)", "self.create_stringers_ui(self.pm.obj.tabs_frames['PlankTE'])")
bcode = bcode.replace("self.create_cam_tab(notebook)", "self.create_cam_ui(self.pm.obj.tabs_frames['CNC'])")

with open("ui/batch_mode.py", "w") as f:
    f.write(bcode)

with open("ui/single_mode.py", "r") as f:
    scode = f.read()

scode = scode.replace("self.create_stringers_tab(notebook)", "self.create_stringers_ui(self.pm.obj.tabs_frames['PlankTE'])")
scode = scode.replace("self.create_cam_tab(notebook)", "self.create_cam_ui(self.pm.obj.tabs_frames['CNC'])")

with open("ui/single_mode.py", "w") as f:
    f.write(scode)

print("Base, batch, and single modes patched!")

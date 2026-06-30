import re

with open("ui/base_mode.py", "r") as f:
    code = f.read()

replacement = """
    def create_cam_ui(self, notebook):
        from tkinter import ttk
        # Create the CNC tab
        f_tab_outer = ttk.Frame(notebook)
        notebook.add(f_tab_outer, text="CNC")
        
        if hasattr(self, 'pm'):
            self.pm.obj.tabs_frames['CNC'] = f_tab_outer
"""

code = code.replace("    def create_cam_ui(self, notebook):\n        from tkinter import ttk\n        # Create the CNC tab\n        f_tab_outer = ttk.Frame(notebook)\n        notebook.add(f_tab_outer, text=\"CNC\")", replacement.strip('\n'))

with open("ui/base_mode.py", "w") as f:
    f.write(code)

print("Export G-Code button KeyError fixed!")

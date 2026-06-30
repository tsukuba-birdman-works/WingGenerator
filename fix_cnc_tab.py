import re

# 1. Update base_mode.py create_cam_ui to accept the notebook and create the tab itself
with open("ui/base_mode.py", "r") as f:
    code = f.read()

replacement = """
    def create_cam_ui(self, notebook):
        from tkinter import ttk
        # Create the CNC tab
        f_tab_outer = ttk.Frame(notebook)
        notebook.add(f_tab_outer, text="CNC")
        
        # Add scrollbars just like other tabs
        import tkinter as tk
        canvas = tk.Canvas(f_tab_outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(f_tab_outer, orient="vertical", command=canvas.yview)
        parent_frame = ttk.Frame(canvas)

        parent_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
        canvas.create_window((0, 0), window=parent_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event, c=canvas):
            c.yview_scroll(int(-1*(event.delta/120)), "units")
        f_tab_outer.bind("<Enter>", lambda e, c=canvas, mw=_on_mousewheel: c.bind_all("<MouseWheel>", mw))
        f_tab_outer.bind("<Leave>", lambda e, c=canvas: c.unbind_all("<MouseWheel>"))

        tab = tk.LabelFrame(parent_frame, text='CNC Support & Tool Settings')
"""

code = re.sub(
    r"    def create_cam_ui\(self, parent_frame\):\n        from tkinter import ttk\n        tab = tk\.LabelFrame\(parent_frame, text='CNC Support & Tool Settings'\)",
    replacement.strip('\n'),
    code
)

with open("ui/base_mode.py", "w") as f:
    f.write(code)

# 2. Update batch_mode.py and single_mode.py to pass notebook instead of the missing CNC frame
for filename in ["ui/batch_mode.py", "ui/single_mode.py"]:
    with open(filename, "r") as f:
        mcode = f.read()
    
    mcode = mcode.replace("self.create_cam_ui(self.pm.obj.tabs_frames['CNC'])", "self.create_cam_ui(notebook)")
    
    with open(filename, "w") as f:
        f.write(mcode)

print("CNC tab manually restored!")

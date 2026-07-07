import sys

with open('ui/single_mode.py', 'r') as f:
    content = f.read()

import re

# Update create_widgets logic
new_create = """    def create_widgets(self):
        import tkinter as tk
        from tkinter import ttk
        
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(main_pane, width=450)
        main_pane.add(left_frame, weight=0)

        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.ui_builder.build_tabs(notebook, self.pm)
        
        if 'Plank TE' in self.pm.obj.tabs_frames:
            self.create_stringers_ui(self.pm.obj.tabs_frames['Plank TE'])
            
        if 'DXF' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['DXF'], text="Export DXF", command=self.export_dxf).pack(fill=tk.X, padx=10, pady=5)
            
        if 'CNC' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['CNC'], text="Export CNC (G-Code)", command=self.export_gcode).pack(fill=tk.X, padx=10, pady=5)
            
        f_top = ttk.Frame(left_frame)
        f_top.pack(fill=tk.X, side=tk.TOP, before=notebook)
        ttk.Button(f_top, text="Load Config", command=self.load_config).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(f_top, text="Save Config", command=self.save_config).pack(side=tk.LEFT, expand=True, fill=tk.X)

        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)

        lf_preview = ttk.LabelFrame(right_frame, text="Rib Preview")
        lf_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        control_frame = ttk.Frame(lf_preview)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="Update Preview", command=self.update_preview).pack(side=tk.LEFT, padx=5)
        
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.fig = Figure(figsize=(7, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=lf_preview)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        for var in self.pm.vars.values():
            if hasattr(var, 'trace_add'):
                try: var.trace_add("write", lambda *args: self.update_preview())
                except: pass"""

content = re.sub(r'    def create_widgets\(self\):.*?                except: pass', new_create, content, flags=re.DOTALL)

with open('ui/single_mode.py', 'w') as f:
    f.write(content)

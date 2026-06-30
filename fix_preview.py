import re

files_to_fix = ["ui/batch_mode.py", "ui/single_mode.py"]

for filepath in files_to_fix:
    with open(filepath, "r") as f:
        code = f.read()

    # Fix apply_local_angle_full signature
    code = code.replace("def apply_local_angle_full(self, event):", "def apply_local_angle_full(self, event=None):")

    # Fix preview canvas initialization
    bad_canvas_init = """        self.fig_canvas_frame = ttk.Frame(lf_preview)
        self.fig_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas_widget = None"""
        
    good_canvas_init = """        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.fig = Figure(figsize=(7, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=lf_preview)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)"""
        
    code = code.replace(bad_canvas_init, good_canvas_init)

    with open(filepath, "w") as f:
        f.write(code)

print("Fixed preview canvas and apply_local_angle_full")

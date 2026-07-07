import re

with open('ui/base_mode.py', 'r', encoding='utf-8') as f:
    content = f.read()

def get_indent(line):
    return len(line) - len(line.lstrip())

start_str = "    def create_cam_ui(self, notebook):"
end_str = "    def get_cam_vars(self):"

start_idx = content.find(start_str)
end_idx = content.find(end_str)

new_method = """    def create_cam_ui(self, notebook):
        from tkinter import ttk
        import tkinter as tk
        import json
        from tkinter import filedialog, messagebox
        import os

        # --- Tab 1: Tabs & Supports ---
        f_tab_supports = ttk.Frame(notebook)
        notebook.add(f_tab_supports, text="Tabs & Supports")
        
        canvas_supp = tk.Canvas(f_tab_supports, highlightthickness=0)
        scroll_supp = ttk.Scrollbar(f_tab_supports, orient="vertical", command=canvas_supp.yview)
        parent_supp = ttk.Frame(canvas_supp)
        if hasattr(self, 'pm'):
            self.pm.obj.tabs_frames['Tabs & Supports'] = parent_supp

        parent_supp.bind("<Configure>", lambda e, c=canvas_supp: c.configure(scrollregion=c.bbox("all")))
        canvas_supp.create_window((0, 0), window=parent_supp, anchor="nw")
        canvas_supp.configure(yscrollcommand=scroll_supp.set)
        
        canvas_supp.pack(side="left", fill="both", expand=True)
        scroll_supp.pack(side="right", fill="y")

        def _on_mousewheel_supp(event, c=canvas_supp):
            c.yview_scroll(int(-1*(event.delta/120)), "units")
        f_tab_supports.bind("<Enter>", lambda e, c=canvas_supp, mw=_on_mousewheel_supp: c.bind_all("<MouseWheel>", mw))
        f_tab_supports.bind("<Leave>", lambda e, c=canvas_supp: c.unbind_all("<MouseWheel>"))

        tab_supp = tk.LabelFrame(parent_supp, text='Holding Tabs & E-Supports')
        tab_supp.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Checkbutton(tab_supp, text="Enable All Tabs", variable=self.tabs_active).pack(anchor="w", padx=10, pady=(10, 5))
        
        lf_truss = tk.LabelFrame(tab_supp, text="Holding Tabs")
        lf_truss.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(lf_truss, text="Inner Tab Base Width (mm):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.truss_tab_width, width=8).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        tk.Label(lf_truss, text="Outer Tab Base Width (mm):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.outer_tab_width, width=8).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        tk.Label(lf_truss, text="Outer Tab Interval (mm):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.outer_tab_interval, width=8).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        tk.Label(lf_truss, text="Tab Thickness Z (mm):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_thickness, width=8).grid(row=3, column=1, sticky="w", padx=5, pady=2)
        tk.Label(lf_truss, text="Tab Z Angle (deg):").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_angle_deg, width=8).grid(row=4, column=1, sticky="w", padx=5, pady=2)
        tk.Label(lf_truss, text="Exclusion (Stringer, mm):").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_exclusion_stringer, width=8).grid(row=5, column=1, sticky="w", padx=5, pady=2)
        tk.Label(lf_truss, text="Exclusion (LE/TE, mm):").grid(row=6, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(lf_truss, textvariable=self.tab_exclusion_le_te, width=8).grid(row=6, column=1, sticky="w", padx=5, pady=2)
        
        lf_main = tk.LabelFrame(tab_supp, text="Main Spar E-Support")
        lf_main.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(lf_main, text="Leg Width (mm):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_main, textvariable=self.main_spar_support_w, width=8).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        tk.Label(lf_main, text="Lift Height (mm):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_main, textvariable=self.main_spar_support_h, width=8).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(lf_main, text="Snap Thickness Z (mm):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_main, textvariable=self.main_spar_support_thick, width=8).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        lf_fr = tk.LabelFrame(tab_supp, text="F/R Spar Tabs")
        lf_fr.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(lf_fr, text="Bridge Padding (mm):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_fr, textvariable=self.spar_bridge_padding, width=8).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        tk.Label(lf_fr, text="Snap Thickness Z (mm):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_fr, textvariable=self.spar_bridge_thickness, width=8).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # --- Tab 2: CNC ---
        f_tab_cnc = ttk.Frame(notebook)
        notebook.add(f_tab_cnc, text="CNC")
        
        canvas_cnc = tk.Canvas(f_tab_cnc, highlightthickness=0)
        scroll_cnc = ttk.Scrollbar(f_tab_cnc, orient="vertical", command=canvas_cnc.yview)
        parent_cnc = ttk.Frame(canvas_cnc)
        if hasattr(self, 'pm'):
            self.pm.obj.tabs_frames['CNC'] = parent_cnc

        parent_cnc.bind("<Configure>", lambda e, c=canvas_cnc: c.configure(scrollregion=c.bbox("all")))
        canvas_cnc.create_window((0, 0), window=parent_cnc, anchor="nw")
        canvas_cnc.configure(yscrollcommand=scroll_cnc.set)
        
        canvas_cnc.pack(side="left", fill="both", expand=True)
        scroll_cnc.pack(side="right", fill="y")

        def _on_mousewheel_cnc(event, c=canvas_cnc):
            c.yview_scroll(int(-1*(event.delta/120)), "units")
        f_tab_cnc.bind("<Enter>", lambda e, c=canvas_cnc, mw=_on_mousewheel_cnc: c.bind_all("<MouseWheel>", mw))
        f_tab_cnc.bind("<Leave>", lambda e, c=canvas_cnc: c.unbind_all("<MouseWheel>"))

        lf_cam = tk.LabelFrame(parent_cnc, text="3-Axis CNC CAM Settings")
        lf_cam.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(lf_cam, text="Tool Diameter (mm):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_cam, textvariable=self.cam_tool_dia, width=8).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(lf_cam, text="Material Thickness (mm):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_cam, textvariable=self.cam_mat_thick, width=8).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(lf_cam, text="Clearance / Safe Z (mm):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_cam, textvariable=self.cam_safe_z, width=8).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(lf_cam, text="Cut Feed Rate (mm/min):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_cam, textvariable=self.cam_feed_rate, width=8).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(lf_cam, text="Spindle Speed (RPM):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_cam, textvariable=self.cam_spindle_speed, width=8).grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(lf_cam, text="Extra Cut Depth (mm):").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_cam, textvariable=self.cam_extra_depth, width=8).grid(row=5, column=1, sticky="w", padx=5, pady=5)

        tk.Label(lf_cam, text="Milling Direction:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        dir_menu = tk.OptionMenu(lf_cam, self.cam_milling_dir, "Conventional (Outer CW)", "Climb (Outer CCW)")
        dir_menu.config(width=10)
        dir_menu.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        
        btn_frame = tk.Frame(lf_cam)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Load Tool Config", command=self.load_tool_config).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Tool Config", command=self.save_tool_config).pack(side="left", padx=5)

"""

new_content = content[:start_idx] + new_method + "\n" + content[end_idx:]

with open('ui/base_mode.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replaced create_cam_ui in ui/base_mode.py")

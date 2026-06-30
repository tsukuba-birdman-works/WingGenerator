import os
import tkinter as tk
from tkinter import filedialog
from utils.config import ConfigHelper

class BaseRibGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.init_cam_variables()

    def safe_float(self, var, default=0.0):
        try:
            val = var.get().strip()
            return float(val) if val else default
        except ValueError:
            return default

    def safe_int(self, var, default=0):
        try:
            val = var.get().strip()
            return int(val) if val else default
        except ValueError:
            return default

    def get_all_vars(self):
        # Base param_spec vars
        vars_dict = self.pm.get_all_vars() if hasattr(self, 'pm') else {}
        # Merge manual CAM vars
        if hasattr(self, 'get_cam_vars'):
            vars_dict.update(self.get_cam_vars())
        # Merge manual Stringer vars
        if hasattr(self, 'str_vars'):
            for name, d in self.str_vars.items():
                vars_dict[f"str_{name}_active"] = d['active']
                vars_dict[f"str_{name}_pos"] = d['pos']
                vars_dict[f"str_{name}_w"] = d['w']
                vars_dict[f"str_{name}_d"] = d['d']
                vars_dict[f"str_{name}_use_dxf"] = d['use_dxf']
                vars_dict[f"str_{name}_dxf"] = d['dxf']
        return vars_dict

    def get_stringers_data(self):
        data = []
        for name in ["A", "B", "C", "D", "E"]:
            if not self.str_vars[name]['active'].get() or not self.str_vars[name]['pos'].get().strip():
                continue
            try:
                data.append({
                    'pos': float(self.str_vars[name]['pos'].get().strip()),
                    'w': float(self.str_vars[name]['w'].get().strip() or "5.0"),
                    'd': float(self.str_vars[name]['d'].get().strip() or "4.0"),
                    'use_dxf': self.str_vars[name]['use_dxf'].get(),
                    'dxf_path': self.str_vars[name]['dxf'].get().strip()
                })
            except ValueError:
                continue
        return data

    def browse_file(self, var, is_dxf=False):
        ftypes = [("DXF Files", "*.dxf")] if is_dxf else [("DAT Files", "*.dat")]
        path = filedialog.askopenfilename(filetypes=ftypes)
        if path:
            var.set(path)

    def load_config(self):
        ConfigHelper.load_config(self)

    def save_config(self, mode_name):
        ConfigHelper.save_config(self, mode_name)

    def create_stringers_ui(self, parent_frame):
        tab = tk.LabelFrame(parent_frame, text='Stringers')
        tab.pack(fill=tk.X, padx=10, pady=5)
        headers = ["Act", "Pos(%)", "W(mm)", "D(mm)", "Use DXF", "DXF Path", ""]
        for col, h in enumerate(headers):
            tk.Label(tab, text=h, font=("Arial", 8)).grid(row=0, column=col, padx=2, pady=5)
        self.str_vars = {}
        for i, name in enumerate(["A", "B", "C", "D", "E"]):
            row = i + 1
            is_act = tk.BooleanVar(value=(name in ["A", "B"]))
            pos = tk.StringVar(value="-15.0" if name == "A" else ("60.0" if name == "B" else ""))
            w = tk.StringVar(value="5.0")
            d = tk.StringVar(value="4.0")
            use_dxf = tk.BooleanVar(value=False)
            dxf = tk.StringVar(value="")
            self.str_vars[name] = {'active': is_act, 'pos': pos, 'w': w, 'd': d, 'use_dxf': use_dxf, 'dxf': dxf}
            tk.Checkbutton(tab, text=name, variable=is_act).grid(row=row, column=0, sticky="w")
            tk.Entry(tab, textvariable=pos, width=6).grid(row=row, column=1, padx=2)
            tk.Entry(tab, textvariable=w, width=5).grid(row=row, column=2, padx=2)
            tk.Entry(tab, textvariable=d, width=5).grid(row=row, column=3, padx=2)
            tk.Checkbutton(tab, variable=use_dxf).grid(row=row, column=4)
            tk.Entry(tab, textvariable=dxf, width=8).grid(row=row, column=5, padx=2)
            tk.Button(tab, text="...", command=lambda v=dxf: self.browse_file(v, is_dxf=True)).grid(row=row, column=6, padx=2)

    def init_cam_variables(self):
        self.tabs_active = tk.BooleanVar(value=True)
        self.truss_tab_width = tk.StringVar(value="4.0")
        self.outer_tab_width = tk.StringVar(value="6.0")
        self.outer_tab_interval = tk.StringVar(value="100.0")
        self.tab_angle_deg = tk.StringVar(value="45.0")
        self.tab_exclusion_stringer = tk.StringVar(value="10.0")
        self.tab_exclusion_le_te = tk.StringVar(value="30.0")
        self.main_spar_support_w = tk.StringVar(value="2.0")
        self.main_spar_support_h = tk.StringVar(value="5.0")
        self.main_spar_support_thick = tk.StringVar(value="2.0")
        self.tab_thickness = tk.StringVar(value="3.0")
        self.spar_bridge_padding = tk.StringVar(value="10.0")
        self.spar_bridge_thickness = tk.StringVar(value="2.0")
        
        self.cam_tool_dia = tk.StringVar(value="2.0")
        self.cam_mat_thick = tk.StringVar(value="10.0")
        self.cam_safe_z = tk.StringVar(value="5.0")
        self.cam_feed_rate = tk.StringVar(value="2000")
        self.cam_spindle_speed = tk.StringVar(value="12000")
        self.cam_extra_depth = tk.StringVar(value="0.5")
        self.cam_milling_dir = tk.StringVar(value="Conventional (Outer CW)")

    def get_cam_vars(self):
        return {
            'tabs_active': self.tabs_active,
            'truss_tab_width': self.truss_tab_width,
            'outer_tab_width': getattr(self, 'outer_tab_width', self.truss_tab_width),
            'outer_tab_interval': getattr(self, 'outer_tab_interval', tk.StringVar(value="100.0")),
            'tab_angle_deg': getattr(self, 'tab_angle_deg', tk.StringVar(value="45.0")),
            'tab_exclusion_stringer': getattr(self, 'tab_exclusion_stringer', tk.StringVar(value="10.0")),
            'tab_exclusion_le_te': getattr(self, 'tab_exclusion_le_te', tk.StringVar(value="30.0")),
            'main_spar_support_w': self.main_spar_support_w,
            'main_spar_support_h': self.main_spar_support_h,
            'main_spar_support_thick': self.main_spar_support_thick,
            'tab_thickness': self.tab_thickness,
            'spar_bridge_padding': self.spar_bridge_padding,
            'spar_bridge_thickness': self.spar_bridge_thickness,
            'cam_tool_dia': self.cam_tool_dia,
            'cam_mat_thick': self.cam_mat_thick,
            'cam_safe_z': self.cam_safe_z,
            'cam_feed_rate': self.cam_feed_rate,
            'cam_spindle_speed': self.cam_spindle_speed,
            'cam_extra_depth': self.cam_extra_depth,
            'cam_milling_dir': self.cam_milling_dir
        }

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
        if hasattr(self, 'pm'):
            self.pm.obj.tabs_frames['CNC'] = parent_frame

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
        tab.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        left_panel = tk.Frame(tab)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Checkbutton(left_panel, text="Enable All Tabs", variable=self.tabs_active).pack(anchor="w", pady=(0, 5))
        
        lf_truss = tk.LabelFrame(left_panel, text="Holding Tabs")
        lf_truss.pack(fill=tk.X, pady=5)
        
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
        
        lf_main = tk.LabelFrame(left_panel, text="Main Spar E-Support")
        lf_main.pack(fill=tk.X, pady=5)
        tk.Label(lf_main, text="Leg Width (mm):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_main, textvariable=self.main_spar_support_w, width=8).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        tk.Label(lf_main, text="Lift Height (mm):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_main, textvariable=self.main_spar_support_h, width=8).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(lf_main, text="Snap Thickness Z (mm):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_main, textvariable=self.main_spar_support_thick, width=8).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        lf_fr = tk.LabelFrame(left_panel, text="F/R Spar Tabs")
        lf_fr.pack(fill=tk.X, pady=5)
        tk.Label(lf_fr, text="Bridge Padding (mm):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_fr, textvariable=self.spar_bridge_padding, width=8).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        tk.Label(lf_fr, text="Snap Thickness Z (mm):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lf_fr, textvariable=self.spar_bridge_thickness, width=8).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        
        lf_cam = tk.LabelFrame(tab, text="3-Axis CNC CAM Settings")
        lf_cam.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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


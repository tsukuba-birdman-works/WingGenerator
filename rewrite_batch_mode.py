with open("backup_batch_mode.py", "r") as f:
    lines = f.readlines()

def find_line(sub):
    for i, line in enumerate(lines):
        if line.startswith(sub): return i
    return -1

init_idx = find_line("    def __init__")
browse_idx = find_line("    def browse_file")

header = "".join(lines[:init_idx])
footer = "".join(lines[browse_idx:])

new_methods = """
    def __init__(self, root):
        super().__init__(root)
        from ui.param_spec import BATCH_PARAMS
        from ui.ui_builder import ParameterManager, UIBuilder
        self.pm = ParameterManager(self, BATCH_PARAMS)
        self.ui_builder = UIBuilder(self.pm)
        self.str_vars = {}
        for name in ["A", "B", "C", "D", "E"]:
            import tkinter as tk
            self.str_vars[name] = {'active': tk.BooleanVar(value=False), 'pos': tk.StringVar(), 'w': tk.StringVar(), 'd': tk.StringVar(), 'use_dxf': tk.BooleanVar(), 'dxf': tk.StringVar()}
        
        self.create_widgets()
        self.calculate_y_positions()

    def get_all_vars(self):
        v = self.pm.get_all_vars().copy()
        for name in ["A", "B", "C", "D", "E"]:
            for key in ['active', 'pos', 'w', 'd', 'use_dxf', 'dxf']:
                v[f'str_{name}_{key}'] = self.str_vars[name][key]
        if hasattr(self, 'get_cam_vars'):
            v.update(self.get_cam_vars())
        return v

    def save_config(self):
        super().save_config("Batch")

    def _get_builder_params(self):
        params = {}
        for p in self.pm.spec:
            vtype = p['type']
            var = self.pm.vars[p['id']]
            if vtype == 'bool': params[p['id']] = var.get()
            elif vtype == 'int': params[p['id']] = self.pm.safe_int(var, p['default'])
            elif vtype == 'float': params[p['id']] = self.pm.safe_float(var, p['default'])
            else: params[p['id']] = var.get().strip()
            
        params['stringers'] = []
        for name in ["A", "B", "C", "D", "E"]:
            try:
                params['stringers'].append({
                    'active': self.str_vars[name]['active'].get(),
                    'pos': float(self.str_vars[name]['pos'].get()),
                    'w': float(self.str_vars[name]['w'].get()),
                    'd': float(self.str_vars[name]['d'].get()),
                    'use_dxf': self.str_vars[name]['use_dxf'].get(),
                    'dxf_path': self.str_vars[name]['dxf'].get().strip()
                })
            except ValueError: continue
            
        try:
            params['connection_points'] = [
                (float(self.pm.vars['conn1_y'].get()), self.pm.vars['conn1_type'].get()),
                (float(self.pm.vars['conn2_y'].get()), self.pm.vars['conn2_type'].get()),
                (float(self.pm.vars['conn3_y'].get()), self.pm.vars['conn3_type'].get()),
                (float(self.pm.vars['conn4_y'].get()), self.pm.vars['conn4_type'].get()),
            ]
        except: params['connection_points'] = []
        
        params['xbrace_zones'] = [
            {'start': self.pm.safe_float(self.pm.vars['xb_start_a']), 'end': self.pm.safe_float(self.pm.vars['xb_end_a'])},
            {'start': self.pm.safe_float(self.pm.vars['xb_start_b']), 'end': self.pm.safe_float(self.pm.vars['xb_end_b'])},
            {'start': self.pm.safe_float(self.pm.vars['xb_start_c']), 'end': self.pm.safe_float(self.pm.vars['xb_end_c'])}
        ]
        
        if hasattr(self, 'truss_angles_dict'):
            params['truss_angles_dict'] = self.truss_angles_dict
            
        params['local_angle_var'] = self.pm.vars['local_angle_var'].get()
        return params

    def create_widgets(self):
        import tkinter as tk
        from tkinter import ttk
        
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Options Notebook
        left_frame = ttk.Frame(main_pane, width=450)
        main_pane.add(left_frame, weight=0)

        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.ui_builder.build_tabs(notebook, self.pm)
        
        # Append custom panels
        self.create_stringers_tab(notebook)
        if hasattr(self, 'create_cam_tab'):
            self.create_cam_tab(notebook)
            
        # Add Generate Positions button into Wing Tab
        if 'Wing' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['Wing'], text="Generate Positions", command=self.calculate_y_positions).pack(fill=tk.X, padx=10, pady=5)
        
        # Add Export Buttons to Export3D tab
        if 'Export3D' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['Export3D'], text="Export 3D Models (GLB)", command=self.export_obj).pack(fill=tk.X, padx=10, pady=5)
            ttk.Button(self.pm.obj.tabs_frames['Export3D'], text="Export Weight Report", command=self.open_weight_window).pack(fill=tk.X, padx=10, pady=5)
            
        # Add Load/Save config to top of left_frame
        f_top = ttk.Frame(left_frame)
        f_top.pack(fill=tk.X, side=tk.TOP, before=notebook)
        ttk.Button(f_top, text="Load Config", command=self.load_config).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(f_top, text="Save Config", command=self.save_config).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Right side: Preview
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)

        lf_preview = ttk.LabelFrame(right_frame, text="Rib Preview")
        lf_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        control_frame = ttk.Frame(lf_preview)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Select Rib:").pack(side=tk.LEFT, padx=5)
        self.rib_select_combo = ttk.Combobox(control_frame, state="readonly", width=40)
        self.rib_select_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.rib_select_combo.bind("<<ComboboxSelected>>", self.on_rib_select_fast)
        
        ttk.Button(control_frame, text="Generate ALL", command=lambda: self.update_preview_full()).pack(side=tk.LEFT, padx=5)
        
        angle_frame = ttk.Frame(lf_preview)
        angle_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(angle_frame, text="Local Angle Override:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(angle_frame, textvariable=self.pm.vars['local_angle_var'], width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(angle_frame, text="Apply Local Angle", command=self.apply_local_angle_full).pack(side=tk.LEFT, padx=5)
        
        self.fig_canvas_frame = ttk.Frame(lf_preview)
        self.fig_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas_widget = None
        
        for var in self.pm.vars.values():
            if hasattr(var, 'trace_add'):
                try: var.trace_add("write", lambda *args: self.update_preview_fast())
                except: pass

"""

with open("ui/batch_mode.py", "w") as f:
    f.write(header + new_methods + footer)

print("Rebuilt ui/batch_mode.py successfully with PanedWindow")

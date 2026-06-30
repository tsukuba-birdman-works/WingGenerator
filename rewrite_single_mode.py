import re
import ast

with open('backup_single_mode.py', 'r') as f:
    code = f.read()

# 1. Extract SINGLE_PARAMS
match = re.search(r'def get_all_vars\(self\):\s*v = \{(.*?)\}', code, re.DOTALL)
if match:
    dict_content = match.group(1)
    keys = re.findall(r"'([a-zA-Z0-9_]+)':", dict_content)
    
    single_params = []
    for key in keys:
        t = 'float'
        w = 'entry'
        if 'export_' in key or 'act' in key: t = 'bool'; w = 'checkbutton'
        if 'mat_' in key or 'type' in key or 'path' in key: t = 'str'; w = 'entry'
        
        # Tabs logic
        tab = 'Single'
        group = 'General'
        if 'file' in key: tab = 'Single'; group = 'Airfoils'
        if 'chord' in key or 'blend' in key: tab = 'Single'; group = 'Geometry'
        if 'spar' in key or 'bolt' in key: tab = 'Single'; group = 'Spars & Bolts'
        if 'truss' in key or 'margin' in key or 'beam' in key: tab = 'Single'; group = 'Truss'
        if 'cr_' in key: tab = 'Single'; group = 'Carbon Ribs'
        if 'plank' in key or 'te_' in key or 'rc' in key: tab = 'Single'; group = 'Plank & TE'
        if 'export_' in key: tab = 'Export'; group = 'Parts Output'
        if 'mat_' in key: tab = 'Export'; group = 'Materials'
        if 'cam_' in key or 'foam_' in key: tab = 'CNC'; group = 'CAM / Foam'
        if 'dxf_' in key: tab = 'DXF'; group = 'DXF Export'
        
        p = {'id': key, 'type': t, 'default': '' if t=='str' else (False if t=='bool' else 0.0), 'tab': tab, 'group': group, 'label': key, 'widget': w}
        single_params.append(p)
        
    with open('ui/param_spec.py', 'a') as f:
        f.write("\nSINGLE_PARAMS = [\n")
        for p in single_params:
            f.write(f"    {repr(p)},\n")
        f.write("]\n")

# 2. Rewrite single_mode.py
lines = code.split('\n')
def find_line(sub):
    for i, line in enumerate(lines):
        if line.startswith(sub): return i
    return -1

init_idx = find_line("    def __init__")
update_preview_idx = find_line("    def update_preview")

header = "\n".join(lines[:init_idx])
footer = "\n".join(lines[update_preview_idx:])

new_methods = """
    def __init__(self, root):
        super().__init__(root)
        from ui.param_spec import SINGLE_PARAMS
        from ui.ui_builder import ParameterManager, UIBuilder
        self.pm = ParameterManager(self, SINGLE_PARAMS)
        self.ui_builder = UIBuilder(self.pm)
        self.str_vars = {}
        for name in ["A", "B", "C", "D", "E"]:
            import tkinter as tk
            self.str_vars[name] = {'active': tk.BooleanVar(value=False), 'pos': tk.StringVar(), 'w': tk.StringVar(), 'd': tk.StringVar(), 'use_dxf': tk.BooleanVar(), 'dxf': tk.StringVar()}
        
        self.last_warnings = []
        self.is_updating_ui = False
        self.create_widgets()

    def get_all_vars(self):
        v = self.pm.get_all_vars().copy()
        for name in ["A", "B", "C", "D", "E"]:
            for key in ['active', 'pos', 'w', 'd', 'use_dxf', 'dxf']:
                v[f'str_{name}_{key}'] = self.str_vars[name][key]
        if hasattr(self, 'get_cam_vars'):
            v.update(self.get_cam_vars())
        return v

    def save_config(self):
        super().save_config("Single")

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
            
        params['is_single_mode'] = True
        return params

    def create_widgets(self):
        import tkinter as tk
        from tkinter import ttk
        
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(main_pane, width=450)
        main_pane.add(left_frame, weight=0)

        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.ui_builder.build_tabs(notebook, self.pm)
        
        self.create_stringers_tab(notebook)
        if hasattr(self, 'create_cam_tab'):
            self.create_cam_tab(notebook)
            
        if 'Export' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['Export'], text="Export 3D Model (GLB)", command=self.export_obj).pack(fill=tk.X, padx=10, pady=5)
            
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
        
        self.fig_canvas_frame = ttk.Frame(lf_preview)
        self.fig_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas_widget = None
        
        for var in self.pm.vars.values():
            if hasattr(var, 'trace_add'):
                try: var.trace_add("write", lambda *args: self.update_preview())
                except: pass

"""

# Remove old _get_builder_params and anything before update_preview
with open("ui/single_mode.py", "w") as f:
    f.write(header + "\n" + new_methods + "\n" + footer)


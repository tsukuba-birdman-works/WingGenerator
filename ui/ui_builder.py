import tkinter as tk
from tkinter import ttk, filedialog

class ParameterManager:
    def __init__(self, obj, param_spec):
        self.obj = obj
        self.spec = param_spec
        self.vars = {}
        for p in self.spec:
            vtype = p['type']
            def_val = p['default']
            if vtype == 'bool':
                var = tk.BooleanVar(value=bool(def_val))
            elif vtype == 'int':
                var = tk.IntVar(value=int(def_val) if def_val else 0)
            elif vtype == 'float':
                var = tk.StringVar(value=str(def_val) if def_val is not None else "")
            else:
                var = tk.StringVar(value=str(def_val).strip("'\"") if def_val else "")
            self.vars[p['id']] = var
            setattr(obj, p['id'], var)
            
    def get_all_vars(self):
        return self.vars

    def safe_float(self, var_or_val, fallback=0.0):
        if hasattr(var_or_val, 'get'):
            val = var_or_val.get()
        else:
            val = var_or_val
        try:
            return float(val)
        except (ValueError, TypeError):
            return fallback

    def safe_int(self, var_or_val, fallback=0):
        if hasattr(var_or_val, 'get'):
            val = var_or_val.get()
        else:
            val = var_or_val
        try:
            return int(val)
        except (ValueError, TypeError):
            return fallback

class UIBuilder:
    def __init__(self, param_manager):
        self.pm = param_manager

    def build_tabs(self, notebook, param_manager):
        spec = param_manager.spec
        obj = param_manager.obj
        
        # Group by tab -> group
        tabs_dict = {}
        for p in spec:
            tab = p.get('tab', 'Other')
            group = p.get('group', 'General')
            if tab not in tabs_dict:
                tabs_dict[tab] = {}
            if group not in tabs_dict[tab]:
                tabs_dict[tab][group] = []
            tabs_dict[tab][group].append(p)
            
        obj.tabs_frames = {}
        obj.groups_frames = {}
            
        for tab_name, groups in tabs_dict.items():
            if tab_name == "Unknown": continue
            f_tab_outer = ttk.Frame(notebook)
            notebook.add(f_tab_outer, text=tab_name)
            
            canvas = tk.Canvas(f_tab_outer, highlightthickness=0)
            scrollbar = ttk.Scrollbar(f_tab_outer, orient="vertical", command=canvas.yview)
            f_tab = ttk.Frame(canvas)

            f_tab.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0, 0), window=f_tab, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def _on_mousewheel(event, c=canvas):
                c.yview_scroll(int(-1*(event.delta/120)), "units")
            f_tab_outer.bind("<Enter>", lambda e, c=canvas, mw=_on_mousewheel: c.bind_all("<MouseWheel>", mw))
            f_tab_outer.bind("<Leave>", lambda e, c=canvas: c.unbind_all("<MouseWheel>"))

            obj.tabs_frames[tab_name] = f_tab
            
            row_idx = 0
            for group_name, params in groups.items():
                if group_name == "Unknown": continue
                lf = ttk.LabelFrame(f_tab, text=group_name)
                lf.pack(fill=tk.X, padx=10, pady=5)
                obj.groups_frames[group_name] = lf
                self.render_params(lf, [p['id'] for p in params])

    def render_params(self, parent_frame, param_ids, columns=2):
        r, c = 0, 0
        for pid in param_ids:
            p = next((x for x in self.pm.spec if x['id'] == pid), None)
            if not p: continue
            
            label = p.get('label', pid) + ":"
            wtype = p.get('widget', 'entry')
            var = self.pm.vars[pid]
            
            if wtype == 'checkbutton':
                ttk.Checkbutton(parent_frame, text=p.get('label', pid), variable=var).grid(row=r, column=c, columnspan=2, sticky=tk.W, padx=5, pady=2)
                c += 2
            if wtype == 'hidden':
                continue
            elif wtype == 'bolt_triple':
                linked_x = p.get('linked_x')
                linked_y = p.get('linked_y')
                var_x = self.pm.vars.get(linked_x)
                var_y = self.pm.vars.get(linked_y)
                ttk.Label(parent_frame, text=label).grid(row=r, column=c, sticky=tk.E, padx=5, pady=2)
                f_bolt = ttk.Frame(parent_frame)
                f_bolt.grid(row=r, column=c+1, sticky=tk.W, padx=5, pady=2)
                ttk.Label(f_bolt, text="D:").pack(side=tk.LEFT)
                ttk.Entry(f_bolt, textvariable=var, width=5).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(f_bolt, text="X:").pack(side=tk.LEFT)
                if var_x: ttk.Entry(f_bolt, textvariable=var_x, width=5).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(f_bolt, text="Y:").pack(side=tk.LEFT)
                if var_y: ttk.Entry(f_bolt, textvariable=var_y, width=5).pack(side=tk.LEFT)
                c += 2
            elif wtype == 'range_pair':
                linked_id = p.get('linked_id')
                linked_var = self.pm.vars.get(linked_id)
                ttk.Label(parent_frame, text=label).grid(row=r, column=c, sticky=tk.E, padx=5, pady=2)
                f_range = ttk.Frame(parent_frame)
                f_range.grid(row=r, column=c+1, sticky=tk.W, padx=5, pady=2)
                ttk.Entry(f_range, textvariable=var, width=6).pack(side=tk.LEFT)
                ttk.Label(f_range, text=" ~ ").pack(side=tk.LEFT)
                if linked_var:
                    ttk.Entry(f_range, textvariable=linked_var, width=6).pack(side=tk.LEFT)
                c += 2
            elif wtype == 'entry':
                ttk.Label(parent_frame, text=label).grid(row=r, column=c, sticky=tk.E, padx=5, pady=2)
                ttk.Entry(parent_frame, textvariable=var, width=10).grid(row=r, column=c+1, sticky=tk.W, padx=5, pady=2)
                c += 2
            elif wtype == 'combobox':
                default_opts = ['Styrofoam (Blue)', 'Carbon (Black)', 'Wood (Brown)', 'Kevlar (Yellow)', 'OPP Film (Clear)', 'Metal (Silver)']
                opts = p.get('values', default_opts)
                ttk.Label(parent_frame, text=label).grid(row=r, column=c, sticky=tk.E, padx=5, pady=2)
                ttk.Combobox(parent_frame, textvariable=var, values=opts, width=15).grid(row=r, column=c+1, sticky=tk.W, padx=5, pady=2)
                c += 2
            elif wtype == 'file':
                ttk.Label(parent_frame, text=label).grid(row=r, column=c, sticky=tk.E, padx=5, pady=2)
                f_file = ttk.Frame(parent_frame)
                f_file.grid(row=r, column=c+1, sticky=tk.EW, padx=5, pady=2)
                ttk.Entry(f_file, textvariable=var, width=15).pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Button(f_file, text="...", width=3, command=lambda v=var: self.browse_file(v)).pack(side=tk.LEFT)
                c += 2
            
            if c >= columns * 2:
                c = 0
                r += 1

    def browse_file(self, var, is_dxf=False):
        ftypes = [("DXF Files", "*.dxf")] if is_dxf else [("DAT Files", "*.dat")]
        path = filedialog.askopenfilename(filetypes=ftypes)
        if path:
            var.set(path)

import re

with open('ui/batch_mode.py', 'r') as f:
    content = f.read()

# 1. Fix Chord Root/Tip
chord_ui_old = """        ttk.Label(tab_wing, text="Chord (Root/Tip):").grid(row=row_idx, column=0, sticky=tk.W)
        fc = ttk.Frame(tab_wing); fc.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fc, textvariable=self.chord_root, width=8).pack(side=tk.LEFT)"""
chord_ui_new = """        ttk.Label(tab_wing, text="Chord (Root/Tip):").grid(row=row_idx, column=0, sticky=tk.W)
        fc = ttk.Frame(tab_wing); fc.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fc, textvariable=self.chord_root, width=8).pack(side=tk.LEFT)
        ttk.Label(fc, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(fc, textvariable=self.chord_tip, width=8).pack(side=tk.LEFT)"""
if chord_ui_old in content:
    content = content.replace(chord_ui_old, chord_ui_new)

# 2. Fix X-Brace variables initialization
xbrace_var_old = """        self.xbrace_y_start = getattr(self, 'xbrace_y_start', tk.StringVar(value=''))
        self.xbrace_y_end = getattr(self, 'xbrace_y_end', tk.StringVar(value=''))
        self.xbrace_pct = getattr(self, 'xbrace_pct', tk.StringVar(value=''))"""
xbrace_var_new = """        self.xb_start_a, self.xb_end_a = getattr(self, 'xb_start_a', tk.StringVar(value='429.5')), getattr(self, 'xb_end_a', tk.StringVar(value='1476'))
        self.xb_start_b, self.xb_end_b = getattr(self, 'xb_start_b', tk.StringVar(value='')), getattr(self, 'xb_end_b', tk.StringVar(value=''))
        self.xb_start_c, self.xb_end_c = getattr(self, 'xb_start_c', tk.StringVar(value='')), getattr(self, 'xb_end_c', tk.StringVar(value=''))"""
if xbrace_var_old in content:
    content = content.replace(xbrace_var_old, xbrace_var_new)

# 3. Fix X-Brace UI components
xbrace_ui_old = """        ttk.Label(tab_wing, text="Y Start / End:").grid(row=row_idx, column=0, sticky=tk.W)
        f_xb1 = ttk.Frame(tab_wing); f_xb1.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_xb1, textvariable=self.xbrace_y_start, width=6).pack(side=tk.LEFT)
        ttk.Label(f_xb1, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(f_xb1, textvariable=self.xbrace_y_end, width=6).pack(side=tk.LEFT)
        ttk.Button(f_xb1, text="Auto Set", command=self.auto_set_xbrace_zones).pack(side=tk.LEFT, padx=5)
        row_idx += 1
        ttk.Label(tab_wing, text="Chord Pos (%):").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_wing, textvariable=self.xbrace_pct, width=6).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1"""
xbrace_ui_new = """        ttk.Label(tab_wing, text="Zone 1 (Start/End):").grid(row=row_idx, column=0, sticky=tk.W)
        f_xb1 = ttk.Frame(tab_wing); f_xb1.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_xb1, textvariable=self.xb_start_a, width=6).pack(side=tk.LEFT)
        ttk.Label(f_xb1, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(f_xb1, textvariable=self.xb_end_a, width=6).pack(side=tk.LEFT)
        ttk.Button(f_xb1, text="Auto Set", command=self.auto_set_xbrace_zones).pack(side=tk.LEFT, padx=5)
        row_idx += 1
        ttk.Label(tab_wing, text="Zone 2 (Start/End):").grid(row=row_idx, column=0, sticky=tk.W)
        f_xb2 = ttk.Frame(tab_wing); f_xb2.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_xb2, textvariable=self.xb_start_b, width=6).pack(side=tk.LEFT)
        ttk.Label(f_xb2, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(f_xb2, textvariable=self.xb_end_b, width=6).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_wing, text="Zone 3 (Start/End):").grid(row=row_idx, column=0, sticky=tk.W)
        f_xb3 = ttk.Frame(tab_wing); f_xb3.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_xb3, textvariable=self.xb_start_c, width=6).pack(side=tk.LEFT)
        ttk.Label(f_xb3, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(f_xb3, textvariable=self.xb_end_c, width=6).pack(side=tk.LEFT)
        row_idx += 1"""
if xbrace_ui_old in content:
    content = content.replace(xbrace_ui_old, xbrace_ui_new)

# 4. Fix _get_builder_params to extract 3 zones without offset
get_params_old = """        # X-Brace Zones
        xb_zones = []
        try:
            s_str, e_str, o_str = self.xbrace_y_start.get().strip(), self.xbrace_y_end.get().strip(), "0.0"
            if s_str and e_str:
                xb_zones.append((float(s_str), float(e_str), float(o_str)))
        except Exception:
            pass"""
get_params_new = """        # X-Brace Zones
        xb_zones = []
        for s_var, e_var in [(self.xb_start_a, self.xb_end_a), (self.xb_start_b, self.xb_end_b), (self.xb_start_c, self.xb_end_c)]:
            try:
                s_str, e_str = s_var.get().strip(), e_var.get().strip()
                if s_str and e_str:
                    xb_zones.append((float(s_str), float(e_str), 0.0))  # No offset in batch mode
            except Exception:
                pass"""
if get_params_old in content:
    content = content.replace(get_params_old, get_params_new)

with open('ui/batch_mode.py', 'w') as f:
    f.write(content)

print("Patch applied to batch_mode.py")

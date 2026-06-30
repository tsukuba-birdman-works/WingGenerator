import re

with open("ui/single_mode.py", "r") as f:
    content = f.read()

# 1. Add variable definitions
var_defs = """        self.rib_thick = tk.StringVar(value="3.0")
        
        self.main_spar_inner_dia = tk.StringVar(value="105.0")
        self.front_spar_inner_dia = tk.StringVar(value="8.0")
        self.rear_spar_inner_dia = tk.StringVar(value="11.4")
        self.xbrace_inner_dia = tk.StringVar(value="28.0")
        self.diag1_inner_dia = tk.StringVar(value="8.0")
        self.diag2_inner_dia = tk.StringVar(value="8.0")
        self.bolt_spacer_inner_dia = tk.StringVar(value="3.0")
        self.bolt_spacer_length = tk.StringVar(value="10.0")"""
content = content.replace('        self.rib_thick = tk.StringVar(value="3.0")', var_defs)

# 2. Add to get_all_vars
var_returns = """            'rib_thick': self.rib_thick,
            'main_spar_inner_dia': self.main_spar_inner_dia, 'front_spar_inner_dia': self.front_spar_inner_dia, 'rear_spar_inner_dia': self.rear_spar_inner_dia,
            'xbrace_inner_dia': self.xbrace_inner_dia, 'diag1_inner_dia': self.diag1_inner_dia, 'diag2_inner_dia': self.diag2_inner_dia,
            'bolt_spacer_inner_dia': self.bolt_spacer_inner_dia, 'bolt_spacer_length': self.bolt_spacer_length,"""
content = content.replace("            'rib_thick': self.rib_thick", var_returns)

# 3. Add to UI
ui_adds = """        self.create_cam_tab(notebook)

        tab_pipes = tk.Frame(notebook)
        notebook.add(tab_pipes, text="3D Pipes & Spacers")
        tk.Label(tab_pipes, text="These settings are used only for 3D Export (OBJ)", font=("Arial", 9, "italic")).grid(row=0, column=0, columnspan=2, pady=5)
        
        row_p = 1
        tk.Label(tab_pipes, text="Main Spar Inner Dia (mm):").grid(row=row_p, column=0, sticky="e", padx=5, pady=2); tk.Entry(tab_pipes, textvariable=self.main_spar_inner_dia, width=8).grid(row=row_p, column=1, sticky="w", padx=5, pady=2); row_p+=1
        tk.Label(tab_pipes, text="Front Spar Inner Dia:").grid(row=row_p, column=0, sticky="e", padx=5, pady=2); tk.Entry(tab_pipes, textvariable=self.front_spar_inner_dia, width=8).grid(row=row_p, column=1, sticky="w", padx=5, pady=2); row_p+=1
        tk.Label(tab_pipes, text="Rear Spar Inner Dia:").grid(row=row_p, column=0, sticky="e", padx=5, pady=2); tk.Entry(tab_pipes, textvariable=self.rear_spar_inner_dia, width=8).grid(row=row_p, column=1, sticky="w", padx=5, pady=2); row_p+=1
        tk.Label(tab_pipes, text="X-Brace Inner Dia:").grid(row=row_p, column=0, sticky="e", padx=5, pady=2); tk.Entry(tab_pipes, textvariable=self.xbrace_inner_dia, width=8).grid(row=row_p, column=1, sticky="w", padx=5, pady=2); row_p+=1
        tk.Label(tab_pipes, text="Diag 1 Inner Dia:").grid(row=row_p, column=0, sticky="e", padx=5, pady=2); tk.Entry(tab_pipes, textvariable=self.diag1_inner_dia, width=8).grid(row=row_p, column=1, sticky="w", padx=5, pady=2); row_p+=1
        tk.Label(tab_pipes, text="Diag 2 Inner Dia:").grid(row=row_p, column=0, sticky="e", padx=5, pady=2); tk.Entry(tab_pipes, textvariable=self.diag2_inner_dia, width=8).grid(row=row_p, column=1, sticky="w", padx=5, pady=2); row_p+=1
        
        import tkinter.ttk as ttk
        ttk.Separator(tab_pipes, orient='horizontal').grid(row=row_p, column=0, columnspan=2, sticky="ew", pady=5); row_p+=1
        tk.Label(tab_pipes, text="Bolt Spacer Inner Dia:").grid(row=row_p, column=0, sticky="e", padx=5, pady=2); tk.Entry(tab_pipes, textvariable=self.bolt_spacer_inner_dia, width=8).grid(row=row_p, column=1, sticky="w", padx=5, pady=2); row_p+=1
        tk.Label(tab_pipes, text="Bolt Spacer Length:").grid(row=row_p, column=0, sticky="e", padx=5, pady=2); tk.Entry(tab_pipes, textvariable=self.bolt_spacer_length, width=8).grid(row=row_p, column=1, sticky="w", padx=5, pady=2); row_p+=1

        btn_frame = tk.Frame(self.root)"""
content = content.replace("        self.create_cam_tab(notebook)\n\n        btn_frame = tk.Frame(self.root)", ui_adds)

# 4. Add to get_params()
params_update = """            'main_spar_inner_dia': self.safe_float(self.main_spar_inner_dia),
            'front_spar_inner_dia': self.safe_float(self.front_spar_inner_dia),
            'rear_spar_inner_dia': self.safe_float(self.rear_spar_inner_dia),
            'xbrace_inner_dia': self.safe_float(self.xbrace_inner_dia),
            'diag1_inner_dia': self.safe_float(self.diag1_inner_dia),
            'diag2_inner_dia': self.safe_float(self.diag2_inner_dia),
            'bolt_spacer_inner_dia': self.safe_float(self.bolt_spacer_inner_dia),
            'bolt_spacer_length': self.safe_float(self.bolt_spacer_length),
            'cam_tool_dia':"""
content = content.replace("            'cam_tool_dia':", params_update)

with open("ui/single_mode.py", "w") as f:
    f.write(content)

print("Patch applied to ui/single_mode.py")

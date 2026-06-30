import re
import os

filepath = 'ui/batch_mode.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Variables to init
var_init = """
        # --- Restored Variables ---
        self.rib_interval = getattr(self, 'rib_interval', tk.StringVar(value="50.0"))
        self.plank_part_start = getattr(self, 'plank_part_start', tk.StringVar(value="0.0"))
        self.plank_part_end = getattr(self, 'plank_part_end', tk.StringVar(value="100.0"))
        self.te_cap_ur_act = getattr(self, 'te_cap_ur_act', tk.BooleanVar(value=False))
        self.te_cap_lr_act = getattr(self, 'te_cap_lr_act', tk.BooleanVar(value=False))
        self.te_cap_thick = getattr(self, 'te_cap_thick', tk.StringVar(value="1.0"))
        self.te_cap_ur_w = getattr(self, 'te_cap_ur_w', tk.StringVar(value="0.0"))
        self.te_cap_lr_w = getattr(self, 'te_cap_lr_w', tk.StringVar(value="0.0"))
        self.rc1_act = getattr(self, 'rc1_act', tk.BooleanVar(value=False))
        self.rc1_start = getattr(self, 'rc1_start', tk.StringVar(value="0.0"))
        self.rc1_end = getattr(self, 'rc1_end', tk.StringVar(value="30.0"))
        self.rc1_width = getattr(self, 'rc1_width', tk.StringVar(value="5.0"))
        self.rc1_thick = getattr(self, 'rc1_thick', tk.StringVar(value="1.0"))
        self.rc2_act = getattr(self, 'rc2_act', tk.BooleanVar(value=False))
        self.rc2_start = getattr(self, 'rc2_start', tk.StringVar(value="70.0"))
        self.rc2_end = getattr(self, 'rc2_end', tk.StringVar(value="100.0"))
        self.rc2_width = getattr(self, 'rc2_width', tk.StringVar(value="5.0"))
        self.rc2_thick = getattr(self, 'rc2_thick', tk.StringVar(value="1.0"))
        self.cr_root_in_act = getattr(self, 'cr_root_in_act', tk.BooleanVar(value=False))
        self.cr_root_in_te = getattr(self, 'cr_root_in_te', tk.BooleanVar(value=True))
        self.cr_root_out_act = getattr(self, 'cr_root_out_act', tk.BooleanVar(value=False))
        self.cr_root_out_te = getattr(self, 'cr_root_out_te', tk.BooleanVar(value=True))
        self.cr_tip_in_act = getattr(self, 'cr_tip_in_act', tk.BooleanVar(value=False))
        self.cr_tip_in_te = getattr(self, 'cr_tip_in_te', tk.BooleanVar(value=True))
        self.cr_tip_out_act = getattr(self, 'cr_tip_out_act', tk.BooleanVar(value=False))
        self.cr_tip_out_te = getattr(self, 'cr_tip_out_te', tk.BooleanVar(value=True))
        self.cr_thick = getattr(self, 'cr_thick', tk.StringVar(value="2.0"))
        self.margin_outer_edge = getattr(self, 'margin_outer_edge', tk.StringVar(value="2.0"))
        self.local_truss_angle = getattr(self, 'local_truss_angle', tk.StringVar(value="0.0"))
        self.root_bolt1_dx = getattr(self, 'root_bolt1_dx', tk.StringVar(value="0.0"))
        self.root_bolt1_dy = getattr(self, 'root_bolt1_dy', tk.StringVar(value="0.0"))
        self.root_bolt1_dia = getattr(self, 'root_bolt1_dia', tk.StringVar(value="0.0"))
        self.root_bolt2_dx = getattr(self, 'root_bolt2_dx', tk.StringVar(value="0.0"))
        self.root_bolt2_dy = getattr(self, 'root_bolt2_dy', tk.StringVar(value="0.0"))
        self.root_bolt2_dia = getattr(self, 'root_bolt2_dia', tk.StringVar(value="0.0"))
        self.tip_bolt1_dx = getattr(self, 'tip_bolt1_dx', tk.StringVar(value="0.0"))
        self.tip_bolt1_dy = getattr(self, 'tip_bolt1_dy', tk.StringVar(value="0.0"))
        self.tip_bolt1_dia = getattr(self, 'tip_bolt1_dia', tk.StringVar(value="0.0"))
        self.tip_bolt2_dx = getattr(self, 'tip_bolt2_dx', tk.StringVar(value="0.0"))
        self.tip_bolt2_dy = getattr(self, 'tip_bolt2_dy', tk.StringVar(value="0.0"))
        self.tip_bolt2_dia = getattr(self, 'tip_bolt2_dia', tk.StringVar(value="0.0"))
        self.spar_pos_tip = getattr(self, 'spar_pos_tip', tk.StringVar(value="30.0"))
        self.export_carbon_ribs = getattr(self, 'export_carbon_ribs', tk.BooleanVar(value=True))
        self.export_main_spar = getattr(self, 'export_main_spar', tk.BooleanVar(value=True))
        self.export_front_spar = getattr(self, 'export_front_spar', tk.BooleanVar(value=True))
        self.export_rear_spar = getattr(self, 'export_rear_spar', tk.BooleanVar(value=True))
        self.export_plank = getattr(self, 'export_plank', tk.BooleanVar(value=True))
        self.export_te = getattr(self, 'export_te', tk.BooleanVar(value=True))
        self.export_connectors = getattr(self, 'export_connectors', tk.BooleanVar(value=True))
        self.export_stringers = getattr(self, 'export_stringers', tk.BooleanVar(value=True))
        self.export_xbrace_wires = getattr(self, 'export_xbrace_wires', tk.BooleanVar(value=True))
        self.export_diag_spars = getattr(self, 'export_diag_spars', tk.BooleanVar(value=True))
        self.export_te_caps = getattr(self, 'export_te_caps', tk.BooleanVar(value=True))
        self.export_rib_caps = getattr(self, 'export_rib_caps', tk.BooleanVar(value=True))
        self.export_film = getattr(self, 'export_film', tk.BooleanVar(value=True))
"""
if "self.margin_outer_edge" not in content:
    content = content.replace("super().__init__(root)", "super().__init__(root)\n" + var_init)


# 2. UI Wing
wing_target = 'ttk.Entry(fc, textvariable=self.chord_root, width=8).pack(side=tk.LEFT)'
wing_inj = """ttk.Entry(fc, textvariable=self.chord_root, width=8).pack(side=tk.LEFT)
        ttk.Entry(fc, textvariable=self.chord_tip, width=8).pack(side=tk.LEFT); row_idx += 1

        ttk.Label(tab_wing, text="Rib Interval (mm):").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_wing, textvariable=self.rib_interval, width=8).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1

        ttk.Label(tab_wing, text="Carbon Ribs (Sandwich):", font=("", 9, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W, pady=(10, 0)); row_idx += 1
        f_cr = ttk.Frame(tab_wing); f_cr.grid(row=row_idx, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(f_cr, text="Root In", variable=self.cr_root_in_act).pack(side=tk.LEFT)
        ttk.Checkbutton(f_cr, text="TE Cut", variable=self.cr_root_in_te).pack(side=tk.LEFT)
        ttk.Checkbutton(f_cr, text="Root Out", variable=self.cr_root_out_act).pack(side=tk.LEFT)
        ttk.Checkbutton(f_cr, text="TE Cut", variable=self.cr_root_out_te).pack(side=tk.LEFT)
        row_idx += 1
        f_cr2 = ttk.Frame(tab_wing); f_cr2.grid(row=row_idx, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(f_cr2, text="Tip In", variable=self.cr_tip_in_act).pack(side=tk.LEFT)
        ttk.Checkbutton(f_cr2, text="TE Cut", variable=self.cr_tip_in_te).pack(side=tk.LEFT)
        ttk.Checkbutton(f_cr2, text="Tip Out", variable=self.cr_tip_out_act).pack(side=tk.LEFT)
        ttk.Checkbutton(f_cr2, text="TE Cut", variable=self.cr_tip_out_te).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_wing, text="Carbon Rib Thick:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_wing, textvariable=self.cr_thick, width=8).grid(row=row_idx, column=1, sticky=tk.W)
"""
if "Carbon Ribs (Sandwich)" not in content:
    content = content.replace(wing_target + '\n        ttk.Entry(fc, textvariable=self.chord_tip, width=8).pack(side=tk.LEFT)', wing_inj)


# 3. UI Spar
spar_target = 'ttk.Entry(f_r, textvariable=self.rear_spar_dia, width=5).pack(side=tk.LEFT)'
spar_inj = """ttk.Entry(f_r, textvariable=self.rear_spar_dia, width=5).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_spar, text="Tip Spar Pos (%):").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_spar, textvariable=self.spar_pos_tip, width=8).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1

        ttk.Label(tab_spar, text="Root Bolt 1 dX/dY/Dia:").grid(row=row_idx, column=0, sticky=tk.W)
        f_b1 = ttk.Frame(tab_spar); f_b1.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_b1, textvariable=self.root_bolt1_dx, width=5).pack(side=tk.LEFT)
        ttk.Entry(f_b1, textvariable=self.root_bolt1_dy, width=5).pack(side=tk.LEFT)
        ttk.Entry(f_b1, textvariable=self.root_bolt1_dia, width=5).pack(side=tk.LEFT); row_idx += 1
        
        ttk.Label(tab_spar, text="Root Bolt 2 dX/dY/Dia:").grid(row=row_idx, column=0, sticky=tk.W)
        f_b2 = ttk.Frame(tab_spar); f_b2.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_b2, textvariable=self.root_bolt2_dx, width=5).pack(side=tk.LEFT)
        ttk.Entry(f_b2, textvariable=self.root_bolt2_dy, width=5).pack(side=tk.LEFT)
        ttk.Entry(f_b2, textvariable=self.root_bolt2_dia, width=5).pack(side=tk.LEFT); row_idx += 1

        ttk.Label(tab_spar, text="Tip Bolt 1 dX/dY/Dia:").grid(row=row_idx, column=0, sticky=tk.W)
        f_b3 = ttk.Frame(tab_spar); f_b3.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_b3, textvariable=self.tip_bolt1_dx, width=5).pack(side=tk.LEFT)
        ttk.Entry(f_b3, textvariable=self.tip_bolt1_dy, width=5).pack(side=tk.LEFT)
        ttk.Entry(f_b3, textvariable=self.tip_bolt1_dia, width=5).pack(side=tk.LEFT); row_idx += 1

        ttk.Label(tab_spar, text="Tip Bolt 2 dX/dY/Dia:").grid(row=row_idx, column=0, sticky=tk.W)
        f_b4 = ttk.Frame(tab_spar); f_b4.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_b4, textvariable=self.tip_bolt2_dx, width=5).pack(side=tk.LEFT)
        ttk.Entry(f_b4, textvariable=self.tip_bolt2_dy, width=5).pack(side=tk.LEFT)
        ttk.Entry(f_b4, textvariable=self.tip_bolt2_dia, width=5).pack(side=tk.LEFT)
"""
if "Tip Bolt 2" not in content:
    content = content.replace(spar_target, spar_inj)

# 4. UI Rib
rib_target = 'ttk.Entry(tab_rib, textvariable=self.truss_fillet, width=8).grid(row=row_idx, column=1, sticky=tk.W)'
rib_inj = """ttk.Entry(tab_rib, textvariable=self.truss_fillet, width=8).grid(row=row_idx, column=1, sticky=tk.W)
        row_idx += 1
        ttk.Label(tab_rib, text="Margin Outer (Norm/Edge):").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_rib, textvariable=self.margin_outer_edge, width=8).grid(row=row_idx, column=1, sticky=tk.W)
"""
if "Margin Outer" not in content:
    content = content.replace(rib_target, rib_inj)


# 5. UI Plank
plank_target = 'ttk.Label(f_te2, text="D:").pack(side=tk.LEFT); ttk.Entry(f_te2, textvariable=self.te_cap_lf_d, width=4).pack(side=tk.LEFT)'
plank_inj = """ttk.Label(f_te2, text="D:").pack(side=tk.LEFT); ttk.Entry(f_te2, textvariable=self.te_cap_lf_d, width=4).pack(side=tk.LEFT)
        row_idx += 1

        ttk.Label(tab_plank, text="Plank Part Start/End (%):").grid(row=row_idx, column=0, sticky=tk.W)
        f_p1 = ttk.Frame(tab_plank); f_p1.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_p1, textvariable=self.plank_part_start, width=6).pack(side=tk.LEFT)
        ttk.Entry(f_p1, textvariable=self.plank_part_end, width=6).pack(side=tk.LEFT); row_idx += 1

        ttk.Label(tab_plank, text="TE Caps Rear (U/L):").grid(row=row_idx, column=0, sticky=tk.W)
        f_te3 = ttk.Frame(tab_plank); f_te3.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Checkbutton(f_te3, text="Upper", variable=self.te_cap_ur_act).pack(side=tk.LEFT)
        ttk.Label(f_te3, text="W:").pack(side=tk.LEFT); ttk.Entry(f_te3, textvariable=self.te_cap_ur_w, width=4).pack(side=tk.LEFT)
        ttk.Checkbutton(f_te3, text="Lower", variable=self.te_cap_lr_act).pack(side=tk.LEFT)
        ttk.Label(f_te3, text="W:").pack(side=tk.LEFT); ttk.Entry(f_te3, textvariable=self.te_cap_lr_w, width=4).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_plank, text="TE Caps Thick (mm):").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_plank, textvariable=self.te_cap_thick, width=6).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1

        ttk.Label(tab_plank, text="Rib Caps 1 (S/E/W/T):").grid(row=row_idx, column=0, sticky=tk.W)
        f_rc1 = ttk.Frame(tab_plank); f_rc1.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Checkbutton(f_rc1, variable=self.rc1_act).pack(side=tk.LEFT)
        ttk.Entry(f_rc1, textvariable=self.rc1_start, width=4).pack(side=tk.LEFT)
        ttk.Entry(f_rc1, textvariable=self.rc1_end, width=4).pack(side=tk.LEFT)
        ttk.Entry(f_rc1, textvariable=self.rc1_width, width=4).pack(side=tk.LEFT)
        ttk.Entry(f_rc1, textvariable=self.rc1_thick, width=4).pack(side=tk.LEFT); row_idx += 1

        ttk.Label(tab_plank, text="Rib Caps 2 (S/E/W/T):").grid(row=row_idx, column=0, sticky=tk.W)
        f_rc2 = ttk.Frame(tab_plank); f_rc2.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Checkbutton(f_rc2, variable=self.rc2_act).pack(side=tk.LEFT)
        ttk.Entry(f_rc2, textvariable=self.rc2_start, width=4).pack(side=tk.LEFT)
        ttk.Entry(f_rc2, textvariable=self.rc2_end, width=4).pack(side=tk.LEFT)
        ttk.Entry(f_rc2, textvariable=self.rc2_width, width=4).pack(side=tk.LEFT)
        ttk.Entry(f_rc2, textvariable=self.rc2_thick, width=4).pack(side=tk.LEFT)
"""
if "Rib Caps 1" not in content:
    content = content.replace(plank_target, plank_inj)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Batch mode patched")

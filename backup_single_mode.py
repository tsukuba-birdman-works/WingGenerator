import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.engine import RibGeneratorEngine, RibParameters, RibGenerationResult
from utils.config import ConfigHelper
from core.export_3d import Wing3DExporter
from ui.base_mode import BaseRibGeneratorGUI

# ==========================================
# 単一リブモードGUI
# ==========================================
class RibGeneratorGUI_Single(BaseRibGeneratorGUI):
    def __init__(self, root):
        BaseRibGeneratorGUI.__init__(self, root)
        self.root = root

        # --- Restored Variables ---
        self.rib_interval = tk.StringVar(value="50.0")
        self.plank_part_start = tk.StringVar(value="0.0")
        self.plank_part_end = tk.StringVar(value="100.0")
        self.te_cap_ur_act = tk.BooleanVar(value=False)
        self.te_cap_lr_act = tk.BooleanVar(value=False)
        self.te_cap_thick = tk.StringVar(value="1.0")
        self.te_cap_ur_w = tk.StringVar(value="0.0")
        self.te_cap_lr_w = tk.StringVar(value="0.0")
        self.rc1_act = tk.BooleanVar(value=False)
        self.rc1_start = tk.StringVar(value="0.0")
        self.rc1_end = tk.StringVar(value="30.0")
        self.rc1_width = tk.StringVar(value="5.0")
        self.rc1_thick = tk.StringVar(value="1.0")
        self.rc2_act = tk.BooleanVar(value=False)
        self.rc2_start = tk.StringVar(value="70.0")
        self.rc2_end = tk.StringVar(value="100.0")
        self.rc2_width = tk.StringVar(value="5.0")
        self.rc2_thick = tk.StringVar(value="1.0")
        self.cr_root_in_act = tk.BooleanVar(value=False)
        self.cr_root_in_te = tk.BooleanVar(value=True)
        self.cr_root_out_act = tk.BooleanVar(value=False)
        self.cr_root_out_te = tk.BooleanVar(value=True)
        self.cr_tip_in_act = tk.BooleanVar(value=False)
        self.cr_tip_in_te = tk.BooleanVar(value=True)
        self.cr_tip_out_act = tk.BooleanVar(value=False)
        self.cr_tip_out_te = tk.BooleanVar(value=True)
        self.cr_thick = tk.StringVar(value="2.0")
        self.margin_outer_edge = tk.StringVar(value="2.0")
        self.local_truss_angle = tk.StringVar(value="0.0")
        self.root_bolt1_dx = tk.StringVar(value="0.0")
        self.root_bolt1_dy = tk.StringVar(value="0.0")
        self.root_bolt1_dia = tk.StringVar(value="0.0")
        self.root_bolt2_dx = tk.StringVar(value="0.0")
        self.root_bolt2_dy = tk.StringVar(value="0.0")
        self.root_bolt2_dia = tk.StringVar(value="0.0")
        self.tip_bolt1_dx = tk.StringVar(value="0.0")
        self.tip_bolt1_dy = tk.StringVar(value="0.0")
        self.tip_bolt1_dia = tk.StringVar(value="0.0")
        self.tip_bolt2_dx = tk.StringVar(value="0.0")
        self.tip_bolt2_dy = tk.StringVar(value="0.0")
        self.tip_bolt2_dia = tk.StringVar(value="0.0")
        self.spar_pos_tip = tk.StringVar(value="30.0")
        self.export_carbon_ribs = tk.BooleanVar(value=True)
        self.export_main_spar = tk.BooleanVar(value=True)
        self.export_front_spar = tk.BooleanVar(value=True)
        self.export_rear_spar = tk.BooleanVar(value=True)
        self.export_plank = tk.BooleanVar(value=True)
        self.export_te = tk.BooleanVar(value=True)
        self.export_connectors = tk.BooleanVar(value=True)
        self.export_stringers = tk.BooleanVar(value=True)
        self.export_xbrace_wires = tk.BooleanVar(value=True)
        self.export_diag_spars = tk.BooleanVar(value=True)
        self.export_te_caps = tk.BooleanVar(value=True)
        self.export_rib_caps = tk.BooleanVar(value=True)
        self.export_film = tk.BooleanVar(value=True)

        self.root.title("Rib Generator (Single Mode)")
        self.root.geometry("1100x880") 
        self.engine = RibGeneratorEngine()
        
        self.file1_path, self.file2_path = tk.StringVar(), tk.StringVar()
        self.blend_ratio_pct, self.chord_length = tk.StringVar(value="100.0"), tk.StringVar(value="1050.0")
        self.spar_pos_pct, self.spar_hole_dia = tk.StringVar(value="41.4"), tk.StringVar(value="107.0")
        self.front_spar_dx, self.front_spar_dy, self.front_spar_dia = tk.StringVar(value="-330.0"), tk.StringVar(value="-30.0"), tk.StringVar(value="10.0")
        self.rear_spar_dx, self.rear_spar_dy, self.rear_spar_dia = tk.StringVar(value="400.0"), tk.StringVar(value="-28.0"), tk.StringVar(value="13.4")
        self.plank_start, self.plank_end, self.plank_thick = tk.StringVar(value="-15.0"), tk.StringVar(value="60.0"), tk.StringVar(value="3.0")
        self.plank_part_start, self.plank_part_end = tk.StringVar(value="-15.0"), tk.StringVar(value="60.0")
        self.te_cut, self.washout_deg = tk.StringVar(value="0.0"), tk.StringVar(value="0.0")

        self.truss_angle, self.truss_front_n, self.truss_rear_n = tk.StringVar(value="60.0"), tk.StringVar(value="3"), tk.StringVar(value="5")
        self.beam_width, self.margin_spar, self.margin_bolt = tk.StringVar(value="6.0"), tk.StringVar(value="8.0"), tk.StringVar(value="8.0")
        self.margin_outer, self.truss_fillet, self.min_hole_dia = tk.StringVar(value="8.0"), tk.StringVar(value="5.0"), tk.StringVar(value="3.0")
        self.xbrace_pct, self.xbrace_dia = tk.StringVar(value="20.0"), tk.StringVar(value="6.0")

        self.safe_margin_var = tk.BooleanVar(value=True)
        self.bolt1_dx, self.bolt1_dy, self.bolt1_dia = tk.StringVar(value="0.0"), tk.StringVar(value="0.0"), tk.StringVar(value="6.0")
        self.bolt2_dx, self.bolt2_dy, self.bolt2_dia = tk.StringVar(value="0.0"), tk.StringVar(value="0.0"), tk.StringVar(value="6.0")
        
        self.te_cap_uf_act = tk.BooleanVar(value=False)
        self.te_cap_uf_w = tk.StringVar(value="5.0")
        self.te_cap_ur_act = tk.BooleanVar(value=False)
        self.te_cap_ur_w = tk.StringVar(value="5.0")
        self.te_cap_lf_act = tk.BooleanVar(value=False)
        self.te_cap_lf_w = tk.StringVar(value="5.0")
        self.te_cap_lr_act = tk.BooleanVar(value=False)
        self.te_cap_lr_w = tk.StringVar(value="5.0")
        self.te_cap_thick = tk.StringVar(value="1.0")
        
        self.rc1_act = tk.BooleanVar(value=False)
        self.rc1_start = tk.StringVar(value="-15.0")
        self.rc1_end = tk.StringVar(value="60.0")
        self.rc1_thick = tk.StringVar(value="1.0")
        self.rc1_width = tk.StringVar(value="5.0")
        
        self.rc2_act = tk.BooleanVar(value=False)
        self.rc2_start = tk.StringVar(value="60.0")
        self.rc2_end = tk.StringVar(value="90.0")
        self.rc2_thick = tk.StringVar(value="1.0")
        self.rc2_width = tk.StringVar(value="5.0")
        
        self.diag1_active = tk.BooleanVar(value=False)
        self.diag1_t1, self.diag1_t2 = tk.StringVar(value="0.0"), tk.StringVar(value="100.0")
        self.diag2_active = tk.BooleanVar(value=False)
        self.diag2_t1, self.diag2_t2 = tk.StringVar(value="0.0"), tk.StringVar(value="100.0")
        self.rib_thick = tk.StringVar(value="3.0")
        
        self.main_spar_inner_dia = tk.StringVar(value="105.0")
        self.front_spar_inner_dia = tk.StringVar(value="8.0")
        self.rear_spar_inner_dia = tk.StringVar(value="11.4")
        self.xbrace_wire_dia = tk.StringVar(value="28.0")
        self.bolt_spacer_inner_dia = tk.StringVar(value="4.0")
        self.bolt_spacer_length = tk.StringVar(value="10.0")

        self.last_warnings = []
        self.is_updating_ui = False
        self.create_widgets()

    def get_all_vars(self):
        v = {
            'file1_path': self.file1_path, 'file2_path': self.file2_path,
            'blend_ratio_pct': self.blend_ratio_pct, 'chord_length': self.chord_length,
            'spar_pos_pct': self.spar_pos_pct, 'spar_hole_dia': self.spar_hole_dia,
            'front_spar_dx': self.front_spar_dx, 'front_spar_dy': self.front_spar_dy, 'front_spar_dia': self.front_spar_dia,
            'rear_spar_dx': self.rear_spar_dx, 'rear_spar_dy': self.rear_spar_dy, 'rear_spar_dia': self.rear_spar_dia,
            'plank_start': self.plank_start, 'plank_end': self.plank_end, 'plank_thick': self.plank_thick,
            'plank_part_start': self.plank_part_start, 'plank_part_end': self.plank_part_end,
            'te_cut': self.te_cut, 'washout_deg': self.washout_deg,
            'truss_angle': self.truss_angle, 'truss_front_n': self.truss_front_n, 'truss_rear_n': self.truss_rear_n,
            'beam_width': self.beam_width, 'margin_spar': self.margin_spar, 'margin_bolt': self.margin_bolt,
            'margin_outer': self.margin_outer, 'truss_fillet': self.truss_fillet, 'min_hole_dia': self.min_hole_dia,
            'xbrace_pct': self.xbrace_pct, 'xbrace_dia': self.xbrace_dia,
            'safe_margin_var': self.safe_margin_var,
            'te_cap_uf_act': self.te_cap_uf_act, 'te_cap_uf_w': self.te_cap_uf_w,
            'te_cap_ur_act': self.te_cap_ur_act, 'te_cap_ur_w': self.te_cap_ur_w,
            'te_cap_lf_act': self.te_cap_lf_act, 'te_cap_lf_w': self.te_cap_lf_w,
            'te_cap_lr_act': self.te_cap_lr_act, 'te_cap_lr_w': self.te_cap_lr_w,
            'te_cap_thick': self.te_cap_thick,
            'rc1_act': self.rc1_act, 'rc1_start': self.rc1_start, 'rc1_end': self.rc1_end, 'rc1_thick': self.rc1_thick, 'rc1_width': self.rc1_width,
            'rc2_act': self.rc2_act, 'rc2_start': self.rc2_start, 'rc2_end': self.rc2_end, 'rc2_thick': self.rc2_thick, 'rc2_width': self.rc2_width,
            'bolt1_dx': self.bolt1_dx, 'bolt1_dy': self.bolt1_dy, 'bolt1_dia': self.bolt1_dia,
            'bolt2_dx': self.bolt2_dx, 'bolt2_dy': self.bolt2_dy, 'bolt2_dia': self.bolt2_dia,
            'diag1_active': self.diag1_active, 'diag1_t1': self.diag1_t1, 'diag1_t2': self.diag1_t2, 
            'diag2_active': self.diag2_active, 'diag2_t1': self.diag2_t1, 'diag2_t2': self.diag2_t2, 
            'rib_thick': self.rib_thick,
            'main_spar_inner_dia': self.main_spar_inner_dia, 'front_spar_inner_dia': self.front_spar_inner_dia, 'rear_spar_inner_dia': self.rear_spar_inner_dia,
            'xbrace_wire_dia': getattr(self, 'xbrace_wire_dia', tk.StringVar(value='28.0')), 
            'bolt_spacer_inner_dia': self.bolt_spacer_inner_dia, 'bolt_spacer_length': self.bolt_spacer_length,
        }
        for name in ["A", "B", "C", "D", "E"]:
            for key in ['active', 'pos', 'w', 'd', 'use_dxf', 'dxf']:
                v[f'str_{name}_{key}'] = self.str_vars[name][key]
        v.update(self.get_cam_vars())
        return v

    def save_config(self): super().save_config("Single")

    def create_widgets(self):
        cf = tk.Frame(self.root, width=400)
        cf.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        top_btn_f = tk.Frame(cf)
        top_btn_f.pack(fill=tk.X, pady=(0, 10))
        tk.Button(top_btn_f, text="Load Config (JSON)", command=self.load_config).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(top_btn_f, text="Save Config (JSON)", command=self.save_config).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        tk.Label(cf, text="Root Airfoil (Base) [.dat]:").pack(anchor="w")
        f1 = tk.Frame(cf); f1.pack(fill=tk.X, pady=(0, 5))
        tk.Entry(f1, textvariable=self.file1_path, width=25).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(f1, text="Browse", command=lambda: self.browse_file(self.file1_path)).pack(side=tk.LEFT, padx=5)

        tk.Label(cf, text="Tip Airfoil (Target) [.dat]:").pack(anchor="w")
        f2 = tk.Frame(cf); f2.pack(fill=tk.X, pady=(0, 10))
        tk.Entry(f2, textvariable=self.file2_path, width=25).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(f2, text="Browse", command=lambda: self.browse_file(self.file2_path)).pack(side=tk.LEFT, padx=5)

        notebook = ttk.Notebook(cf)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        tab_main = tk.Frame(notebook)
        notebook.add(tab_main, text="Airfoil & Spars")
        params1 = [("Blend Ratio (%):", self.blend_ratio_pct), ("Chord (mm):", self.chord_length), ("Main Spar X (LEから%):", self.spar_pos_pct), ("Main Spar Dia (mm):", self.spar_hole_dia)]
        for i, (l, v) in enumerate(params1): tk.Label(tab_main, text=l).grid(row=i, column=0, sticky="e", padx=5, pady=5); tk.Entry(tab_main, textvariable=v, width=8).grid(row=i, column=1, sticky="w", padx=5)

        tk.Label(tab_main, text="Front Spar dX/dY/Dia:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        f3 = tk.Frame(tab_main); f3.grid(row=4, column=1, sticky="w")
        for v in [self.front_spar_dx, self.front_spar_dy, self.front_spar_dia]: tk.Entry(f3, textvariable=v, width=4).pack(side="left", padx=1)

        tk.Label(tab_main, text="Rear Spar dX/dY/Dia:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        f4 = tk.Frame(tab_main); f4.grid(row=5, column=1, sticky="w")
        for v in [self.rear_spar_dx, self.rear_spar_dy, self.rear_spar_dia]: tk.Entry(f4, textvariable=v, width=4).pack(side="left", padx=1)
        
        tk.Label(tab_main, text="Plank Cut(Rib) Start/End:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        f5 = tk.Frame(tab_main); f5.grid(row=6, column=1, sticky="w")
        for v in [self.plank_start, self.plank_end]: tk.Entry(f5, textvariable=v, width=4).pack(side="left", padx=1)
        
        tk.Label(tab_main, text="Plank Part Start/End:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        f5_part = tk.Frame(tab_main); f5_part.grid(row=7, column=1, sticky="w")
        for v in [self.plank_part_start, self.plank_part_end]: tk.Entry(f5_part, textvariable=v, width=4).pack(side="left", padx=1)
        
        tk.Label(tab_main, text="Plank Thick (mm):").grid(row=8, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(tab_main, textvariable=self.plank_thick, width=8).grid(row=8, column=1, sticky="w", padx=5)
        
        tk.Label(tab_main, text="TE Cut / Washout:").grid(row=9, column=0, sticky="e", padx=5, pady=5)
        f6 = tk.Frame(tab_main); f6.grid(row=9, column=1, sticky="w")
        tk.Entry(f6, textvariable=self.te_cut, width=5).pack(side="left", padx=1); tk.Entry(f6, textvariable=self.washout_deg, width=5).pack(side="left", padx=1)
        
        tk.Label(tab_main, text="TE Caps (U/L, F/R):").grid(row=10, column=0, sticky="e", padx=5, pady=5)
        tc_f = tk.Frame(tab_main); tc_f.grid(row=10, column=1, sticky="w")
        tk.Label(tc_f, text="U:").pack(side="left")
        tk.Checkbutton(tc_f, text="F", variable=self.te_cap_uf_act).pack(side="left")
        tk.Entry(tc_f, textvariable=self.te_cap_uf_w, width=3).pack(side="left")
        tk.Checkbutton(tc_f, text="R", variable=self.te_cap_ur_act).pack(side="left")
        tk.Entry(tc_f, textvariable=self.te_cap_ur_w, width=3).pack(side="left")
        tk.Label(tc_f, text=" L:").pack(side="left")
        tk.Checkbutton(tc_f, text="F", variable=self.te_cap_lf_act).pack(side="left")
        tk.Entry(tc_f, textvariable=self.te_cap_lf_w, width=3).pack(side="left")
        tk.Checkbutton(tc_f, text="R", variable=self.te_cap_lr_act).pack(side="left")
        tk.Entry(tc_f, textvariable=self.te_cap_lr_w, width=3).pack(side="left")
        tk.Label(tc_f, text=" T:").pack(side="left")
        tk.Entry(tc_f, textvariable=self.te_cap_thick, width=3).pack(side="left")

        tk.Label(tab_main, text="Rib Caps 1 (Start/End %):").grid(row=11, column=0, sticky="e", padx=5, pady=5)
        rc1_f = tk.Frame(tab_main); rc1_f.grid(row=11, column=1, sticky="w")
        tk.Checkbutton(rc1_f, text="Act", variable=self.rc1_act).pack(side="left")
        tk.Entry(rc1_f, textvariable=self.rc1_start, width=5).pack(side="left")
        tk.Label(rc1_f, text="~").pack(side="left")
        tk.Entry(rc1_f, textvariable=self.rc1_end, width=5).pack(side="left")
        tk.Label(rc1_f, text=" T:").pack(side="left")
        tk.Entry(rc1_f, textvariable=self.rc1_thick, width=3).pack(side="left")
        tk.Label(rc1_f, text=" W:").pack(side="left")
        tk.Entry(rc1_f, textvariable=self.rc1_width, width=4).pack(side="left")

        tk.Label(tab_main, text="Rib Caps 2 (Start/End %):").grid(row=12, column=0, sticky="e", padx=5, pady=5)
        rc2_f = tk.Frame(tab_main); rc2_f.grid(row=12, column=1, sticky="w")
        tk.Checkbutton(rc2_f, text="Act", variable=self.rc2_act).pack(side="left")
        tk.Entry(rc2_f, textvariable=self.rc2_start, width=5).pack(side="left")
        tk.Label(rc2_f, text="~").pack(side="left")
        tk.Entry(rc2_f, textvariable=self.rc2_end, width=5).pack(side="left")
        tk.Label(rc2_f, text=" T:").pack(side="left")
        tk.Entry(rc2_f, textvariable=self.rc2_thick, width=3).pack(side="left")
        tk.Label(rc2_f, text=" W:").pack(side="left")
        tk.Entry(rc2_f, textvariable=self.rc2_width, width=4).pack(side="left")

        tab_truss = tk.Frame(notebook)
        notebook.add(tab_truss, text="Truss & Braces")
        
        tk.Label(tab_truss, text="Truss Front/Rear Count:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        t_n_f = tk.Frame(tab_truss); t_n_f.grid(row=0, column=1, sticky="w")
        tk.Entry(t_n_f, textvariable=self.truss_front_n, width=4).pack(side="left"); tk.Entry(t_n_f, textvariable=self.truss_rear_n, width=4).pack(side="left", padx=5)

        tk.Label(tab_truss, text="Beam W / Fillet / MinHole:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        f7 = tk.Frame(tab_truss); f7.grid(row=1, column=1, sticky="w")
        for v in [self.beam_width, self.truss_fillet, self.min_hole_dia]: tk.Entry(f7, textvariable=v, width=4).pack(side="left", padx=1)

        tk.Label(tab_truss, text="Margin (Spar/Bolt/Outer):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        f8 = tk.Frame(tab_truss); f8.grid(row=2, column=1, sticky="w")
        for v in [self.margin_spar, self.margin_bolt, self.margin_outer]: tk.Entry(f8, textvariable=v, width=4).pack(side="left", padx=1)

        tk.Label(tab_truss, text="X-Brace % / Dia:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        f9 = tk.Frame(tab_truss); f9.grid(row=3, column=1, sticky="w")
        tk.Entry(f9, textvariable=self.xbrace_pct, width=5).pack(side="left", padx=1); tk.Entry(f9, textvariable=self.xbrace_dia, width=5).pack(side="left", padx=1)

        tk.Label(tab_truss, text="Diag 1 (t1%/t2%/Dia):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        f10 = tk.Frame(tab_truss); f10.grid(row=4, column=1, sticky="w")
        tk.Checkbutton(f10, text="Act", variable=self.diag1_active).pack(side="left")
        for v in [self.diag1_t1, self.diag1_t2]: tk.Entry(f10, textvariable=v, width=4).pack(side="left", padx=1)
        
        tk.Label(tab_truss, text="Diag 2 (t1%/t2%/Dia):").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        f11 = tk.Frame(tab_truss); f11.grid(row=5, column=1, sticky="w")
        tk.Checkbutton(f11, text="Act", variable=self.diag2_active).pack(side="left")
        for v in [self.diag2_t1, self.diag2_t2]: tk.Entry(f11, textvariable=v, width=4).pack(side="left", padx=1)

        tk.Label(tab_truss, text="Rib Thickness (mm):").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(tab_truss, textvariable=self.rib_thick, width=5).grid(row=6, column=1, sticky="w", padx=5)

        
        # Restored UI fields
        tk.Label(tab_main, text="Plank Part S/E:").grid(row=13, column=0, sticky="e", padx=5, pady=5)
        f_p = tk.Frame(tab_main); f_p.grid(row=13, column=1, sticky="w")
        tk.Entry(f_p, textvariable=self.plank_part_start, width=5).pack(side=tk.LEFT)
        tk.Entry(f_p, textvariable=self.plank_part_end, width=5).pack(side=tk.LEFT)

        tk.Label(tab_main, text="Root Bolt 1 (dX/dY/Dia):").grid(row=14, column=0, sticky="e", padx=5, pady=5)
        f_b1 = tk.Frame(tab_main); f_b1.grid(row=14, column=1, sticky="w")
        tk.Entry(f_b1, textvariable=self.root_bolt1_dx, width=4).pack(side=tk.LEFT)
        tk.Entry(f_b1, textvariable=self.root_bolt1_dy, width=4).pack(side=tk.LEFT)
        tk.Entry(f_b1, textvariable=self.root_bolt1_dia, width=4).pack(side=tk.LEFT)

        tk.Label(tab_main, text="Root Bolt 2 (dX/dY/Dia):").grid(row=15, column=0, sticky="e", padx=5, pady=5)
        f_b2 = tk.Frame(tab_main); f_b2.grid(row=15, column=1, sticky="w")
        tk.Entry(f_b2, textvariable=self.root_bolt2_dx, width=4).pack(side=tk.LEFT)
        tk.Entry(f_b2, textvariable=self.root_bolt2_dy, width=4).pack(side=tk.LEFT)
        tk.Entry(f_b2, textvariable=self.root_bolt2_dia, width=4).pack(side=tk.LEFT)

        tk.Label(tab_truss, text="Margin Outer (Norm/Edge):").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(tab_truss, textvariable=self.margin_outer_edge, width=6).grid(row=7, column=1, sticky="w", padx=5)
        
        tk.Label(tab_truss, text="Local Truss Angle:").grid(row=8, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(tab_truss, textvariable=self.local_truss_angle, width=6).grid(row=8, column=1, sticky="w", padx=5)
        self.create_stringers_tab(notebook)
        self.create_cam_tab(notebook)

        # Traces
        traces = [v for _, v in params1] + [
            self.front_spar_dx, self.front_spar_dy, self.front_spar_dia, self.rear_spar_dx, self.rear_spar_dy, self.rear_spar_dia, 
            self.washout_deg, self.plank_start, self.plank_end, self.plank_part_start, self.plank_part_end, self.plank_thick, self.te_cut, self.bolt1_dx, self.bolt1_dy, self.bolt1_dia,
            self.bolt2_dx, self.bolt2_dy, self.bolt2_dia, self.truss_front_n, self.truss_rear_n, self.beam_width, self.margin_spar, self.margin_bolt, self.margin_outer, self.truss_fillet, self.min_hole_dia,
            self.truss_angle, self.xbrace_pct, self.xbrace_dia, self.diag1_t1, self.diag1_t2,  self.diag2_t1, self.diag2_t2,  self.rib_thick,
            self.diag1_active, self.diag2_active,
            self.te_cap_uf_act, self.te_cap_uf_w, self.te_cap_ur_act, self.te_cap_ur_w,
            self.te_cap_lf_act, self.te_cap_lf_w, self.te_cap_lr_act, self.te_cap_lr_w, self.te_cap_thick,
            self.rc1_act, self.rc1_start, self.rc1_end, self.rc1_thick, self.rc1_width,
            self.rc2_act, self.rc2_start, self.rc2_end, self.rc2_thick, self.rc2_width,
            self.tabs_active, self.truss_tab_width, self.main_spar_support_w, self.main_spar_support_h, self.main_spar_support_thick, self.tab_thickness,
            self.spar_bridge_padding, self.spar_bridge_thickness,
            self.cam_tool_dia, self.cam_mat_thick, self.cam_safe_z, self.cam_feed_rate, self.cam_spindle_speed, self.cam_extra_depth
        ]
        for name in ["A", "B", "C", "D", "E"]:
            traces.extend([self.str_vars[name]['active'], self.str_vars[name]['pos'], self.str_vars[name]['w'], self.str_vars[name]['d'], self.str_vars[name]['use_dxf'], self.str_vars[name]['dxf']])
            
        for var in traces: 
            try: var.trace_add("write", lambda *args: self.update_preview_fast())
            except: pass

        btn_f = tk.Frame(cf); btn_f.pack(fill=tk.X, pady=10)
        tk.Button(btn_f, text="Generate Preview (Full)", command=self.update_preview_full, bg="lightgreen", height=2).pack(fill=tk.X, pady=(0, 5))
        
        ex_f = tk.Frame(btn_f)
        ex_f.pack(fill=tk.X)
        tk.Button(ex_f, text="Export DXF", command=self.export_dxf, bg="lightblue", height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        tk.Button(ex_f, text="Export OBJ (3D)", command=self.export_obj, bg="plum", height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 2))
        tk.Button(ex_f, text="Export G-Code", command=self.export_gcode, bg="khaki", height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        prev_f = tk.Frame(self.root); prev_f.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.fig = Figure(figsize=(6, 5), dpi=100); self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=prev_f)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def browse_file(self, var, is_dxf=False):
        super().browse_file(var, is_dxf)
        self.update_preview_full()

    def update_preview_fast(self, *args): self.update_preview(fast_mode=True)
    def update_preview_full(self, *args): self.update_preview(fast_mode=False)

    def get_rib_parameters(self, fast_mode=False) -> RibParameters:
        t_rib = self.safe_float(self.rib_thick)
        diag_params_list = []
        if self.diag1_active.get():
            diag_params_list.append({
                't1': self.safe_float(self.diag1_t1) / 100.0,
                't2': self.safe_float(self.diag1_t2) / 100.0,
                'R': self.safe_float(self.rear_spar_dia) / 2.0,
                't': t_rib
            })
        if self.diag2_active.get():
            diag_params_list.append({
                't1': self.safe_float(self.diag2_t1) / 100.0,
                't2': self.safe_float(self.diag2_t2) / 100.0,
                'R': self.safe_float(self.rear_spar_dia) / 2.0,
                't': t_rib
            })
            
        return RibParameters(
            file1=self.file1_path.get(),
            file2=self.file2_path.get(),
            blend_ratio=self.safe_float(self.blend_ratio_pct)/100.0,
            chord=self.safe_float(self.chord_length),
            spar_pct=self.safe_float(self.spar_pos_pct),
            washout_deg=self.safe_float(self.washout_deg),
            spar_hole_dia=self.safe_float(self.spar_hole_dia),
            rear_dx=self.safe_float(self.rear_spar_dx),
            rear_dy=self.safe_float(self.rear_spar_dy),
            rear_dia=self.safe_float(self.rear_spar_dia),
            front_dx=self.safe_float(self.front_spar_dx),
            front_dy=self.safe_float(self.front_spar_dy),
            front_dia=self.safe_float(self.front_spar_dia),
            truss_angle=self.safe_float(self.truss_angle),
            truss_front_n=self.safe_int(self.truss_front_n),
            truss_rear_n=self.safe_int(self.truss_rear_n),
            beam_width=self.safe_float(self.beam_width),
            margin_spar=self.safe_float(self.margin_spar),
            margin_bolt=self.safe_float(self.margin_bolt),
            margin_outer=self.safe_float(self.margin_outer),
            truss_fillet=self.safe_float(self.truss_fillet),
            min_hole_dia=self.safe_float(self.min_hole_dia),
            local_xb_pct=self.safe_float(self.xbrace_pct),
            x_dia=self.safe_float(self.xbrace_dia),
            plank_start=self.safe_float(self.plank_start),
            plank_end=self.safe_float(self.plank_end),
            plank_part_start=self.safe_float(self.plank_part_start),
            plank_part_end=self.safe_float(self.plank_part_end),
            plank_thick=self.safe_float(self.plank_thick),
            stringers_data=self.get_stringers_data(),
            te_cut=self.safe_float(self.te_cut),
            apply_safe_margin=self.safe_margin_var.get(),
            te_cap_uf_act=self.te_cap_uf_act.get(),
            te_cap_uf_w=self.safe_float(self.te_cap_uf_w),
            te_cap_ur_act=self.te_cap_ur_act.get(),
            te_cap_ur_w=self.safe_float(self.te_cap_ur_w),
            te_cap_lf_act=self.te_cap_lf_act.get(),
            te_cap_lf_w=self.safe_float(self.te_cap_lf_w),
            te_cap_lr_act=self.te_cap_lr_act.get(),
            te_cap_lr_w=self.safe_float(self.te_cap_lr_w),
            te_cap_thick=self.safe_float(self.te_cap_thick),
            rc1_act=self.rc1_act.get(),
            rc1_start=self.safe_float(self.rc1_start),
            rc1_end=self.safe_float(self.rc1_end),
            rc1_thick=self.safe_float(self.rc1_thick),
            rc2_act=self.rc2_act.get(),
            rc2_start=self.safe_float(self.rc2_start),
            rc2_end=self.safe_float(self.rc2_end),
            rc2_thick=self.safe_float(self.rc2_thick),
            bolt1_dx=self.safe_float(self.bolt1_dx),
            bolt1_dy=self.safe_float(self.bolt1_dy),
            bolt1_dia=self.safe_float(self.bolt1_dia),
            bolt2_dx=self.safe_float(self.bolt2_dx),
            bolt2_dy=self.safe_float(self.bolt2_dy),
            bolt2_dia=self.safe_float(self.bolt2_dia),
            diag_params_list=diag_params_list,
            fast_mode=fast_mode,
            tabs_active=self.tabs_active.get(),
            truss_tab_width=self.safe_float(self.truss_tab_width, 4.0),
            spar_tab_width=self.safe_float(self.main_spar_support_w, 4.0)
        )

    def update_preview(self, fast_mode=False):
        if getattr(self, 'is_updating_ui', False): return
        if not self.file1_path.get() or not self.file2_path.get(): return
        try:
            params = self.get_rib_parameters(fast_mode)
            res = self.engine.generate_single_rib(params)
            self.last_warnings = res.warnings_list
            chord = params.chord
            washout = params.washout_deg
            title = f"Rib Shape (Chord: {chord:.1f}mm, Washout: {washout:.2f}°)" + (" [FAST PREVIEW]" if fast_mode else "")
            self.draw_plot(*res[:12], self.last_warnings, res.plank_poly_rot, res.te_part_coords, res.c_b1, res.hole_b1, res.c_b2, res.hole_b2, res.diag_poly_pts_list, res.final_rib_orig, title, res.te_cap_pts_list, res.rc_cap_pts_list)
        except Exception as e: print("Preview Error:", e)

    def draw_plot(self, rib_pts, c_m, h_m, c_r, h_r, c_f, h_f, t_holes, xb_act, xb_c_act, xb_skip, xb_c_skip, warnings_list, plank_poly, te_part, c_b1, hole_b1, c_b2, hole_b2, diag_poly_pts_list, final_rib_orig, title, te_cap_pts_list=None, rc_cap_pts_list=None):
        self.ax.clear(); self.ax.grid(True, linestyle='--', alpha=0.7); self.ax.set_aspect('equal', adjustable='datalim')
        if len(rib_pts) > 0:
            self.ax.plot(rib_pts[:, 0], rib_pts[:, 1], 'b-', linewidth=2, label="Rib Shape")
        if final_rib_orig is not None and len(final_rib_orig) > 0:
            le = final_rib_orig[np.argmin(final_rib_orig[:, 0])]
            te = final_rib_orig[0]
            self.ax.plot([le[0], te[0]], [le[1], te[1]], 'k-.', linewidth=0.8, alpha=0.5, label="Chord Line")
        if self.safe_float(self.spar_hole_dia) > 0: self.ax.plot(c_m[0], c_m[1], 'kx', markersize=6); self.ax.plot(h_m[:, 0], h_m[:, 1], 'r-', linewidth=1.5)
        if self.safe_float(self.front_spar_dia) > 0: self.ax.plot(c_f[0], c_f[1], 'cx', markersize=6); self.ax.plot(h_f[:, 0], h_f[:, 1], 'c-', linewidth=1.5)
        if self.safe_float(self.rear_spar_dia) > 0: self.ax.plot(c_r[0], c_r[1], 'mx', markersize=6); self.ax.plot(h_r[:, 0], h_r[:, 1], 'm-', linewidth=1.5)
        if len(hole_b1) > 0: self.ax.plot(c_b1[0], c_b1[1], 'kx', markersize=4); self.ax.plot(hole_b1[:, 0], hole_b1[:, 1], 'r-', linewidth=1.5)
        if len(hole_b2) > 0: self.ax.plot(c_b2[0], c_b2[1], 'kx', markersize=4); self.ax.plot(hole_b2[:, 0], hole_b2[:, 1], 'r-', linewidth=1.5)
        for h in t_holes: self.ax.plot(h[:, 0], h[:, 1], color='orange', linestyle='-', linewidth=1.5)
        for xb in xb_act: self.ax.plot(xb[:, 0], xb[:, 1], color='orange', linestyle='-', linewidth=1.5)
        for c in xb_c_act: self.ax.plot(c[0], c[1], marker='x', color='orange', markersize=6, label="X-Brace")
        for xb in xb_skip: self.ax.plot(xb[:, 0], xb[:, 1], color='gray', linestyle=':', linewidth=1.5)
        for diag_pts in diag_poly_pts_list:
            if len(diag_pts) > 0: self.ax.plot(diag_pts[:, 0], diag_pts[:, 1], color='purple', linestyle='-', linewidth=2, label="Diagonal Spar")
        if len(plank_poly) > 0: self.ax.plot(plank_poly[:, 0], plank_poly[:, 1], color='green', linestyle='-', linewidth=1.5, alpha=0.7, label="Plank Layer")
        if len(te_part) > 0: self.ax.plot(te_part[:, 0], te_part[:, 1], color='cyan', linestyle='-', linewidth=2, label="TE Part")
        if te_cap_pts_list is not None:
            drawn_te_cap = False
            for cap_pts in te_cap_pts_list:
                if len(cap_pts) > 0:
                    self.ax.plot(cap_pts[:, 0], cap_pts[:, 1], color='black', linestyle='-', linewidth=2, label="TE Cap" if not drawn_te_cap else "")
                    drawn_te_cap = True
        if rc_cap_pts_list is not None:
            drawn_rc_cap = False
            for cap_pts in rc_cap_pts_list[0] + rc_cap_pts_list[1]:
                if len(cap_pts) > 0:
                    self.ax.plot(cap_pts[:, 0], cap_pts[:, 1], color='red', linestyle='-', linewidth=2, label="Rib Cap" if not drawn_rc_cap else "")
                    drawn_rc_cap = True
        if warnings_list: self.ax.text(0.5, 0.95, "⚠️ " + " / ".join(warnings_list), transform=self.ax.transAxes, color='white', fontsize=12, fontweight='bold', ha='center', va='top', bbox=dict(facecolor='red', alpha=0.8, edgecolor='none', pad=5))
        self.ax.set_title(title); self.ax.set_xlabel("X (mm)"); self.ax.set_ylabel("Y (mm)")
        handles, labels = self.ax.get_legend_handles_labels(); by_label = dict(zip(labels, handles)); self.ax.legend(by_label.values(), by_label.keys())
        self.canvas.draw()

    def export_dxf(self):
        f1, f2 = self.file1_path.get(), self.file2_path.get()
        if not f1 or not f2 or not os.path.exists(f1) or not os.path.exists(f2): return messagebox.showerror("Error", "Please select valid files.")
        path = filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("DXF Files", "*.dxf")])
        if not path: return
        try:
            params = self.get_rib_parameters(fast_mode=False)
            params.tabs_active = False
            res = self.engine.generate_single_rib(params)
            self.engine.export_dxf(path, res[1], res[0], res[1], self.safe_float(self.spar_hole_dia), 
                                   res[5], self.safe_float(self.front_spar_dia), res[3], self.safe_float(self.rear_spar_dia), 
                                   res[7], res[9], self.safe_float(self.xbrace_dia), res[13], res[14], 
                                   res[15], self.safe_float(self.bolt1_dia), res[16], 
                                   res[17], self.safe_float(self.bolt2_dia), res[18], res[19])
            messagebox.showinfo("Success", f"Saved to:\n{path}")
        except Exception as e: messagebox.showerror("Export Error", str(e))

    def export_obj(self):
        f1, f2 = self.file1_path.get(), self.file2_path.get()
        if not f1 or not f2 or not os.path.exists(f1) or not os.path.exists(f2): return messagebox.showerror("Error", "Please select valid files.")
        filepath = filedialog.asksaveasfilename(
            title="Save 3D Model",
            defaultextension=".glb", 
            filetypes=[("glTF Binary", "*.glb"), ("Wavefront OBJ", "*.obj")]
        )
        if not filepath: return
        
        try:
            import trimesh
        except ImportError:
            return messagebox.showerror("Error", "trimesh library is required for 3D export.\nPlease run: pip install trimesh")

        try:
            params = self.get_rib_parameters(fast_mode=False)
            params.tabs_active = False
            res = self.engine.generate_single_rib(params)
            
            c_m = res[1]
            def to_rel(pts): return np.array(pts) - c_m if len(pts) > 0 else pts
            
            rel_outline = to_rel(res[0])
            rel_holes = []
            for h_idx in [2, 4, 6, 16, 18]:
                if len(res[h_idx]) > 0: rel_holes.append(to_rel(res[h_idx]))
            for h in res[7] + res[8] + res[19]:
                rel_holes.append(to_rel(h))
            
            scene_rib_data = [(0.0, t_rib, rel_outline, rel_holes)]
            rc_cap_pts1, rc_cap_pts2 = res[23]
            if self.rc1_act.get():
                rc1_width = self.safe_float(self.rc1_width)
                rc1_y_start = 0.0 + t_rib/2.0 - rc1_width/2.0
                for cap_pts in rc_cap_pts1:
                    if len(cap_pts) > 0: scene_rib_data.append((rc1_y_start, rc1_width, to_rel(cap_pts), [], 'Rib_Cap'))
            if self.rc2_act.get():
                rc2_width = self.safe_float(self.rc2_width)
                rc2_y_start = 0.0 + t_rib/2.0 - rc2_width/2.0
                for cap_pts in rc_cap_pts2:
                    if len(cap_pts) > 0: scene_rib_data.append((rc2_y_start, rc2_width, to_rel(cap_pts), [], 'Rib_Cap'))
            
            from core.materials import AVAILABLE_MATERIALS
            part_colors = {'Ribs': AVAILABLE_MATERIALS.get('Styrofoam (Blue)', [135, 206, 235, 255]),
                           'Rib_Cap': AVAILABLE_MATERIALS.get('Carbon (Black)', [30, 30, 30, 255])}
            
            Wing3DExporter.export_3d_scene(filepath, scene_rib_data, {}, is_left_wing=False, part_colors=part_colors)
            messagebox.showinfo("Success", f"Saved 3D Model to:\n{filepath}")
        except Exception as e: messagebox.showerror("Export Error", str(e))

    def export_gcode(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".gcode", filetypes=[("G-Code Files", "*.gcode;*.nc;*.g;*.cnc")])
            if not path: return
            
            params = self.get_rib_parameters(fast_mode=False)
            res = self.engine.generate_single_rib(params)
            
            vars_dict = {k: v.get() if hasattr(v, 'get') else v for k, v in self.get_all_vars().items()}
            
            from core.cam_engine import SpindleCAMEngine
            cam = SpindleCAMEngine()
            gcode_str, warnings = cam.generate_gcode(res, vars_dict)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(gcode_str)
                
            if warnings:
                msg = "Exported G-code with warnings:\n\n" + "\n".join(warnings)
                messagebox.showwarning("Export Warning", msg)
            else:
                messagebox.showinfo("Success", f"Saved G-Code to:\n{path}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Export Error", str(e))
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from core.engine import RibGeneratorEngine, RibParameters, RibGenerationResult
from utils.config import ConfigHelper
from core.export_3d import Wing3DExporter, Wing3DBuilder
from core.export_dxf import WingDXFExporter
from ui.base_mode import BaseRibGeneratorGUI

# ==========================================
# 一括生成モードGUI
# ==========================================
class RibGeneratorGUI_Batch(BaseRibGeneratorGUI):
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

        self.root.title("Rib Generator (Batch Wing Mode)")
        self.root.geometry("1150x970") 
        self.engine = RibGeneratorEngine()
        
        self.file1_path, self.file2_path = tk.StringVar(), tk.StringVar()
        self.chord_root, self.chord_tip = tk.StringVar(value="1050.0"), tk.StringVar(value="1030.0")
        self.spar_pos_root, self.spar_pos_tip = tk.StringVar(value="41.5"), tk.StringVar(value="40.5")
        self.joint_length, self.wing_span, self.rib_interval, self.washout_tip = tk.StringVar(value="300"), tk.StringVar(value="3400.0"), tk.StringVar(value="262.0"), tk.StringVar(value="0.0")
        self.spar_hole_dia = tk.StringVar(value="107.0")
        self.front_spar_dx, self.front_spar_dy, self.front_spar_dia = tk.StringVar(value="-330.0"), tk.StringVar(value="-30.0"), tk.StringVar(value="10.0")
        self.rear_spar_dx, self.rear_spar_dy, self.rear_spar_dia = tk.StringVar(value="400.0"), tk.StringVar(value="-28.0"), tk.StringVar(value="13.4")
        self.plank_start, self.plank_end, self.plank_thick, self.te_cut = tk.StringVar(value="-15.0"), tk.StringVar(value="65.0"), tk.StringVar(value="3.0"), tk.StringVar(value="40.0")
        self.plank_part_start, self.plank_part_end = tk.StringVar(value="-15.0"), tk.StringVar(value="65.0")
        self.base_truss_angle, self.truss_front_n, self.truss_rear_n = tk.StringVar(value="60.0"), tk.StringVar(value="3"), tk.StringVar(value="5")
        
        self.beam_width, self.edge_beam_width = tk.StringVar(value="6.0"), tk.StringVar(value="6.0")
        self.margin_spar, self.margin_bolt = tk.StringVar(value="8.0"), tk.StringVar(value="8.0")
        self.margin_outer, self.margin_outer_edge = tk.StringVar(value="8.0"), tk.StringVar(value="15.0")
        self.truss_fillet, self.min_hole_dia, self.xbrace_dia = tk.StringVar(value="5.0"), tk.StringVar(value="3.0"), tk.StringVar(value="30.0")
        self.xb_start_a, self.xb_end_a = tk.StringVar(value="429.5"), tk.StringVar(value="1476")
        self.xb_start_b, self.xb_end_b = tk.StringVar(value="1476"), tk.StringVar(value="2524")
        self.xb_start_c, self.xb_end_c = tk.StringVar(value="2524"), tk.StringVar(value="3570.5")

        self.safe_margin_var = tk.BooleanVar(value=True)
        self.conn1_y, self.conn2_y, self.conn3_y, self.conn4_y = tk.StringVar(value=""), tk.StringVar(value=""), tk.StringVar(value=""), tk.StringVar(value="")
        self.root_bolt1_dx, self.root_bolt1_dy, self.root_bolt1_dia = tk.StringVar(value="0.0"), tk.StringVar(value="0.0"), tk.StringVar(value="6.0")
        self.root_bolt2_dx, self.root_bolt2_dy, self.root_bolt2_dia = tk.StringVar(value="0.0"), tk.StringVar(value="0.0"), tk.StringVar(value="6.0")
        self.tip_bolt1_dx, self.tip_bolt1_dy, self.tip_bolt1_dia = tk.StringVar(value="0.0"), tk.StringVar(value="0.0"), tk.StringVar(value="6.0")
        self.tip_bolt2_dx, self.tip_bolt2_dy, self.tip_bolt2_dia = tk.StringVar(value="0.0"), tk.StringVar(value="0.0"), tk.StringVar(value="6.0")
        
        self.diag1_active = tk.BooleanVar(value=False)
        self.diag1_y_main, self.diag1_y_rear = tk.StringVar(value="0.0"), tk.StringVar(value="3400.0")
        self.diag2_active = tk.BooleanVar(value=False)
        self.diag2_y_main, self.diag2_y_rear = tk.StringVar(value="0.0"), tk.StringVar(value="3400.0")
        self.main_spar_inner_dia = tk.StringVar(value="105.0")
        self.front_spar_inner_dia = tk.StringVar(value="8.0")
        self.rear_spar_inner_dia = tk.StringVar(value="11.4")
        self.xbrace_wire_dia = tk.StringVar(value="28.0")
        self.bolt_spacer_inner_dia = tk.StringVar(value="4.0")
        self.bolt_spacer_length = tk.StringVar(value="10.0")

        self.rib_thick = tk.StringVar(value="3.0")
        self.foam_target = tk.StringVar(value="Plank")
        self.wing_type = tk.StringVar(value="Right")
        self.conn1_type, self.conn2_type, self.conn3_type, self.conn4_type = tk.StringVar(value="Y-Shape"), tk.StringVar(value="Y-Shape"), tk.StringVar(value="Y-Shape"), tk.StringVar(value="Y-Shape")

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

        self.cr_root_in_act = tk.BooleanVar(value=False)
        self.cr_root_in_te = tk.BooleanVar(value=False)
        self.cr_root_out_act = tk.BooleanVar(value=False)
        self.cr_root_out_te = tk.BooleanVar(value=False)
        self.cr_tip_in_act = tk.BooleanVar(value=False)
        self.cr_tip_in_te = tk.BooleanVar(value=False)
        self.cr_tip_out_act = tk.BooleanVar(value=False)
        self.cr_tip_out_te = tk.BooleanVar(value=False)
        self.cr_thick = tk.StringVar(value="1.0")

        self.export_ribs = tk.BooleanVar(value=True)
        self.export_main_spar = tk.BooleanVar(value=True)
        self.export_front_spar = tk.BooleanVar(value=True)
        self.export_rear_spar = tk.BooleanVar(value=True)
        self.export_plank = tk.BooleanVar(value=True)
        self.export_te = tk.BooleanVar(value=True)
        self.export_connectors = tk.BooleanVar(value=True)
        self.export_stringers = tk.BooleanVar(value=True)
        self.export_xbrace_wires = tk.BooleanVar(value=True)
        self.export_diag_spars = tk.BooleanVar(value=True)
        self.export_carbon_ribs = tk.BooleanVar(value=True)
        self.export_te_caps = tk.BooleanVar(value=True)
        self.export_rib_caps = tk.BooleanVar(value=True)
        self.export_film = tk.BooleanVar(value=False)

        self.mat_ribs = tk.StringVar(value='Styrofoam (Blue)')
        self.mat_main_spar = tk.StringVar(value='Carbon (Black)')
        self.mat_front_spar = tk.StringVar(value='Carbon (Black)')
        self.mat_rear_spar = tk.StringVar(value='Carbon (Black)')
        self.mat_plank = tk.StringVar(value='Styrofoam (Blue)')
        self.mat_te = tk.StringVar(value='Styrofoam (Blue)')
        self.mat_connectors = tk.StringVar(value='Carbon (Black)')
        self.mat_stringers = tk.StringVar(value='Wood (Brown)')
        self.mat_xbrace_wires = tk.StringVar(value='Kevlar (Yellow)')
        self.mat_diag_spars = tk.StringVar(value='Carbon (Black)')
        self.mat_carbon_ribs = tk.StringVar(value='Carbon (Black)')
        self.mat_te_caps = tk.StringVar(value='Carbon (Black)')
        self.mat_rib_caps = tk.StringVar(value='Carbon (Black)')
        self.mat_film = tk.StringVar(value='OPP Film (Clear)')

        self.y_positions, self.truss_angles_dict, self.current_rib_idx, self.local_truss_angle = [], {}, tk.IntVar(value=0), tk.StringVar(value="60.0")
        self.last_warnings, self.is_updating_ui = [], False

        
        self.washout_root = tk.StringVar(value="0.0")
        self.washout_exp = tk.StringVar(value="1.0")
        self.spar_pos_root = getattr(self, 'spar_pos_root', tk.StringVar(value="41.5"))
        self.spar_pos_tip = getattr(self, 'spar_pos_tip', tk.StringVar(value="40.5"))
        
        self.rib_sections = getattr(self, 'rib_sections', tk.StringVar(value="5"))
        self.export_is_left = getattr(self, 'export_is_left', tk.BooleanVar(value=False))
        self.xb_start_a, self.xb_end_a = getattr(self, 'xb_start_a', tk.StringVar(value='429.5')), getattr(self, 'xb_end_a', tk.StringVar(value='1476'))
        self.xb_start_b, self.xb_end_b = getattr(self, 'xb_start_b', tk.StringVar(value='')), getattr(self, 'xb_end_b', tk.StringVar(value=''))
        self.xb_start_c, self.xb_end_c = getattr(self, 'xb_start_c', tk.StringVar(value='')), getattr(self, 'xb_end_c', tk.StringVar(value=''))
        self.carbon_te_cut = getattr(self, 'carbon_te_cut', tk.StringVar(value=''))
        self.carbon_le_cut = getattr(self, 'carbon_le_cut', tk.StringVar(value=''))
        self.carbon_offset = getattr(self, 'carbon_offset', tk.StringVar(value=''))
        self.plank_thick_tip = getattr(self, 'plank_thick_tip', tk.StringVar(value=''))
        self.plank_angle_offset = getattr(self, 'plank_angle_offset', tk.StringVar(value=''))
        
        if not hasattr(self, 'str_vars') or not isinstance(self.str_vars, dict):
            self.str_vars = {}
            for name in ["A", "B", "C", "D", "E"]:
                is_act = tk.BooleanVar(value=(name in ["A", "B"]))
                pos = tk.StringVar(value="-15.0" if name == "A" else ("60.0" if name == "B" else ""))
                w = tk.StringVar(value="5.0")
                d = tk.StringVar(value="4.0")
                use_dxf = tk.BooleanVar(value=False)
                dxf = tk.StringVar(value="")
                self.str_vars[name] = {'active': is_act, 'pos': pos, 'w': w, 'd': d, 'use_dxf': use_dxf, 'dxf': dxf}

        self.te_cap_uf_d = getattr(self, 'te_cap_uf_d', tk.BooleanVar(value=False))
        self.te_cap_lf_d = getattr(self, 'te_cap_lf_d', tk.BooleanVar(value=False))
        self.main_spar_tab_width = getattr(self, 'main_spar_tab_width', tk.StringVar(value=''))
        self.main_spar_tab_dist = getattr(self, 'main_spar_tab_dist', tk.StringVar(value=''))
        self.fr_spar_tab_width = getattr(self, 'fr_spar_tab_width', tk.StringVar(value=''))
        self.fr_spar_tab_dist = getattr(self, 'fr_spar_tab_dist', tk.StringVar(value=''))
        self.tab_depth = getattr(self, 'tab_depth', tk.StringVar(value=''))
        self.cam_margin = getattr(self, 'cam_margin', tk.StringVar(value=''))
        self.cam_selected_rib = getattr(self, 'cam_selected_rib', tk.StringVar(value=''))
        self.foam_cut_kerf = getattr(self, 'foam_cut_kerf', tk.StringVar(value=''))
        self.foam_cut_z_offset = getattr(self, 'foam_cut_z_offset', tk.StringVar(value=''))
        self.foam_block_width = getattr(self, 'foam_block_width', tk.StringVar(value=''))
        self.foam_overcut_x = getattr(self, 'foam_overcut_x', tk.StringVar(value=''))
        self.foam_clearance_z = getattr(self, 'foam_clearance_z', tk.StringVar(value=''))
        self.foam_support_y = getattr(self, 'foam_support_y', tk.StringVar(value=''))
        self.dxf_export_ribs = getattr(self, 'dxf_export_ribs', tk.StringVar(value=''))
        self.dxf_export_plank = getattr(self, 'dxf_export_plank', tk.StringVar(value=''))
        self.dxf_export_te = getattr(self, 'dxf_export_te', tk.StringVar(value=''))
        self.dxf_export_carbon = getattr(self, 'dxf_export_carbon', tk.StringVar(value=''))
        self.dxf_export_stringer = getattr(self, 'dxf_export_stringer', tk.StringVar(value=''))
        self.create_widgets()
        self.calculate_y_positions()

    def get_all_vars(self):
        v = {
            'file1_path': self.file1_path, 'file2_path': self.file2_path,
            'chord_root': self.chord_root, 'chord_tip': self.chord_tip,
            'spar_pos_root': self.spar_pos_root, 'spar_pos_tip': self.spar_pos_tip,
            'joint_length': self.joint_length, 'wing_span': self.wing_span, 'rib_interval': self.rib_interval, 'washout_tip': self.washout_tip,
            'spar_hole_dia': self.spar_hole_dia,
            'front_spar_dx': self.front_spar_dx, 'front_spar_dy': self.front_spar_dy, 'front_spar_dia': self.front_spar_dia,
            'rear_spar_dx': self.rear_spar_dx, 'rear_spar_dy': self.rear_spar_dy, 'rear_spar_dia': self.rear_spar_dia,
            'plank_start': self.plank_start, 'plank_end': self.plank_end, 'plank_thick': self.plank_thick, 'te_cut': self.te_cut,
            'plank_part_start': self.plank_part_start, 'plank_part_end': self.plank_part_end,
            'base_truss_angle': self.base_truss_angle, 'truss_front_n': self.truss_front_n, 'truss_rear_n': self.truss_rear_n,
            'beam_width': self.beam_width, 'edge_beam_width': self.edge_beam_width,
            'margin_spar': self.margin_spar, 'margin_bolt': self.margin_bolt,
            'margin_outer': self.margin_outer, 'margin_outer_edge': self.margin_outer_edge,
            'truss_fillet': self.truss_fillet, 'min_hole_dia': self.min_hole_dia,
            'xbrace_dia': self.xbrace_dia,
            'xb_start_a': self.xb_start_a, 'xb_end_a': self.xb_end_a,
            'xb_start_b': self.xb_start_b, 'xb_end_b': self.xb_end_b,
            'xb_start_c': self.xb_start_c, 'xb_end_c': self.xb_end_c,
            'safe_margin_var': self.safe_margin_var,
            'root_bolt1_dx': self.root_bolt1_dx, 'root_bolt1_dy': self.root_bolt1_dy, 'root_bolt1_dia': self.root_bolt1_dia,
            'root_bolt2_dx': self.root_bolt2_dx, 'root_bolt2_dy': self.root_bolt2_dy, 'root_bolt2_dia': self.root_bolt2_dia,
            'tip_bolt1_dx': self.tip_bolt1_dx, 'tip_bolt1_dy': self.tip_bolt1_dy, 'tip_bolt1_dia': self.tip_bolt1_dia,
            'tip_bolt2_dx': self.tip_bolt2_dx, 'tip_bolt2_dy': self.tip_bolt2_dy, 'tip_bolt2_dia': self.tip_bolt2_dia,
            'diag1_active': self.diag1_active, 'diag1_y_main': self.diag1_y_main, 'diag1_y_rear': self.diag1_y_rear, 
            'diag2_active': self.diag2_active, 'diag2_y_main': self.diag2_y_main, 'diag2_y_rear': self.diag2_y_rear, 
            'main_spar_inner_dia': self.main_spar_inner_dia, 'front_spar_inner_dia': self.front_spar_inner_dia, 'rear_spar_inner_dia': self.rear_spar_inner_dia,
            'xbrace_wire_dia': getattr(self, 'xbrace_wire_dia', self.xbrace_dia), 
            'bolt_spacer_inner_dia': self.bolt_spacer_inner_dia, 'bolt_spacer_length': self.bolt_spacer_length,
            'conn1_y': self.conn1_y, 'conn2_y': self.conn2_y, 'conn3_y': self.conn3_y, 'conn4_y': self.conn4_y,
            'conn1_type': self.conn1_type, 'conn2_type': self.conn2_type, 'conn3_type': self.conn3_type, 'conn4_type': self.conn4_type,
            'rib_thick': self.rib_thick,
            'wing_type': self.wing_type,
            'te_cap_uf_act': self.te_cap_uf_act, 'te_cap_uf_w': self.te_cap_uf_w,
            'te_cap_ur_act': self.te_cap_ur_act, 'te_cap_ur_w': self.te_cap_ur_w,
            'te_cap_lf_act': self.te_cap_lf_act, 'te_cap_lf_w': self.te_cap_lf_w,
            'te_cap_lr_act': self.te_cap_lr_act, 'te_cap_lr_w': self.te_cap_lr_w,
            'te_cap_thick': self.te_cap_thick,
            'rc1_act': self.rc1_act, 'rc1_start': self.rc1_start, 'rc1_end': self.rc1_end, 'rc1_thick': self.rc1_thick, 'rc1_width': self.rc1_width,
            'rc2_act': self.rc2_act, 'rc2_start': self.rc2_start, 'rc2_end': self.rc2_end, 'rc2_thick': self.rc2_thick, 'rc2_width': self.rc2_width,
            'cr_root_in_act': self.cr_root_in_act, 'cr_root_in_te': self.cr_root_in_te,
            'cr_root_out_act': self.cr_root_out_act, 'cr_root_out_te': self.cr_root_out_te,
            'cr_tip_in_act': self.cr_tip_in_act, 'cr_tip_in_te': self.cr_tip_in_te,
            'cr_tip_out_act': self.cr_tip_out_act, 'cr_tip_out_te': self.cr_tip_out_te,
            'cr_thick': self.cr_thick,
            'export_ribs': self.export_ribs,
            'export_main_spar': self.export_main_spar,
            'export_front_spar': self.export_front_spar,
            'export_rear_spar': self.export_rear_spar,
            'export_plank': self.export_plank,
            'export_te': self.export_te,
            'export_connectors': self.export_connectors,
            'export_stringers': self.export_stringers,
            'export_xbrace_wires': self.export_xbrace_wires,
            'export_diag_spars': self.export_diag_spars,
            'export_carbon_ribs': self.export_carbon_ribs,
            'export_te_caps': self.export_te_caps,
            'export_rib_caps': self.export_rib_caps,
            'export_film': self.export_film,
            'mat_ribs': self.mat_ribs,
            'mat_main_spar': self.mat_main_spar,
            'mat_front_spar': self.mat_front_spar,
            'mat_rear_spar': self.mat_rear_spar,
            'mat_plank': self.mat_plank,
            'mat_te': self.mat_te,
            'mat_connectors': self.mat_connectors,
            'mat_stringers': self.mat_stringers,
            'mat_xbrace_wires': self.mat_xbrace_wires,
            'mat_diag_spars': self.mat_diag_spars,
            'mat_carbon_ribs': self.mat_carbon_ribs,
            'mat_te_caps': self.mat_te_caps,
            'mat_rib_caps': self.mat_rib_caps,
            'mat_film': self.mat_film
        }
        for name in ["A", "B", "C", "D", "E"]:
            for key in ['active', 'pos', 'w', 'd', 'use_dxf', 'dxf']:
                v[f'str_{name}_{key}'] = self.str_vars[name][key]
        v.update(self.get_cam_vars())
        return v

    def save_config(self): super().save_config("Batch")

    def create_widgets(self):
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Options Notebook
        left_frame = ttk.Frame(main_pane, width=450)
        main_pane.add(left_frame, weight=0)

        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Create Tabs
        tab_wing = ttk.Frame(notebook); notebook.add(tab_wing, text="Wing (span)")
        tab_spar = ttk.Frame(notebook); notebook.add(tab_spar, text="Spar")
        tab_rib = ttk.Frame(notebook); notebook.add(tab_rib, text="Rib")
        tab_plank = ttk.Frame(notebook); notebook.add(tab_plank, text="Plank & stringers & TE")
        tab_cnc = ttk.Frame(notebook); notebook.add(tab_cnc, text="CNC milling")
        tab_export3d = ttk.Frame(notebook); notebook.add(tab_export3d, text="3D Export")
        tab_foam = ttk.Frame(notebook); notebook.add(tab_foam, text="CNC foam cutter")
        tab_dxf = ttk.Frame(notebook); notebook.add(tab_dxf, text="DXF Export")

        # --- Tab 1: Wing (span) ---
        row_idx = 0
        ttk.Label(tab_wing, text="Wing Span Settings", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        ttk.Label(tab_wing, text="Airfoil (Root):").grid(row=row_idx, column=0, sticky=tk.W)
        f1 = ttk.Frame(tab_wing); f1.grid(row=row_idx, column=1, sticky=tk.EW)
        ttk.Entry(f1, textvariable=self.file1_path, width=20).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(f1, text="Browse", command=lambda: self.browse_file(self.file1_path)).pack(side=tk.LEFT); row_idx += 1
        
        ttk.Label(tab_wing, text="Airfoil (Tip):").grid(row=row_idx, column=0, sticky=tk.W)
        f2 = ttk.Frame(tab_wing); f2.grid(row=row_idx, column=1, sticky=tk.EW)
        ttk.Entry(f2, textvariable=self.file2_path, width=20).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(f2, text="Browse", command=lambda: self.browse_file(self.file2_path)).pack(side=tk.LEFT); row_idx += 1

        ttk.Label(tab_wing, text="Chord (Root/Tip):").grid(row=row_idx, column=0, sticky=tk.W)
        fc = ttk.Frame(tab_wing); fc.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fc, textvariable=self.chord_root, width=8).pack(side=tk.LEFT)
        ttk.Label(fc, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(fc, textvariable=self.chord_tip, width=8).pack(side=tk.LEFT)

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
        ttk.Entry(tab_wing, textvariable=self.cr_thick, width=8).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1

        ttk.Label(fc, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(fc, textvariable=self.chord_tip, width=8).pack(side=tk.LEFT)
        row_idx += 1

        ttk.Label(tab_wing, text="Wing Span:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_wing, textvariable=self.wing_span, width=10).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_wing, text="Rib Sections:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_wing, textvariable=self.rib_sections, width=10).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_wing, text="Joint Length:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_wing, textvariable=self.joint_length, width=10).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        
        ttk.Label(tab_wing, text="Washout (Root/Tip/Exp):").grid(row=row_idx, column=0, sticky=tk.W)
        fw = ttk.Frame(tab_wing); fw.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fw, textvariable=self.washout_root, width=5).pack(side=tk.LEFT)
        ttk.Label(fw, text="/").pack(side=tk.LEFT)
        ttk.Entry(fw, textvariable=self.washout_tip, width=5).pack(side=tk.LEFT)
        ttk.Label(fw, text="/").pack(side=tk.LEFT)
        ttk.Entry(fw, textvariable=self.washout_exp, width=5).pack(side=tk.LEFT)
        row_idx += 1
        
        ttk.Checkbutton(tab_wing, text="Is Left Wing (Mirrored)", variable=self.export_is_left).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        
        ttk.Separator(tab_wing, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_wing, text="Connectors", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Checkbutton(tab_wing, text="Use Safe Margin for Conns", variable=self.safe_margin_var).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Label(tab_wing, text="Conn 1-4 Y pos:").grid(row=row_idx, column=0, sticky=tk.W)
        f_conn = ttk.Frame(tab_wing); f_conn.grid(row=row_idx, column=1, sticky=tk.W)
        for var in [self.conn1_y, self.conn2_y, self.conn3_y, self.conn4_y]:
            ttk.Entry(f_conn, textvariable=var, width=5).pack(side=tk.LEFT, padx=1)
        row_idx += 1

        ttk.Separator(tab_wing, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_wing, text="X-Brace Positions", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Label(tab_wing, text="Zone 1 (Start/End):").grid(row=row_idx, column=0, sticky=tk.W)
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
        row_idx += 1
        
        ttk.Separator(tab_wing, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_wing, text="Diagonal Connectors", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        for d_idx, (act_var, ym_var, yr_var) in enumerate([(self.diag1_active, self.diag1_y_main, self.diag1_y_rear), 
                                                           (self.diag2_active, self.diag2_y_main, self.diag2_y_rear)]):
            ttk.Checkbutton(tab_wing, text=f"Diag {d_idx+1} Active", variable=act_var).grid(row=row_idx, column=0, sticky=tk.W)
            f_dg = ttk.Frame(tab_wing); f_dg.grid(row=row_idx, column=1, sticky=tk.W)
            ttk.Label(f_dg, text="MainY:").pack(side=tk.LEFT)
            ttk.Entry(f_dg, textvariable=ym_var, width=6).pack(side=tk.LEFT)
            ttk.Label(f_dg, text=" RearY:").pack(side=tk.LEFT)
            ttk.Entry(f_dg, textvariable=yr_var, width=6).pack(side=tk.LEFT)
            row_idx += 1

        # --- Tab 2: Spar ---
        row_idx = 0
        ttk.Label(tab_spar, text="Main Spar", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        ttk.Label(tab_spar, text="Outer Dia / Inner Dia:").grid(row=row_idx, column=0, sticky=tk.W)
        fs_m = ttk.Frame(tab_spar); fs_m.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fs_m, textvariable=self.spar_hole_dia, width=6).pack(side=tk.LEFT)
        ttk.Label(fs_m, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(fs_m, textvariable=self.main_spar_inner_dia, width=6).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_spar, text="Position (LE%):").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_spar, textvariable=self.spar_pos_root, width=6).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1

        ttk.Separator(tab_spar, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_spar, text="Front Spar", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Label(tab_spar, text="Outer Dia / Inner Dia:").grid(row=row_idx, column=0, sticky=tk.W)
        fs_f = ttk.Frame(tab_spar); fs_f.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fs_f, textvariable=self.front_spar_dia, width=6).pack(side=tk.LEFT)
        ttk.Label(fs_f, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(fs_f, textvariable=self.front_spar_inner_dia, width=6).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_spar, text="Offset DX / DY:").grid(row=row_idx, column=0, sticky=tk.W)
        fs_fd = ttk.Frame(tab_spar); fs_fd.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fs_fd, textvariable=self.front_spar_dx, width=6).pack(side=tk.LEFT)
        ttk.Label(fs_fd, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(fs_fd, textvariable=self.front_spar_dy, width=6).pack(side=tk.LEFT)
        row_idx += 1

        ttk.Separator(tab_spar, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_spar, text="Rear Spar", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Label(tab_spar, text="Outer Dia / Inner Dia:").grid(row=row_idx, column=0, sticky=tk.W)
        fs_r = ttk.Frame(tab_spar); fs_r.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fs_r, textvariable=self.rear_spar_dia, width=6).pack(side=tk.LEFT)
        ttk.Label(fs_r, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(fs_r, textvariable=self.rear_spar_inner_dia, width=6).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_spar, text="Offset DX / DY:").grid(row=row_idx, column=0, sticky=tk.W)
        fs_rd = ttk.Frame(tab_spar); fs_rd.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fs_rd, textvariable=self.rear_spar_dx, width=6).pack(side=tk.LEFT)
        ttk.Label(fs_rd, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(fs_rd, textvariable=self.rear_spar_dy, width=6).pack(side=tk.LEFT)
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
        ttk.Entry(f_b4, textvariable=self.tip_bolt2_dia, width=5).pack(side=tk.LEFT); row_idx += 1

                # --- Tab 3: Rib ---
        # Wrapping Rib tab in a canvas for scrollbar if needed, but it should fit
        row_idx = 0
        ttk.Label(tab_rib, text="Truss Relations", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        ttk.Label(tab_rib, text="Edge/Mid Beam W:").grid(row=row_idx, column=0, sticky=tk.W)
        fr_b = ttk.Frame(tab_rib); fr_b.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fr_b, textvariable=self.edge_beam_width, width=5).pack(side=tk.LEFT)
        ttk.Label(fr_b, text="/").pack(side=tk.LEFT)
        ttk.Entry(fr_b, textvariable=self.beam_width, width=5).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_rib, text="Margins (Spar/Bolt/Outer):").grid(row=row_idx, column=0, sticky=tk.W)
        fr_m = ttk.Frame(tab_rib); fr_m.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fr_m, textvariable=self.margin_spar, width=4).pack(side=tk.LEFT)
        ttk.Entry(fr_m, textvariable=self.margin_bolt, width=4).pack(side=tk.LEFT)
        ttk.Entry(fr_m, textvariable=self.margin_outer, width=4).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_rib, text="Fillet / Min Hole:").grid(row=row_idx, column=0, sticky=tk.W)
        fr_f = ttk.Frame(tab_rib); fr_f.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fr_f, textvariable=self.truss_fillet, width=5).pack(side=tk.LEFT)
        ttk.Label(fr_f, text="/").pack(side=tk.LEFT)
        ttk.Entry(fr_f, textvariable=self.min_hole_dia, width=5).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_rib, text="Truss N (Front/Rear):").grid(row=row_idx, column=0, sticky=tk.W)
        fr_n = ttk.Frame(tab_rib); fr_n.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fr_n, textvariable=self.truss_front_n, width=4).pack(side=tk.LEFT)
        ttk.Entry(fr_n, textvariable=self.truss_rear_n, width=4).pack(side=tk.LEFT)
        row_idx += 1

        ttk.Separator(tab_rib, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_rib, text="X-Brace Hole & Wire", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Label(tab_rib, text="Hole Dia / Wire Dia:").grid(row=row_idx, column=0, sticky=tk.W)
        fxb = ttk.Frame(tab_rib); fxb.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fxb, textvariable=self.xbrace_dia, width=6).pack(side=tk.LEFT)
        ttk.Label(fxb, text=" / ").pack(side=tk.LEFT)
        ttk.Entry(fxb, textvariable=self.xbrace_wire_dia, width=6).pack(side=tk.LEFT)
        row_idx += 1

        ttk.Separator(tab_rib, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_rib, text="Bolt Hole Relations", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Label(tab_rib, text="Spacers (Inner Dia / Len):").grid(row=row_idx, column=0, sticky=tk.W)
        fb_s = ttk.Frame(tab_rib); fb_s.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fb_s, textvariable=self.bolt_spacer_inner_dia, width=5).pack(side=tk.LEFT)
        ttk.Label(fb_s, text="/").pack(side=tk.LEFT)
        ttk.Entry(fb_s, textvariable=self.bolt_spacer_length, width=5).pack(side=tk.LEFT)
        row_idx += 1
        for b_lbl, b1_dx, b1_dy, b1_dia, b2_dx, b2_dy, b2_dia in [
            ("Root Bolts (DX/DY/Dia)", self.root_bolt1_dx, self.root_bolt1_dy, self.root_bolt1_dia, self.root_bolt2_dx, self.root_bolt2_dy, self.root_bolt2_dia),
            ("Tip Bolts (DX/DY/Dia)", self.tip_bolt1_dx, self.tip_bolt1_dy, self.tip_bolt1_dia, self.tip_bolt2_dx, self.tip_bolt2_dy, self.tip_bolt2_dia)
        ]:
            ttk.Label(tab_rib, text=b_lbl).grid(row=row_idx, column=0, sticky=tk.W)
            fb = ttk.Frame(tab_rib); fb.grid(row=row_idx, column=1, sticky=tk.W)
            ttk.Entry(fb, textvariable=b1_dx, width=4).pack(side=tk.LEFT)
            ttk.Entry(fb, textvariable=b1_dy, width=4).pack(side=tk.LEFT)
            ttk.Entry(fb, textvariable=b1_dia, width=4).pack(side=tk.LEFT)
            ttk.Label(fb, text="|").pack(side=tk.LEFT, padx=2)
            ttk.Entry(fb, textvariable=b2_dx, width=4).pack(side=tk.LEFT)
            ttk.Entry(fb, textvariable=b2_dy, width=4).pack(side=tk.LEFT)
            ttk.Entry(fb, textvariable=b2_dia, width=4).pack(side=tk.LEFT)
            row_idx += 1

        ttk.Separator(tab_rib, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_rib, text="General & Carbon Rib", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Label(tab_rib, text="Rib Thickness:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_rib, textvariable=self.rib_thick, width=6).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_rib, text="Carbon (TE/LE Cut/Offset):").grid(row=row_idx, column=0, sticky=tk.W)
        fcb = ttk.Frame(tab_rib); fcb.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(fcb, textvariable=self.carbon_te_cut, width=5).pack(side=tk.LEFT)
        ttk.Entry(fcb, textvariable=self.carbon_le_cut, width=5).pack(side=tk.LEFT)
        ttk.Entry(fcb, textvariable=self.carbon_offset, width=5).pack(side=tk.LEFT)
        row_idx += 1

        ttk.Separator(tab_rib, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_rib, text="Rib Caps", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        for i, (act, w, st, en, th) in enumerate([(self.rc1_act, self.rc1_width, self.rc1_start, self.rc1_end, self.rc1_thick),
                                                  (self.rc2_act, self.rc2_width, self.rc2_start, self.rc2_end, self.rc2_thick)]):
            f_rc = ttk.Frame(tab_rib); f_rc.grid(row=row_idx, column=0, columnspan=2, sticky=tk.W)
            ttk.Checkbutton(f_rc, text=f"Cap{i+1}", variable=act).pack(side=tk.LEFT)
            ttk.Label(f_rc, text="W/St/En/Th:").pack(side=tk.LEFT)
            for v in [w, st, en, th]: ttk.Entry(f_rc, textvariable=v, width=4).pack(side=tk.LEFT, padx=1)
            row_idx += 1

        # --- Tab 4: Plank & Stringers & TE ---
        row_idx = 0
        ttk.Label(tab_plank, text="Plank Relations", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        ttk.Label(tab_plank, text="Start / End %:").grid(row=row_idx, column=0, sticky=tk.W)
        f_pk1 = ttk.Frame(tab_plank); f_pk1.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_pk1, textvariable=self.plank_start, width=6).pack(side=tk.LEFT)
        ttk.Label(f_pk1, text="/").pack(side=tk.LEFT)
        ttk.Entry(f_pk1, textvariable=self.plank_end, width=6).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_plank, text="Thickness (Root/Tip):").grid(row=row_idx, column=0, sticky=tk.W)
        f_pk2 = ttk.Frame(tab_plank); f_pk2.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_pk2, textvariable=self.plank_thick, width=6).pack(side=tk.LEFT)
        ttk.Label(f_pk2, text="/").pack(side=tk.LEFT)
        ttk.Entry(f_pk2, textvariable=self.plank_thick_tip, width=6).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_plank, text="Angle Offset (deg):").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_plank, textvariable=self.plank_angle_offset, width=6).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1

        ttk.Separator(tab_plank, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_plank, text="Stringers", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        for name in ["A", "B", "C", "D", "E"]:
            f_str = ttk.Frame(tab_plank); f_str.grid(row=row_idx, column=0, columnspan=2, sticky=tk.W)
            ttk.Checkbutton(f_str, text=name, variable=self.str_vars[name]['active']).pack(side=tk.LEFT)
            ttk.Label(f_str, text="Pos%").pack(side=tk.LEFT)
            ttk.Entry(f_str, textvariable=self.str_vars[name]['pos'], width=4).pack(side=tk.LEFT)
            ttk.Label(f_str, text="W").pack(side=tk.LEFT)
            ttk.Entry(f_str, textvariable=self.str_vars[name]['w'], width=4).pack(side=tk.LEFT)
            ttk.Label(f_str, text="D").pack(side=tk.LEFT)
            ttk.Entry(f_str, textvariable=self.str_vars[name]['d'], width=4).pack(side=tk.LEFT)
            ttk.Checkbutton(f_str, text="DXF", variable=self.str_vars[name]['use_dxf']).pack(side=tk.LEFT)
            ttk.Entry(f_str, textvariable=self.str_vars[name]['dxf'], width=10).pack(side=tk.LEFT)
            ttk.Button(f_str, text="...", command=lambda v=self.str_vars[name]['dxf']: self.browse_file(v, True), width=2).pack(side=tk.LEFT)
            row_idx += 1

        ttk.Separator(tab_plank, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_plank, text="TE Relations", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Label(tab_plank, text="TE Cut:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_plank, textvariable=self.te_cut, width=6).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        
        f_te1 = ttk.Frame(tab_plank); f_te1.grid(row=row_idx, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(f_te1, text="TE Cap Upper", variable=self.te_cap_uf_act).pack(side=tk.LEFT)
        ttk.Label(f_te1, text="W:").pack(side=tk.LEFT); ttk.Entry(f_te1, textvariable=self.te_cap_uf_w, width=4).pack(side=tk.LEFT)
        ttk.Label(f_te1, text="D:").pack(side=tk.LEFT); ttk.Entry(f_te1, textvariable=self.te_cap_uf_d, width=4).pack(side=tk.LEFT)
        row_idx += 1
        
        f_te2 = ttk.Frame(tab_plank); f_te2.grid(row=row_idx, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(f_te2, text="TE Cap Lower", variable=self.te_cap_lf_act).pack(side=tk.LEFT)
        ttk.Label(f_te2, text="W:").pack(side=tk.LEFT); ttk.Entry(f_te2, textvariable=self.te_cap_lf_w, width=4).pack(side=tk.LEFT)
        ttk.Label(f_te2, text="D:").pack(side=tk.LEFT); ttk.Entry(f_te2, textvariable=self.te_cap_lf_d, width=4).pack(side=tk.LEFT)

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
        ttk.Entry(f_rc2, textvariable=self.rc2_thick, width=4).pack(side=tk.LEFT); row_idx += 1

        row_idx += 1

        # --- Tab 5: CNC milling ---
        row_idx = 0
        ttk.Label(tab_cnc, text="Tabs Settings", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        ttk.Checkbutton(tab_cnc, text="Enable Tabs", variable=self.tabs_active).grid(row=row_idx, column=0, sticky=tk.W); row_idx += 1
        ttk.Label(tab_cnc, text="Truss Tab Width:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_cnc, textvariable=self.truss_tab_width, width=6).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_cnc, text="Main Spar Tab (W/Dist):").grid(row=row_idx, column=0, sticky=tk.W)
        f_t1 = ttk.Frame(tab_cnc); f_t1.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_t1, textvariable=self.main_spar_tab_width, width=6).pack(side=tk.LEFT)
        ttk.Entry(f_t1, textvariable=self.main_spar_tab_dist, width=6).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_cnc, text="F/R Spar Tab (W/Dist):").grid(row=row_idx, column=0, sticky=tk.W)
        f_t2 = ttk.Frame(tab_cnc); f_t2.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_t2, textvariable=self.fr_spar_tab_width, width=6).pack(side=tk.LEFT)
        ttk.Entry(f_t2, textvariable=self.fr_spar_tab_dist, width=6).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_cnc, text="Tab Depth:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_cnc, textvariable=self.tab_depth, width=6).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1

        ttk.Separator(tab_cnc, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_cnc, text="CNC Milling Settings", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, sticky=tk.W); row_idx += 1
        ttk.Label(tab_cnc, text="Tool Dia / Margin:").grid(row=row_idx, column=0, sticky=tk.W)
        f_m1 = ttk.Frame(tab_cnc); f_m1.grid(row=row_idx, column=1, sticky=tk.W)
        ttk.Entry(f_m1, textvariable=self.cam_tool_dia, width=6).pack(side=tk.LEFT)
        ttk.Entry(f_m1, textvariable=self.cam_margin, width=6).pack(side=tk.LEFT)
        row_idx += 1
        ttk.Label(tab_cnc, text="Direction:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Combobox(tab_cnc, textvariable=self.cam_milling_dir, values=["Conventional", "Climb"], width=10, state="readonly").grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_cnc, text="Output Target:").grid(row=row_idx, column=0, sticky=tk.W)
        self.combo_cam_rib = ttk.Combobox(tab_cnc, textvariable=self.cam_selected_rib, values=["ALL"], width=15, state="readonly")
        self.combo_cam_rib.grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Button(tab_cnc, text="Export G-Code", command=self.export_gcode_all).grid(row=row_idx, column=0, columnspan=2, pady=10)

        # --- Tab 6: 3D Export ---
        row_idx = 0
        ttk.Label(tab_export3d, text="Export Parts List", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        
        parts_flags = [
            ("Carbon Ribs", self.export_carbon_ribs),
            ("Main Spar", self.export_main_spar),
            ("Front Spar", self.export_front_spar),
            ("Rear Spar", self.export_rear_spar),
            ("Connectors", self.export_connectors),
            ("Diagonal Spars", self.export_diag_spars),
            ("X-Brace Wires", self.export_xbrace_wires),
            ("Plank Skin", self.export_plank),
            ("TE Skin", self.export_te),
            ("Film Skin", self.export_film),
            ("Stringers", self.export_stringers),
            ("TE Caps", self.export_te_caps),
            ("Rib Caps", self.export_rib_caps)
        ]
        
        for i, (name, var) in enumerate(parts_flags):
            ttk.Checkbutton(tab_export3d, text=name, variable=var).grid(row=row_idx + i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
        row_idx += (len(parts_flags) // 2) + 1
        

        ttk.Separator(tab_export3d, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Label(tab_export3d, text="Materials", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        
        mat_opts = ['Styrofoam (Blue)', 'Carbon (Black)', 'Wood (Brown)', 'Kevlar (Yellow)', 'OPP Film (Clear)', 'Metal (Silver)']
        
        mat_vars = [
            ("Ribs", self.mat_ribs), ("Carbon Ribs", self.mat_carbon_ribs),
            ("Main Spar", self.mat_main_spar), ("Front/Rear Spars", self.mat_front_spar),
            ("Plank", self.mat_plank), ("TE/Rib Caps", self.mat_te_caps),
            ("X-Brace", self.mat_xbrace_wires), ("Connectors", self.mat_connectors),
            ("Stringers", self.mat_stringers), ("Film", self.mat_film)
        ]
        
        for i, (name, var) in enumerate(mat_vars):
            ttk.Label(tab_export3d, text=name+":").grid(row=row_idx + i//2, column=(i%2)*2, sticky=tk.E, padx=5, pady=2)
            ttk.Combobox(tab_export3d, textvariable=var, values=mat_opts, width=15).grid(row=row_idx + i//2, column=(i%2)*2 + 1, sticky=tk.W, padx=5, pady=2)
            
        row_idx += (len(mat_vars) // 2) + 1

        ttk.Separator(tab_export3d, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky=tk.EW, pady=5); row_idx += 1
        ttk.Button(tab_export3d, text="Export 3D Model (.glb)", command=self.export_obj).grid(row=row_idx, column=0, columnspan=2, pady=10)

        # --- Tab 7: CNC foam cutter ---
        row_idx = 0
        ttk.Label(tab_foam, text="Foam CNC Settings", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        ttk.Label(tab_foam, text="Kerf (Wire thick):").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_foam, textvariable=self.foam_cut_kerf, width=10).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_foam, text="Z Offset:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_foam, textvariable=self.foam_cut_z_offset, width=10).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_foam, text="Block Width:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_foam, textvariable=self.foam_block_width, width=10).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_foam, text="Overcut X:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_foam, textvariable=self.foam_overcut_x, width=10).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_foam, text="Clearance Z:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_foam, textvariable=self.foam_clearance_z, width=10).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Label(tab_foam, text="Support Y:").grid(row=row_idx, column=0, sticky=tk.W)
        ttk.Entry(tab_foam, textvariable=self.foam_support_y, width=10).grid(row=row_idx, column=1, sticky=tk.W); row_idx += 1
        ttk.Button(tab_foam, text="Open in Foam CAM", command=self.open_in_foam_cam).grid(row=row_idx, column=0, columnspan=2, pady=10)

        # --- Tab 8: DXF Export ---
        row_idx = 0
        ttk.Label(tab_dxf, text="Export Parts List", font=("", 10, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=5, sticky=tk.W); row_idx += 1
        ttk.Checkbutton(tab_dxf, text="Ribs", variable=self.dxf_export_ribs).grid(row=row_idx, column=0, sticky=tk.W); row_idx += 1
        ttk.Checkbutton(tab_dxf, text="Plank", variable=self.dxf_export_plank).grid(row=row_idx, column=0, sticky=tk.W); row_idx += 1
        ttk.Checkbutton(tab_dxf, text="TE Parts", variable=self.dxf_export_te).grid(row=row_idx, column=0, sticky=tk.W); row_idx += 1
        ttk.Checkbutton(tab_dxf, text="Carbon Ribs", variable=self.dxf_export_carbon).grid(row=row_idx, column=0, sticky=tk.W); row_idx += 1
        ttk.Checkbutton(tab_dxf, text="Stringers", variable=self.dxf_export_stringer).grid(row=row_idx, column=0, sticky=tk.W); row_idx += 1
        ttk.Button(tab_dxf, text="Export DXF", command=self.export_dxf).grid(row=row_idx, column=0, columnspan=2, pady=10)

        # Global buttons at the bottom of the left frame
        f_global = ttk.Frame(left_frame)
        f_global.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(f_global, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(f_global, text="Load Config", command=self.load_config).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(f_global, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(f_global, text="Calculate Weight", command=self.open_weight_window).pack(side=tk.LEFT, padx=5)

        # Right side: Plot
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)

        self.fig = Figure(figsize=(7, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=5)
        ttk.Label(control_frame, text="Select Rib to view:").pack(side=tk.LEFT)
        self.combo_rib = ttk.Combobox(control_frame, state="readonly")
        self.combo_rib.pack(side=tk.LEFT, padx=5)
        self.combo_rib.bind("<<ComboboxSelected>>", self.on_rib_select_full)
        ttk.Button(control_frame, text="Generate ALL", command=lambda: self.update_preview_full()).pack(side=tk.LEFT, padx=5)
        
        local_f = ttk.Frame(control_frame)
        local_f.pack(side=tk.RIGHT)
        ttk.Label(local_f, text="Angle (deg):").pack(side=tk.LEFT)
        self.local_angle_var = tk.StringVar(value="0")
        entry_ang = ttk.Entry(local_f, textvariable=self.local_angle_var, width=6)
        entry_ang.pack(side=tk.LEFT)
        entry_ang.bind("<Return>", self.apply_local_angle_full)
        ttk.Button(local_f, text="Apply", command=lambda: self.apply_local_angle_full(None)).pack(side=tk.LEFT)

        # Add traces
        for var in [self.file1_path, self.file2_path, self.chord_root, self.chord_tip, self.spar_pos_root,
                    self.plank_start, self.plank_end, self.plank_thick, self.plank_thick_tip,
                    self.edge_beam_width, self.beam_width, self.margin_spar, self.margin_bolt, self.margin_outer, self.truss_fillet,
                    self.front_spar_dia, self.rear_spar_dia, self.xbrace_dia, self.truss_front_n, self.truss_rear_n,
                    self.spar_hole_dia, self.safe_margin_var,
                    self.conn1_y, self.conn2_y, self.conn3_y, self.conn4_y,
                    self.te_cut, self.joint_length, self.min_hole_dia,
                    self.xb_start_a, self.xb_end_a, self.xb_start_b, self.xb_end_b, self.xb_start_c, self.xb_end_c,
                    self.plank_angle_offset,
                    self.te_cap_uf_act, self.te_cap_uf_w, self.te_cap_uf_d,
                    self.te_cap_lf_act, self.te_cap_lf_w, self.te_cap_lf_d,
                    self.diag1_active, self.diag1_y_main, self.diag1_y_rear,
                    self.diag2_active, self.diag2_y_main, self.diag2_y_rear,
                    self.root_bolt1_dia, self.root_bolt1_dx, self.root_bolt1_dy,
                    self.tip_bolt1_dia, self.tip_bolt1_dx, self.tip_bolt1_dy,
                    self.rib_thick]:
            try: var.trace_add("write", lambda *args: self.update_preview_fast())
            except Exception: pass

        for var in [self.wing_span, self.rib_sections]:
            try: var.trace_add("write", lambda *args: self.calculate_y_positions())
            except Exception: pass

    def browse_file(self, var, is_dxf=False):
        super().browse_file(var, is_dxf)
        self.update_preview_full()

    def calculate_y_positions(self):
        if getattr(self, 'is_updating_ui', False): return
        try:
            span, interval, joint = self.safe_float(self.wing_span), self.safe_float(self.rib_interval), self.safe_float(self.joint_length)
            if span <= 0 or interval <= 0: self.y_positions, self.combo_rib['values'] = [], []; return
            
            y_pos = []
            rem = span % interval
            if rem < 1e-3 or abs(interval - rem) < 1e-3: y_pos = list(np.arange(0, span + 1e-3, interval))
            else:
                edge = (rem + interval) / 2.0; y_pos.append(0.0)
                if span > edge:
                    y_pos.append(edge); curr = edge
                    while curr + interval < span - edge + 1e-3: curr += interval; y_pos.append(curr)
                if abs(y_pos[-1] - span) > 1e-3: y_pos.append(span)
                    
            self.y_positions = y_pos
            
            items = []
            for i, y in enumerate(self.y_positions):
                items.append({'type': 'rib', 'idx': i, 'y_local': y, 'label': f"Rib {i} (Y={y + joint:.1f}mm)"})
                
            if self.cr_root_in_act.get() and len(self.y_positions) > 0: items.append({'type': 'carbon', 'loc': 'root', 'pos': 'inner', 'idx': 0, 'y_local': self.y_positions[0], 'label': f"C-Rib Root Inner (Y={self.y_positions[0] + joint:.1f}mm)"})
            if self.cr_root_out_act.get() and len(self.y_positions) > 0: items.append({'type': 'carbon', 'loc': 'root', 'pos': 'outer', 'idx': 0, 'y_local': self.y_positions[0], 'label': f"C-Rib Root Outer (Y={self.y_positions[0] + joint:.1f}mm)"})
            if self.cr_tip_in_act.get() and len(self.y_positions) > 0: items.append({'type': 'carbon', 'loc': 'tip', 'pos': 'inner', 'idx': len(self.y_positions)-1, 'y_local': self.y_positions[-1], 'label': f"C-Rib Tip Inner (Y={self.y_positions[-1] + joint:.1f}mm)"})
            if self.cr_tip_out_act.get() and len(self.y_positions) > 0: items.append({'type': 'carbon', 'loc': 'tip', 'pos': 'outer', 'idx': len(self.y_positions)-1, 'y_local': self.y_positions[-1], 'label': f"C-Rib Tip Outer (Y={self.y_positions[-1] + joint:.1f}mm)"})
            
            self.preview_items = items
            c_values = [item['label'] for item in items]
            self.combo_rib['values'] = c_values
            
            if hasattr(self, 'combo_foam_start'):
                rib_only_values = [item['label'] for item in items if item['type'] == 'rib']
                self.combo_foam_start['values'] = rib_only_values
                self.combo_foam_end['values'] = rib_only_values
                
            if len(c_values) > 0:
                current = self.current_rib_idx.get()
                if current >= len(c_values): current = len(c_values) - 1
                self.combo_rib.current(current); self.current_rib_idx.set(current)
                
                if hasattr(self, 'combo_foam_start'):
                    if self.combo_foam_start.current() < 0: self.combo_foam_start.current(0)
                    if self.combo_foam_end.current() < 0: self.combo_foam_end.current(len(c_values)-1)
                    
            self.on_rib_select_fast(None)
        except Exception: pass

    def open_in_foam_cam(self):
        idx_start = self.combo_foam_start.current()
        idx_end = self.combo_foam_end.current()
        if idx_start < 0 or idx_end < 0: return messagebox.showerror("Error", "Please select valid start and end ribs.")
        if not self.file1_path.get() or not self.file2_path.get(): return messagebox.showerror("Error", "Please load Airfoil profiles first.")
        
        target = self.foam_target.get()
        
        def get_poly(idx):
            y_local = self.y_positions[idx]
            t_rib = self.safe_float(self.rib_thick)
            p = self._get_builder_params()
            p['fast_mode'] = True
            res = self.engine.generate_rib_at_y(p, y_local, idx, t_rib)
            poly = res.plank_poly_rot if target == "Plank" else res.te_part_coords
            return poly, res.c_m

        try:
            poly1, c_m1 = get_poly(idx_start)
            poly2, c_m2 = get_poly(idx_end)
            
            if len(poly1) == 0 or len(poly2) == 0:
                messagebox.showerror("Error", f"Could not extract {target} polygon. Ensure its settings (Thickness/TE Cut) are configured.")
                return
                
            if idx_start <= idx_end:
                poly_root, c_m_root, poly_tip, c_m_tip = poly1, c_m1, poly2, c_m2
            else:
                poly_root, c_m_root, poly_tip, c_m_tip = poly2, c_m2, poly1, c_m1
                idx_start, idx_end = idx_end, idx_start
                
            temp_root = os.path.abspath(f"temp_foam_{target.replace(' ', '')}_Root.dxf")
            temp_tip = os.path.abspath(f"temp_foam_{target.replace(' ', '')}_Tip.dxf")
            
            self.engine.export_single_poly_dxf(temp_root, poly_root, c_m_root)
            self.engine.export_single_poly_dxf(temp_tip, poly_tip, c_m_tip)
            
            calc_width = abs(self.y_positions[idx_end] - self.y_positions[idx_start])
            if calc_width < 1.0: calc_width = 910.0
            
            from ui.foam_mode import FoamCutterGUI
            top = tk.Toplevel(self.root)
            FoamCutterGUI(top, root_file=temp_root, tip_file=temp_tip, block_width=calc_width, wing_type=self.wing_type.get())
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def auto_set_xbrace_zones(self):
        vals = []
        for v in [self.conn1_y, self.conn2_y, self.conn3_y, self.conn4_y]:
            try:
                val_str = v.get().strip()
                if val_str: vals.append(float(val_str))
            except ValueError: pass
        vals.sort()
        if len(vals) >= 2:
            self.xb_start_a.set(str(vals[0])); self.xb_end_a.set(str(vals[1]))
            if len(vals) >= 3:
                self.xb_start_b.set(str(vals[1])); self.xb_end_b.set(str(vals[2]))
            else:
                self.xb_start_b.set(""); self.xb_end_b.set("")
            if len(vals) >= 4:
                self.xb_start_c.set(str(vals[2])); self.xb_end_c.set(str(vals[3]))
            else:
                self.xb_start_c.set(""); self.xb_end_c.set("")
        self.update_preview_full()

    def on_rib_select_fast(self, event):
        idx = self.combo_rib.current()
        if idx >= 0 and hasattr(self, 'preview_items') and idx < len(self.preview_items):
            self.current_rib_idx.set(idx)
            angle = self.truss_angles_dict.get(self.preview_items[idx]['idx'], self.safe_float(self.base_truss_angle))
            was_updating = getattr(self, 'is_updating_ui', False)
            self.is_updating_ui = True; self.local_truss_angle.set(str(angle)); self.is_updating_ui = was_updating
            self.update_preview_fast()

    def on_rib_select_full(self, event):
        idx = self.combo_rib.current()
        if idx >= 0 and hasattr(self, 'preview_items') and idx < len(self.preview_items):
            self.current_rib_idx.set(idx)
            angle = self.truss_angles_dict.get(self.preview_items[idx]['idx'], self.safe_float(self.base_truss_angle))
            was_updating = getattr(self, 'is_updating_ui', False)
            self.is_updating_ui = True; self.local_truss_angle.set(str(angle)); self.is_updating_ui = was_updating
            self.update_preview_full()

    def apply_local_angle_full(self, event):
        idx = self.current_rib_idx.get()
        if hasattr(self, 'preview_items') and idx < len(self.preview_items):
            real_idx = self.preview_items[idx]['idx']
            new_angle = self.safe_float(self.local_truss_angle)
            self.truss_angles_dict[real_idx] = new_angle; self.update_preview_full()

    def get_local_params(self, y_local):
        p = self._get_builder_params()
        return self.engine.get_local_params(p, y_local)

    def update_preview_fast(self, *args): self.update_preview(fast_mode=True)
    def update_preview_full(self, *args): self.update_preview(fast_mode=False)

    def update_preview(self, fast_mode=False):
        if self.is_updating_ui: return
        if not self.file1_path.get() or not self.file2_path.get() or not hasattr(self, 'preview_items'): return
        item_idx = self.current_rib_idx.get()
        if item_idx >= len(self.preview_items): return
        
        item = self.preview_items[item_idx]
        is_carbon = (item['type'] == 'carbon')
        idx = item['idx']
        
        y_local = item['y_local']
        t_rib = self.safe_float(self.cr_thick) if is_carbon else self.safe_float(self.rib_thick)
        te_cut_val = self.safe_float(self.te_cut)
        
        if is_carbon:
            if item['loc'] == 'root' and item['pos'] == 'inner' and not self.cr_root_in_te.get(): te_cut_val = 0.0
            if item['loc'] == 'root' and item['pos'] == 'outer' and not self.cr_root_out_te.get(): te_cut_val = 0.0
            if item['loc'] == 'tip' and item['pos'] == 'inner' and not self.cr_tip_in_te.get(): te_cut_val = 0.0
            if item['loc'] == 'tip' and item['pos'] == 'outer' and not self.cr_tip_out_te.get(): te_cut_val = 0.0

        try:
            p = self._get_builder_params()
            p['fast_mode'] = fast_mode
            res = self.engine.generate_rib_at_y(p, y_local, idx, t_rib, is_carbon=is_carbon, te_cut_override=te_cut_val)
            self.last_warnings = res.warnings_list
            chord, spar_pct, washout, blend, local_xb_pct, x_dia = self.get_local_params(y_local)
            angle = p['truss_angles_dict'].get(idx, p['base_truss_angle'])
            title = f"{item['label']} - Chord: {chord:.1f}mm, Washout: {washout:.2f}°, Truss: {angle:.1f}°" + (" [FAST PREVIEW]" if fast_mode else "")
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
        if not self.y_positions: return messagebox.showerror("Error", "No rib positions generated. Check span and interval.")
            
        dir_path = filedialog.askdirectory(title="Select Output Directory for Wing DXFs")
        if not dir_path: return

        try:
            # UIからすべてのパラメータを収集
            params = self._get_builder_params()

            # WingDXFExporterのインスタンスを作成し、エクスポートを実行
            exporter = WingDXFExporter(self.engine, params)
            exported_count = exporter.export_all_ribs(dir_path)

            messagebox.showinfo("Success", f"Exported {exported_count} ribs to:\n{dir_path}")
        except Exception as e: messagebox.showerror("Export Error", str(e))

    def open_weight_window(self):
        """重量計算ウインドウを開く"""
        try:
            params = self._get_builder_params()
        except Exception as e:
            params = {}
        from ui.weight_window import WeightWindow
        WeightWindow(self.root, self.engine, params)

    def export_obj(self):
        f1, f2 = self.file1_path.get(), self.file2_path.get()
        if not f1 or not f2 or not os.path.exists(f1) or not os.path.exists(f2): return messagebox.showerror("Error", "Please select valid files.")
        if not self.y_positions: return messagebox.showerror("Error", "No rib positions generated. Check span and interval.")
            
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
            params = self._get_builder_params()
            params['tabs_active'] = False
            
            # Wing3DBuilderのインスタンスを作成し、エクスポートを実行
            builder = Wing3DBuilder(self.engine, params)
            builder.build_and_export(filepath)

            messagebox.showinfo("Success", f"Exported 3D Model to:\n{filepath}")

        except Exception as e: messagebox.showerror("Export Error", str(e))

    def _get_builder_params(self):
        """3DビルダーやDXFエクスポーターに渡すためのパラメータを辞書として収集・整理する"""

        # X-Brace Zones
        xb_zones = []
        for s_var, e_var in [(self.xb_start_a, self.xb_end_a), (self.xb_start_b, self.xb_end_b), (self.xb_start_c, self.xb_end_c)]:
            try:
                s_str, e_str = s_var.get().strip(), e_var.get().strip()
                if s_str and e_str:
                    xb_zones.append((float(s_str), float(e_str), 0.0))  # No offset in batch mode
            except Exception:
                pass

        # Connectors
        connectors = []
        for y_v in [self.conn1_y, self.conn2_y, self.conn3_y, self.conn4_y]:
            y_str = y_v.get().strip()
            if y_str:
                try: connectors.append((float(y_str), "V-Shape")) # hardcoded to V-Shape for now since type UI was removed
                except ValueError: pass

        # Carbon Rib Configs
        carbon_rib_configs = [
            {'loc': 'root', 'pos': 'inner', 'idx': 0, 'act': getattr(self, 'cr_root_in_act', tk.BooleanVar(value=False)).get(), 'te': getattr(self, 'cr_root_in_te', tk.BooleanVar(value=False)).get()},
            {'loc': 'root', 'pos': 'outer', 'idx': 0, 'act': getattr(self, 'cr_root_out_act', tk.BooleanVar(value=False)).get(), 'te': getattr(self, 'cr_root_out_te', tk.BooleanVar(value=False)).get()},
            {'loc': 'tip', 'pos': 'inner', 'idx': len(self.y_positions)-1, 'act': getattr(self, 'cr_tip_in_act', tk.BooleanVar(value=False)).get(), 'te': getattr(self, 'cr_tip_in_te', tk.BooleanVar(value=False)).get()},
            {'loc': 'tip', 'pos': 'outer', 'idx': len(self.y_positions)-1, 'act': getattr(self, 'cr_tip_out_act', tk.BooleanVar(value=False)).get(), 'te': getattr(self, 'cr_tip_out_te', tk.BooleanVar(value=False)).get()},
        ]

        # Diagonal Spars
        diag1_ym, diag1_yr = self.safe_float(self.diag1_y_main), self.safe_float(self.diag1_y_rear)
        diag2_ym, diag2_yr = self.safe_float(self.diag2_y_main), self.safe_float(self.diag2_y_rear)

        # Tab Support params handling for compatibility
        truss_tab_width = self.safe_float(self.truss_tab_width, 4.0)
        ms_tab_w, ms_tab_d = 4.0, 10.0
        try: ms_tab_w = self.safe_float(self.main_spar_tab_width, 4.0)
        except Exception: pass
        try: ms_tab_d = self.safe_float(self.main_spar_tab_dist, 10.0)
        except Exception: pass

        return {
            'file1': self.file1_path.get(), 'file2': self.file2_path.get(), 'y_positions': self.y_positions,
            'truss_angles_dict': getattr(self, 'truss_angles_dict', {}), 'stringers_data': getattr(self, 'get_stringers_data', lambda: [])(),
            'wing_type': getattr(self, 'wing_type', tk.StringVar(value="Linear")).get(),
            **{k: self.safe_float(getattr(self, k)) for k in ['joint_length', 'wing_span', 'chord_root', 'chord_tip', 'spar_pos_root', 'spar_pos_tip', 'washout_root', 'washout_tip', 'spar_hole_dia', 'front_spar_dx', 'front_spar_dy', 'front_spar_dia', 'rear_spar_dx', 'rear_spar_dy', 'rear_spar_dia', 'plank_start', 'plank_end', 'plank_thick', 'plank_part_start', 'plank_part_end', 'te_cut', 'beam_width', 'edge_beam_width', 'margin_spar', 'margin_bolt', 'margin_outer', 'margin_outer_edge', 'base_truss_angle', 'truss_fillet', 'min_hole_dia', 'xbrace_dia', 'rib_thick', 'cr_thick', 'te_cap_thick', 'rc1_start', 'rc1_end', 'rc1_thick', 'rc1_width', 'rc2_start', 'rc2_end', 'rc2_thick', 'rc2_width'] if hasattr(self, k)},
            **{k: self.safe_int(getattr(self, k)) for k in ['truss_front_n', 'truss_rear_n'] if hasattr(self, k)},
            **{k: getattr(self, k).get() for k in ['safe_margin_var', 'te_cap_uf_act', 'te_cap_lf_act', 'te_cap_ur_act', 'te_cap_lr_act', 'rc1_act', 'rc2_act', 'diag1_active', 'diag2_active'] if hasattr(self, k)},
            **{k: getattr(self, k).get() for k in ['export_main_spar', 'export_front_spar', 'export_rear_spar', 'export_plank', 'export_te', 'export_connectors', 'export_stringers', 'export_xbrace_wires', 'export_diag_spars', 'export_carbon_ribs', 'export_te_caps', 'export_rib_caps', 'export_film'] if hasattr(self, k)},
            **{f'mat_{k}': getattr(self, f'mat_{k}').get() for k in ['ribs', 'main_spar', 'front_spar', 'rear_spar', 'plank', 'te', 'connectors', 'stringers', 'xbrace_wires', 'diag_spars', 'carbon_ribs', 'te_caps', 'rib_caps', 'film'] if hasattr(self, f'mat_{k}')},
            'main_spar_inner_dia': self.safe_float(self.main_spar_inner_dia),
            'front_spar_inner_dia': self.safe_float(self.front_spar_inner_dia),
            'rear_spar_inner_dia': self.safe_float(self.rear_spar_inner_dia),
            'xbrace_wire_dia': getattr(self, 'safe_float')(getattr(self, 'xbrace_wire_dia', tk.StringVar(value="28.0"))),
            'bolt_spacer_inner_dia': self.safe_float(getattr(self, 'bolt_spacer_inner_dia', tk.StringVar(value="4.0"))),
            'bolt_spacer_length': self.safe_float(getattr(self, 'bolt_spacer_length', tk.StringVar(value="10.0"))),
            'root_bolt1': (self.safe_float(self.root_bolt1_dx), self.safe_float(self.root_bolt1_dy), self.safe_float(self.root_bolt1_dia)) if hasattr(self, 'root_bolt1_dx') else (0,0,0),
            'root_bolt2': (self.safe_float(self.root_bolt2_dx), self.safe_float(self.root_bolt2_dy), self.safe_float(self.root_bolt2_dia)) if hasattr(self, 'root_bolt2_dx') else (0,0,0),
            'tip_bolt1': (self.safe_float(self.tip_bolt1_dx), self.safe_float(self.tip_bolt1_dy), self.safe_float(self.tip_bolt1_dia)) if hasattr(self, 'tip_bolt1_dx') else (0,0,0),
            'tip_bolt2': (self.safe_float(self.tip_bolt2_dx), self.safe_float(self.tip_bolt2_dy), self.safe_float(self.tip_bolt2_dia)) if hasattr(self, 'tip_bolt2_dx') else (0,0,0),
            'xb_zones': xb_zones, 'connectors': connectors, 'carbon_rib_configs': carbon_rib_configs,
            'diag1_y_main': diag1_ym, 'diag1_y_rear': diag1_yr, 'diag1_range': (min(diag1_ym, diag1_yr), max(diag1_ym, diag1_yr)) if abs(diag1_yr - diag1_ym) > 1e-5 else (-1,-1),
            'diag2_y_main': diag2_ym, 'diag2_y_rear': diag2_yr, 'diag2_range': (min(diag2_ym, diag2_yr), max(diag2_ym, diag2_yr)) if abs(diag2_yr - diag2_ym) > 1e-5 else (-1,-1),
            'te_cap_uf_w': getattr(self, 'safe_float')(getattr(self, 'te_cap_uf_w', tk.StringVar(value="0.0"))), 
            'te_cap_lf_w': getattr(self, 'safe_float')(getattr(self, 'te_cap_lf_w', tk.StringVar(value="0.0"))),
            'te_cap_ur_w': getattr(self, 'safe_float')(getattr(self, 'te_cap_ur_w', tk.StringVar(value="0.0"))),
            'te_cap_lr_w': getattr(self, 'safe_float')(getattr(self, 'te_cap_lr_w', tk.StringVar(value="0.0"))),
            'tabs_active': getattr(self, 'tabs_active', tk.BooleanVar(value=False)).get(),
            'truss_tab_width': truss_tab_width,
            'main_spar_support_w': ms_tab_w,
            'main_spar_support_h': ms_tab_d,
            'main_spar_support_thick': 3.0,
            'tab_thickness': getattr(self, 'safe_float')(getattr(self, 'tab_depth', tk.StringVar(value="3.0")), 3.0),
        }

    def export_gcode_all(self):
        f1, f2 = self.file1_path.get(), self.file2_path.get()
        if not f1 or not f2 or not os.path.exists(f1) or not os.path.exists(f2): return messagebox.showerror("Error", "Please select valid files.")
        if not self.y_positions: return messagebox.showerror("Error", "No rib positions generated. Check span and interval.")
            
        dir_path = filedialog.askdirectory(title="Select Output Directory for Wing G-Codes")
        if not dir_path: return

        try:
            params = self._get_builder_params()
            from core.cam_engine import SpindleCAMEngine
            cam = SpindleCAMEngine()
            
            exported_count = 0
            all_warnings = []
            
            # 1. Export Normal Ribs G-code
            for i, y_local in enumerate(params['y_positions']):
                res = self.engine.generate_rib_at_y(params, y_local, i, params['rib_thick'])
                gcode_str, warnings = cam.generate_gcode(res, params)
                
                y_global = y_local + params['joint_length']
                filename = f"Rib_{i:02d}_Y{y_global:.1f}.gcode"
                filepath = os.path.join(dir_path, filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(gcode_str)
                
                if warnings:
                    all_warnings.extend([f"Rib {i}: {w}" for w in warnings])
                exported_count += 1

            # 2. Export Carbon Ribs G-code
            for cconf in params['carbon_rib_configs']:
                if not cconf['act']: continue
                idx, y_local = cconf['idx'], params['y_positions'][cconf['idx']]
                
                te_cut_override = params['te_cut'] if cconf['te'] else 0.0
                res = self.engine.generate_rib_at_y(params, y_local, idx, params['cr_thick'], is_carbon=True, te_cut_override=te_cut_override)
                gcode_str, warnings = cam.generate_gcode(res, params)
                
                y_global = y_local + params['joint_length']
                filename = f"CarbonRib_{cconf['loc'].capitalize()}_{cconf['pos'].capitalize()}_Y{y_global:.1f}.gcode"
                filepath = os.path.join(dir_path, filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(gcode_str)
                
                if warnings:
                    all_warnings.extend([f"CarbonRib {cconf['loc']}_{cconf['pos']}: {w}" for w in warnings])
                exported_count += 1

            if all_warnings:
                msg = f"Exported {exported_count} G-code files with warnings:\n\n" + "\n".join(all_warnings[:20])
                if len(all_warnings) > 20:
                    msg += f"\n... and {len(all_warnings) - 20} more warnings."
                messagebox.showwarning("Export Warning", msg)
            else:
                messagebox.showinfo("Success", f"Exported {exported_count} G-code files to:\n{dir_path}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Export Error", str(e))
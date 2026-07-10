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
        super().__init__(root)
        from core.engine import RibGeneratorEngine
        self.engine = RibGeneratorEngine()
        from ui.param_spec import BATCH_PARAMS
        from ui.ui_builder import ParameterManager, UIBuilder
        self.pm = ParameterManager(self, BATCH_PARAMS)
        self.ui_builder = UIBuilder(self.pm)
        self.str_vars = {}
        for name in ["A", "B", "C", "D", "E"]:
            import tkinter as tk
            self.str_vars[name] = {'active': tk.BooleanVar(value=False), 'pos': tk.StringVar(), 'w': tk.StringVar(), 'd': tk.StringVar(), 'use_dxf': tk.BooleanVar(), 'dxf': tk.StringVar()}
        

        import tkinter as tk
        self.y_positions = []
        self.truss_angles_dict = {}
        self.current_rib_idx = tk.IntVar(value=0)
        self.local_truss_angle = tk.StringVar(value="60.0")
        self.last_warnings = []
        self.is_updating_ui = False
        self.preview_items = []
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
        """3DビルダーやDXFエクスポーターに渡すためのパラメータを辞書として収集・整理する"""

        import tkinter as tk
        xb_zones = []
        xb_offset = self.safe_float(getattr(self, 'xbrace_offset', tk.StringVar(value='0.0')))
        for s_var, e_var in [(self.xb_start_a, self.xb_end_a), (self.xb_start_b, self.xb_end_b), (self.xb_start_c, self.xb_end_c)]:
            try:
                s_str, e_str = s_var.get().strip(), e_var.get().strip()
                if s_str and e_str:
                    xb_zones.append((float(s_str), float(e_str), xb_offset))
            except Exception:
                pass

        # Joint Sleeves
        joint_sleeves = []
        for i in [1, 2]:
            act_var = getattr(self, f'js{i}_act', tk.BooleanVar(value=False))
            if act_var.get():
                joint_sleeves.append({
                    'type': getattr(self, f'js{i}_type', tk.StringVar(value='Foam+Cap')).get(),
                    'start': self.safe_float(getattr(self, f'js{i}_start')),
                    'end': self.safe_float(getattr(self, f'js{i}_end')),
                    'out_dia': self.safe_float(getattr(self, f'js{i}_out_dia')),
                    't1': self.safe_float(getattr(self, f'js{i}_t1')),
                    't2': self.safe_float(getattr(self, f'js{i}_t2')),
                })

        # Connectors
        connectors = []
        for y_v, t_v in zip([self.conn1_y, self.conn2_y, self.conn3_y, self.conn4_y], 
                            [self.conn1_type, self.conn2_type, self.conn3_type, self.conn4_type]):
            y_str = y_v.get().strip()
            if y_str:
                try: connectors.append((float(y_str), t_v.get().strip()))
                except ValueError: pass

        # Carbon Rib Configs
        carbon_rib_configs = [
            {'loc': 'root', 'pos': 'inner', 'idx': 0, 'act': getattr(self, 'cr_root_in_act', tk.BooleanVar(value=False)).get(), 'te': True},
            {'loc': 'root', 'pos': 'outer', 'idx': 0, 'act': getattr(self, 'cr_root_out_act', tk.BooleanVar(value=False)).get(), 'te': getattr(self, 'cr_root_out_te', tk.BooleanVar(value=False)).get()},
            {'loc': 'tip', 'pos': 'inner', 'idx': len(self.y_positions)-1, 'act': getattr(self, 'cr_tip_in_act', tk.BooleanVar(value=False)).get(), 'te': True},
            {'loc': 'tip', 'pos': 'outer', 'idx': len(self.y_positions)-1, 'act': getattr(self, 'cr_tip_out_act', tk.BooleanVar(value=False)).get(), 'te': getattr(self, 'cr_tip_out_te', tk.BooleanVar(value=False)).get()},
        ]

        # Diagonal Spars
        diag1_ym, diag1_yr = self.safe_float(self.diag1_y_main), self.safe_float(self.diag1_y_rear)
        diag2_ym, diag2_yr = self.safe_float(self.diag2_y_main), self.safe_float(self.diag2_y_rear)

        # Tab Support params handling for compatibility
        truss_tab_width = self.safe_float(self.truss_tab_width, 4.0)
        ms_tab_w = self.safe_float(self.main_spar_support_w, 4.0) if hasattr(self, 'main_spar_support_w') else 4.0
        ms_tab_d = self.safe_float(self.main_spar_support_h, 10.0) if hasattr(self, 'main_spar_support_h') else 10.0
        ms_tab_thick = self.safe_float(self.main_spar_support_thick, 3.0) if hasattr(self, 'main_spar_support_thick') else 3.0
        
        wing_name = getattr(self, 'wing_name', tk.StringVar(value='')).get().strip().replace('/', '_').replace('\\', '_')

        return {
            'file1': os.path.abspath(self.file1_path.get()) if self.file1_path.get() else '', 
            'file2': os.path.abspath(self.file2_path.get()) if self.file2_path.get() else '', 
            'y_positions': self.y_positions,
            'truss_angles_dict': getattr(self, 'truss_angles_dict', {}), 'stringers_data': getattr(self, 'get_stringers_data', lambda: [])(),
            'wing_type': getattr(self, 'wing_type', tk.StringVar(value="Linear")).get(),
            'wing_name': wing_name,
            **{k: self.safe_float(getattr(self, k)) for k in ['joint_length', 'wing_span', 'chord_root', 'chord_tip', 'spar_pos_root', 'spar_pos_tip', 'washout_root', 'washout_tip', 'base_aoa', 'plank_start', 'plank_end', 'plank_thick', 'plank_part_start', 'plank_part_end', 'te_cut', 'beam_width', 'edge_beam_width', 'margin_spar', 'margin_bolt', 'margin_outer', 'margin_outer_edge', 'base_truss_angle', 'truss_fillet', 'min_hole_dia', 'xbrace_offset', 'rib_thick', 'cr_thick', 'te_cap_thick', 'rc1_start', 'rc1_end', 'rc1_thick', 'rc1_width', 'rc2_start', 'rc2_end', 'rc2_thick', 'rc2_width', 'le_interp_range', 'le_interp_divisions'] if hasattr(self, k)},
            **{k: self.safe_float(getattr(self, k), default=None) for k in ['front_spar_dx', 'front_spar_dy', 'front_spar_dx_root', 'front_spar_dy_root', 'front_spar_dx_tip', 'front_spar_dy_tip', 'rear_spar_dx_root', 'rear_spar_dy_root', 'rear_spar_dx_tip', 'rear_spar_dy_tip', 'rear_spar_dx', 'rear_spar_dy'] if hasattr(self, k)},
            **{k: self.safe_float(getattr(self, k), default=-1.0) for k in ['spar_hole_dia', 'spar_hole_dv', 'front_spar_dia', 'rear_spar_dia', 'xbrace_dia', 'xbrace_wire_dia'] if hasattr(self, k)},
            **{k: self.safe_int(getattr(self, k)) for k in ['truss_front_n', 'truss_rear_n'] if hasattr(self, k)},
            **{k: self.pm.vars[k].get() for k in ['safe_margin_var', 'te_cap_uf_act', 'te_cap_lf_act', 'te_cap_ur_act', 'te_cap_lr_act', 'rc1_act', 'rc2_act', 'diag1_active', 'diag2_active', 'jig_y_positions', 'jig_base_height', 'jig_base_thickness', 'jig_wall_thickness', 'jig_pillar_angle', 'jig_te_stopper_height', 'jig_slot_interval', 'jig_slot_width', 'jig_slot_depth', 'dxf_layer_rib_outline', 'dxf_layer_holes', 'dxf_layer_truss', 'dxf_layer_plank', 'dxf_layer_te_part', 'dxf_layer_jig_outline', 'dxf_all_in_one', 'le_interp_active'] if k in self.pm.vars},
            'dxf_selections': {k: v.get() for k, v in getattr(self, 'dxf_selection_vars', {}).items()},
            **{k: getattr(self, k).get() for k in ['export_main_spar', 'export_front_spar', 'export_rear_spar', 'export_plank', 'export_te', 'export_connectors', 'export_stringers', 'export_xbrace_wires', 'export_diag_spars', 'export_carbon_ribs', 'export_te_caps', 'export_rib_caps', 'export_film', 'export_joint_sleeves'] if hasattr(self, k)},
            **{f'mat_{k}': getattr(self, f'mat_{k}').get() for k in ['ribs', 'main_spar', 'front_spar', 'rear_spar', 'plank', 'te', 'connectors', 'stringers', 'xbrace_wires', 'diag_spars', 'carbon_ribs', 'te_caps', 'rib_caps', 'film', 'js_cap', 'js_foam', 'js_skin'] if hasattr(self, f'mat_{k}')},
            'main_spar_inner_dia': self.safe_float(self.main_spar_inner_dia),
            'front_spar_inner_dia': self.safe_float(self.front_spar_inner_dia),
            'rear_spar_inner_dia': self.safe_float(self.rear_spar_inner_dia),
            'xbrace_wire_dia': getattr(self, 'safe_float')(getattr(self, 'xbrace_wire_dia', tk.StringVar(value="28.0"))),
            'bolt_spacer_inner_dia': self.safe_float(getattr(self, 'bolt_spacer_inner_dia', tk.StringVar(value="4.0"))),
            'bolt_spacer_length': self.safe_float(getattr(self, 'bolt_spacer_length', tk.StringVar(value="10.0"))),
            'root_bolt1': (self.safe_float(self.root_bolt1_dx, default=None), self.safe_float(self.root_bolt1_dy, default=None), self.safe_float(self.root_bolt1_dia, default=-1.0)) if hasattr(self, 'root_bolt1_dx') else (0,0,-1.0),
            'root_bolt2': (self.safe_float(self.root_bolt2_dx, default=None), self.safe_float(self.root_bolt2_dy, default=None), self.safe_float(self.root_bolt2_dia, default=-1.0)) if hasattr(self, 'root_bolt2_dx') else (0,0,-1.0),
            'tip_bolt1': (self.safe_float(self.tip_bolt1_dx, default=None), self.safe_float(self.tip_bolt1_dy, default=None), self.safe_float(self.tip_bolt1_dia, default=-1.0)) if hasattr(self, 'tip_bolt1_dx') else (0,0,-1.0),
            'tip_bolt2': (self.safe_float(self.tip_bolt2_dx, default=None), self.safe_float(self.tip_bolt2_dy, default=None), self.safe_float(self.tip_bolt2_dia, default=-1.0)) if hasattr(self, 'tip_bolt2_dx') else (0,0,-1.0),
            'xb_zones': xb_zones, 'connectors': connectors, 'carbon_rib_configs': carbon_rib_configs, 'joint_sleeves': joint_sleeves,
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
            'main_spar_support_thick': ms_tab_thick,
            'tab_thickness': getattr(self, 'safe_float')(getattr(self, 'tab_thickness', tk.StringVar(value="3.0")), 3.0),
            'outer_tab_width': getattr(self, 'safe_float')(getattr(self, 'outer_tab_width', tk.StringVar(value="6.0")), 6.0),
            'outer_tab_interval': getattr(self, 'safe_float')(getattr(self, 'outer_tab_interval', tk.StringVar(value="100.0")), 100.0),
            'tab_angle_deg': getattr(self, 'safe_float')(getattr(self, 'tab_angle_deg', tk.StringVar(value="45.0")), 45.0),
            'tab_exclusion_stringer': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_stringer', tk.StringVar(value="10.0")), 10.0),
            'tab_exclusion_le_te': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_le_te', tk.StringVar(value="30.0")), 30.0),
            'cam_tool_dia': getattr(self, 'safe_float')(getattr(self, 'cam_tool_dia', tk.StringVar(value="2.0")), 2.0),
            'cam_mat_thick': getattr(self, 'safe_float')(getattr(self, 'cam_mat_thick', tk.StringVar(value="10.0")), 10.0),
            'cam_safe_z': getattr(self, 'safe_float')(getattr(self, 'cam_safe_z', tk.StringVar(value="5.0")), 5.0),
            'cam_feed_rate': getattr(self, 'safe_float')(getattr(self, 'cam_feed_rate', tk.StringVar(value="2000")), 2000.0),
            'cam_spindle_speed': getattr(self, 'safe_float')(getattr(self, 'cam_spindle_speed', tk.StringVar(value="12000")), 12000.0),
            'cam_extra_depth': getattr(self, 'safe_float')(getattr(self, 'cam_extra_depth', tk.StringVar(value="0.5")), 0.5),
            'cam_milling_dir': getattr(self, 'cam_milling_dir', tk.StringVar(value="Conventional (Outer CW)")).get(),
            'spar_bridge_padding': getattr(self, 'safe_float')(getattr(self, 'spar_bridge_padding', tk.StringVar(value="0.5")), 0.5),
            'spar_bridge_thickness': getattr(self, 'safe_float')(getattr(self, 'spar_bridge_thickness', tk.StringVar(value="3.0")), 3.0),
        }

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
        self.create_stringers_ui(self.pm.obj.tabs_frames['プランク・後縁'])
        if hasattr(self, 'create_cam_ui'):
            self.create_cam_ui(notebook)
            

        

        if '翼全体' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['翼全体'], text="Generate Positions", command=self.calculate_y_positions).pack(fill=tk.X, padx=10, pady=5)

        if 'Xブレース' in self.pm.obj.groups_frames:
            ttk.Button(self.pm.obj.groups_frames['Xブレース'], text="自動設定", command=self.auto_set_xbrace_zones).grid(row=99, column=0, columnspan=4, pady=5)
            
        if 'CNC' in self.pm.obj.tabs_frames:
            self.create_cnc_selection_ui(self.pm.obj.tabs_frames['CNC'])
            ttk.Button(self.pm.obj.tabs_frames['CNC'], text="Export G-Code", command=self.export_gcode_all).pack(fill=tk.X, padx=10, pady=5)
            
        if 'Foam' in self.pm.obj.tabs_frames:
            f_tab = self.pm.obj.tabs_frames['Foam']
            lf = ttk.LabelFrame(f_tab, text="切り出し範囲")
            lf.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(lf, text="開始リブ:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
            self.combo_foam_start = ttk.Combobox(lf, state="readonly", width=25)
            self.combo_foam_start.grid(row=0, column=1, padx=5, pady=2, sticky="w")
            
            ttk.Label(lf, text="終了リブ:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
            self.combo_foam_end = ttk.Combobox(lf, state="readonly", width=25)
            self.combo_foam_end.grid(row=1, column=1, padx=5, pady=2, sticky="w")
            
            ttk.Button(f_tab, text="Foam CAMを開く", command=self.open_in_foam_cam).pack(fill=tk.X, padx=10, pady=5)
            
        if 'DXF' in self.pm.obj.tabs_frames:
            self.create_dxf_selection_ui(self.pm.obj.tabs_frames['DXF'])
            ttk.Button(self.pm.obj.tabs_frames['DXF'], text="Export DXF", command=self.export_dxf).pack(fill=tk.X, padx=10, pady=5)

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
        self.combo_rib = ttk.Combobox(control_frame, state="readonly", width=40)
        self.combo_rib.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.combo_rib.bind("<<ComboboxSelected>>", self.on_rib_select_fast)
        
        ttk.Button(control_frame, text="Generate ALL", command=lambda: self.update_preview_full()).pack(side=tk.LEFT, padx=5)
        
        angle_frame = ttk.Frame(lf_preview)
        angle_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(angle_frame, text="Local Angle Override:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(angle_frame, textvariable=self.local_truss_angle, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(angle_frame, text="Apply Local Angle", command=self.apply_local_angle_full).pack(side=tk.LEFT, padx=5)
        
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.fig = Figure(figsize=(7, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=lf_preview)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        for name, var in self.pm.vars.items():
            if hasattr(var, 'trace_add'):
                try:
                    var.trace_add("write", lambda *args: self.update_preview_fast())
                except: pass

        notebook.bind("<<NotebookTabChanged>>", lambda e: [self.calculate_y_positions(), self.update_preview_full()]) if hasattr(self, 'combo_rib') else None

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
            
            
            try:
                jig_str = self.pm.vars.get('jig_y_positions').get() if 'jig_y_positions' in self.pm.vars else ''
                if jig_str:
                    jigs = [float(v.strip()) for v in jig_str.split(',') if v.strip()]
                    for j_idx, jy in enumerate(jigs):
                        # Find closest rib index (or just assign a dummy idx)
                        # We use idx to get truss_angles_dict.
                        # It's better to find closest rib index to use its truss angle.
                        closest_idx = 0
                        min_dist = 99999
                        for r_idx, ry in enumerate(self.y_positions):
                            if abs(ry - jy) < min_dist:
                                min_dist = abs(ry - jy)
                                closest_idx = r_idx
                        items.append({'type': 'jig', 'idx': closest_idx, 'jig_idx': j_idx, 'y_local': jy, 'label': f"Jig {j_idx} (Y={jy + joint:.1f}mm)"})
            except Exception as e: print("Jig preview extraction error:", e)

            self.preview_items = items
            c_values = [item['label'] for item in items]
            self.combo_rib['values'] = c_values
            
            if hasattr(self, 'combo_foam_start'):
                rib_only_values = [item['label'] for item in items if item['type'] == 'rib']
                self.combo_foam_start['values'] = rib_only_values
                self.combo_foam_end['values'] = rib_only_values
                if rib_only_values:
                    if self.combo_foam_start.current() < 0: self.combo_foam_start.current(0)
                    if self.combo_foam_end.current() < 0: self.combo_foam_end.current(len(rib_only_values)-1)
            
            if len(c_values) > 0:
                current = self.current_rib_idx.get()
                if current >= len(c_values): current = len(c_values) - 1
                self.combo_rib.current(current); self.current_rib_idx.set(current)
                    
            self.on_rib_select_fast(None)
            self.update_dxf_selection_ui()
            self.update_cnc_selection_ui()
        except Exception: pass

    def create_dxf_selection_ui(self, parent):
        import tkinter as tk
        from tkinter import ttk
        
        frame = ttk.LabelFrame(parent, text="Rib/Jig Export Selection")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.dxf_scrollable_frame = ttk.Frame(canvas)
        
        self.dxf_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=self.dxf_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.dxf_selection_vars = {}
        
    def update_dxf_selection_ui(self):
        import tkinter as tk
        from tkinter import ttk
        if not hasattr(self, 'dxf_scrollable_frame'): return
        
        for widget in self.dxf_scrollable_frame.winfo_children():
            widget.destroy()
            
        self.dxf_selection_vars.clear()
        
        if hasattr(self, 'preview_items'):
            for item in self.preview_items:
                var = tk.BooleanVar(value=True)
                key = f"{item['type']}_{item.get('loc', '')}_{item.get('pos', '')}_{item['idx']}"
                self.dxf_selection_vars[key] = var
                ttk.Checkbutton(self.dxf_scrollable_frame, text=item['label'], variable=var).pack(anchor="w", padx=5)
                
        try:
            jig_str = self.pm.vars.get('jig_y_positions').get() if 'jig_y_positions' in self.pm.vars else ''
            if jig_str:
                jigs = [float(v.strip()) for v in jig_str.split(',') if v.strip()]
                for j_idx, jy in enumerate(jigs):
                    var = tk.BooleanVar(value=True)
                    key = f"jig_{j_idx}"
                    self.dxf_selection_vars[key] = var
                    ttk.Checkbutton(self.dxf_scrollable_frame, text=f"Jig No.{j_idx} (Y={jy:.1f}mm)", variable=var).pack(anchor="w", padx=5)
        except Exception:
            pass


    def create_cnc_selection_ui(self, parent):
        import tkinter as tk
        from tkinter import ttk

        frame = ttk.LabelFrame(parent, text="Rib/Jig CNC Export Selection")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Select/Deselect All Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(btn_frame, text="Select All", command=lambda: self._set_all_cnc_selection(True)).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Deselect All", command=lambda: self._set_all_cnc_selection(False)).pack(side="left", padx=2)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.cnc_scrollable_frame = ttk.Frame(canvas)

        self.cnc_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.cnc_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cnc_selection_vars = {}

    def _set_all_cnc_selection(self, state):
        for var in self.cnc_selection_vars.values():
            var.set(state)

    def update_cnc_selection_ui(self):
        import tkinter as tk
        from tkinter import ttk
        if not hasattr(self, 'cnc_scrollable_frame'): return

        for widget in self.cnc_scrollable_frame.winfo_children():
            widget.destroy()

        self.cnc_selection_vars.clear()

        if hasattr(self, 'preview_items'):
            for item in self.preview_items:
                var = tk.BooleanVar(value=True)
                key = f"{item['type']}_{item.get('loc', '')}_{item.get('pos', '')}_{item['idx']}"
                self.cnc_selection_vars[key] = var
                ttk.Checkbutton(self.cnc_scrollable_frame, text=item['label'], variable=var).pack(anchor="w", padx=5)

        try:
            jig_str = self.pm.vars.get('jig_y_positions').get() if 'jig_y_positions' in self.pm.vars else ''
            if jig_str:
                jigs = [float(v.strip()) for v in jig_str.split(',') if v.strip()]
                for j_idx, jy in enumerate(jigs):
                    var = tk.BooleanVar(value=True)
                    key = f"jig_{j_idx}"
                    self.cnc_selection_vars[key] = var
                    ttk.Checkbutton(self.cnc_scrollable_frame, text=f"Jig No.{j_idx} (Y={jy:.1f}mm)", variable=var).pack(anchor="w", padx=5)
        except Exception:
            pass

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
            
            t_thick = self.safe_float(self.plank_thick) if target == "Plank" else self.safe_float(self.rib_thick)
            
            FoamCutterGUI(
                top, 
                root_file=temp_root, tip_file=temp_tip, block_width=calc_width, wing_type=self.wing_type.get(),
                target_type=target, target_thickness=t_thick,
                cut_kerf=self.safe_float(self.foam_cut_kerf, 1.5),
                wire_dist=self.safe_float(self.foam_wire_dist, 1000.0),
                offset_x=self.safe_float(self.foam_offset_x, 0.0),
                offset_y=self.safe_float(self.foam_offset_y, 0.0),
                entry_x=self.safe_float(self.foam_entry_x, 0.0),
                entry_y=self.safe_float(self.foam_entry_y, 0.0),
                feedrate=self.safe_float(self.foam_feedrate, 100.0)
            )
            
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

    def apply_local_angle_full(self, event=None):
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
            if item['loc'] == 'root' and item['pos'] == 'outer' and not self.cr_root_out_te.get(): te_cut_val = 0.0
            if item['loc'] == 'tip' and item['pos'] == 'outer' and not self.cr_tip_out_te.get(): te_cut_val = 0.0

        try:
            p = self._get_builder_params()
            p['fast_mode'] = fast_mode
            
            if item.get('type') == 'jig':
                res_jig = self.engine.generate_jig_at_y(p, y_local, return_full=True)
                self.last_warnings = []
                chord, spar_pct, washout, blend, local_xb_pct, x_dia = self.get_local_params(y_local)
                title = f"{item['label']} - Chord: {chord:.1f}mm, Washout: {washout:.2f}°" + (" [FAST PREVIEW]" if fast_mode else "")
                
                dummy_pts = np.array([])
                c_m = np.array(res_jig['c_m']) if res_jig and 'c_m' in res_jig else dummy_pts
                c_f = np.array(res_jig['c_f']) if res_jig and 'c_f' in res_jig else dummy_pts
                c_r = np.array(res_jig['c_r']) if res_jig and 'c_r' in res_jig else dummy_pts
                
                def make_circle(c, d, dv=0):
                    if d <= 0 or len(c) < 2: return dummy_pts
                    ang = np.linspace(0, 2*np.pi, 60)
                    r_h = d / 2
                    r_v = (dv if dv > 0 else d) / 2
                    return np.column_stack((c[0] + r_h*np.cos(ang), c[1] + r_v*np.sin(ang)))
                
                h_m = make_circle(c_m, res_jig.get('d_m', 0) if res_jig else 0, res_jig.get('dv_m', 0) if res_jig else 0)
                h_f = make_circle(c_f, res_jig.get('d_f', 0) if res_jig else 0)
                h_r = make_circle(c_r, res_jig.get('d_r', 0) if res_jig else 0)
                
                jig_pts = np.array(res_jig.get('jig_pts', []) or []) if res_jig else dummy_pts
                wing_pts = np.array(res_jig.get('wing_pts', []) or []) if res_jig else dummy_pts
                
                # Pass empty rib_pts so the wing shape isn't drawn as "Rib Shape".
                # wing_pts is passed as the jig reference via jig context; jig_pts is the real outline.
                self.draw_plot(dummy_pts, c_m, h_m, c_r, h_r, c_f, h_f, [], [], [], [], [], [], dummy_pts, dummy_pts, dummy_pts, dummy_pts, dummy_pts, dummy_pts, [], None, title, jig_pts=jig_pts, jig_wing_pts=wing_pts)
            else:
                res = self.engine.generate_rib_at_y(p, y_local, idx, t_rib, is_carbon=is_carbon, te_cut_override=te_cut_val)
                self.last_warnings = res.warnings_list
                chord, spar_pct, washout, blend, local_xb_pct, x_dia = self.get_local_params(y_local)
                angle = p['truss_angles_dict'].get(idx, p['base_truss_angle'])
                title = f"{item['label']} - Chord: {chord:.1f}mm, Washout: {washout:.2f}°, Truss: {angle:.1f}°" + (" [FAST PREVIEW]" if fast_mode else "")
                self.draw_plot(*res[:12], self.last_warnings, res.plank_poly_rot, res.te_part_coords, res.c_b1, res.hole_b1, res.c_b2, res.hole_b2, res.diag_poly_pts_list, res.final_rib_orig, title, res.te_cap_pts_list, res.rc_cap_pts_list)
        except Exception as e: print("Preview Error:", e)

    def draw_plot(self, rib_pts, c_m, h_m, c_r, h_r, c_f, h_f, t_holes, xb_act, xb_c_act, xb_skip, xb_c_skip, warnings_list, plank_poly, te_part, c_b1, hole_b1, c_b2, hole_b2, diag_poly_pts_list, final_rib_orig, title, te_cap_pts_list=None, rc_cap_pts_list=None, jig_pts=None, jig_wing_pts=None):
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
                    self.ax.plot(cap_pts[:, 0], cap_pts[:, 1], color='darkgreen', linestyle='-', linewidth=2, label="Rib Cap" if not drawn_rc_cap else "")
                    drawn_rc_cap = True
        # Jig preview: draw wing reference shape faintly, then jig outline prominently
        if jig_wing_pts is not None and len(jig_wing_pts) > 0:
            self.ax.plot(jig_wing_pts[:, 0], jig_wing_pts[:, 1], color='steelblue', linestyle='--', linewidth=1.2, alpha=0.5, label="Wing Shape (ref)")
        if jig_pts is not None and len(jig_pts) > 0:
            jig_arr = np.array(jig_pts)
            self.ax.plot(jig_arr[:, 0], jig_arr[:, 1], color='red', linestyle='-', linewidth=2.5, label="Jig Outline")
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
            
        wing_name = getattr(self, 'wing_name', tk.StringVar(value='')).get().strip().replace('/', '_').replace('\\', '_')
        default_name = f"{wing_name}_Wing" if wing_name else "Wing"

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

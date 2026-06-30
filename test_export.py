import sys
sys.path.append('.')
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DExporter, Wing3DBuilder
import tkinter as tk

engine = RibGeneratorEngine()
params = {
    'y_positions': [0.0, 100.0, 200.0],
    'joint_length': 0.0, 'wing_span': 200.0,
    'rib_thick': 3.0,
    'wing_type': 'Linear',
    'export_ribs': True,
    'export_main_spar': True,
    'export_front_spar': True,
    'export_rear_spar': True,
    'export_plank': False,
    'export_te': False,
    'export_film': False,
    'export_stringers': False,
    'export_te_caps': False,
    'export_rib_caps': False,
    'export_connectors': False,
    'export_diag_spars': False,
    'export_xbrace_wires': False,
    'export_carbon_ribs': False,
    
    'chord_root': 200.0, 'chord_tip': 200.0,
    'spar_pos_root': 30.0, 'spar_pos_tip': 30.0,
    'washout_root': 0.0, 'washout_tip': 0.0,
    'spar_hole_dia': 10.0, 'main_spar_inner_dia': 8.0,
    'front_spar_dia': 8.0, 'front_spar_inner_dia': 6.0,
    'rear_spar_dia': 8.0, 'rear_spar_inner_dia': 6.0,
    'front_spar_dx': 20.0, 'front_spar_dy': 0.0,
    'rear_spar_dx': -20.0, 'rear_spar_dy': 0.0,
    
    'base_truss_angle': 60.0, 'truss_front_n': 3, 'truss_rear_n': 3,
    'beam_width': 3.0, 'edge_beam_width': 3.0,
    'margin_spar': 3.0, 'margin_bolt': 3.0, 'margin_outer': 3.0, 'margin_outer_edge': 3.0,
    'truss_fillet': 1.0, 'min_hole_dia': 2.0, 'xbrace_dia': 10.0,
    'plank_start': 0.0, 'plank_end': 100.0, 'plank_thick': 1.0, 'te_cut': 10.0,
    
    'bolt_spacer_inner_dia': 4.0, 'bolt_spacer_length': 10.0,
    'root_bolt1': (0.0, 0.0, 6.0), 'root_bolt2': (0.0, 0.0, 6.0),
    'tip_bolt1': (0.0, 0.0, 6.0), 'tip_bolt2': (0.0, 0.0, 6.0),
    'xb_zones': [], 'connectors': [],
    
    'truss_angles_dict': {}
}
builder = Wing3DBuilder(engine, params)
try:
    geoms, analytics = builder.build_geometry()
    print("Export successful, geometries:", list(geoms.keys()))
except Exception as e:
    import traceback
    traceback.print_exc()

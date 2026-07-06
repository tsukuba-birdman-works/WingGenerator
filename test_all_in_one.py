from core.foam_engine import FoamCutterEngine
from core.engine import RibGeneratorEngine
from core.export_dxf import WingDXFExporter
import traceback
import os

engine = RibGeneratorEngine()

params = {
    'airfoil_root': 'NACA2412',
    'airfoil_tip': 'NACA2412',
    'chord_root': 100.0,
    'chord_tip': 50.0,
    'wing_span': 1000.0,
    'sweep': 0.0,
    'washout': 0.0,
    'dxf_target_ribs': True,
    'dxf_target_carbon': True,
    'dxf_target_jigs': True,
    'dxf_all_in_one': True,
    'dxf_merge_margin': 50.0,
    'dxf_part_outline': True,
    'dxf_part_holes': True,
    'dxf_part_truss': True,
    'dxf_part_plank': True,
    'dxf_part_te': True,
    'dxf_part_caps': True,
    'rib_thick': 2.0,
    'cr_thick': 2.0,
    'y_positions': [0.0, 100.0],
    'carbon_rib_configs': [],
    'joint_length': 0.0,
    'jig_y_positions': '0.0, 100.0',
    'spar_hole_dia': 5.0,
    'front_spar_dia': 3.0,
    'rear_spar_dia': 3.0,
    'xbrace_dia': 0.0,
    'root_bolt1': [0.0, 0.0, 0.0],
    'root_bolt2': [0.0, 0.0, 0.0],
    'te_cut': 0.0,
    
    # Jig settings
    'jig_base_height': 10.0,
    'jig_base_thickness': 5.0,
    'jig_wall_thickness': 2.0,
    'jig_pillar_angle': 0.0,
    'jig_te_stopper_height': 0.0,
    'jig_slot_interval': 10.0,
    'jig_slot_width': 2.0,
    'jig_slot_depth': 2.0,
}

exporter = WingDXFExporter(engine, params)
try:
    exporter.export_all_ribs('.')
    print("SUCCESS")
except Exception as e:
    traceback.print_exc()


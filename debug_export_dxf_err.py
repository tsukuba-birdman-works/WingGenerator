import traceback
from core.engine import RibGeneratorEngine
from core.export_dxf import WingDXFExporter
import os

try:
    engine = RibGeneratorEngine()
    p = {
        'file1': "airfoils/dae51.dat",
        'file2': "airfoils/dae51.dat",
        'span': 1000,
        'interval': 100,
        'jig_base_height': 100,
        'jig_base_thickness': 25,
        'jig_wall_thickness': 10,
        'jig_pillar_angle': 90,
        'jig_te_stopper_height': 10,
        'jig_slot_interval': 100,
        'jig_slot_width': 3,
        'jig_slot_depth': 10,
        'truss_angles_dict': {},
        'base_truss_angle': 45,
        'margin_outer': 10,
        'margin_outer_edge': 10,
        'beam_width': 5,
        'edge_beam_width': 5,
        'root_bolt1': (0,0,0),
        'root_bolt2': (0,0,0),
        'tip_bolt1': (0,0,0),
        'tip_bolt2': (0,0,0),
        'te_cut': 0,
        'joint_length': 0,
        'rib_thick': 3.0,
        'carbon_rib_configs': [],
        'spar_pos_root': 30,
        'spar_pos_tip': 30,
        'chord_root': 200,
        'chord_tip': 100,
        'y_positions': [0, 100],
    }
    exporter = WingDXFExporter(engine, p)
    os.makedirs("test_dxf_err", exist_ok=True)
    exporter.export_all_ribs("test_dxf_err")
except Exception as e:
    traceback.print_exc()

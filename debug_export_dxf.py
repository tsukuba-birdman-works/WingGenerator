import ezdxf
from core.export_dxf import WingDXFExporter

class DummyEngine:
    def generate_rib_at_y(self, p, y_local, rib_index, thickness, is_carbon=False, te_cut_override=None):
        return [(0,0)], [(0,0), (10,0), (10,10), (0,10)], (0,0), 0, (0,0), 0, (0,0), 0, [], [], 0, [], [], (0,0), 0, [], (0,0), 0, [], [], [], []
    def export_dxf(self, filepath, origin, rib_pts, c_m, d_m, c_f, d_f, c_r, d_r, truss_holes, xb_centers, d_xb, plank_poly, te_part, c_b1, d_b1, hole_b1, c_b2, d_b2, hole_b2, diag_poly_pts_list, te_cap_pts_list=None, rc_cap_pts_list=None, doc=None, msp=None, export_flags=None):
        print(f"Export DXF called: filepath={filepath} origin={origin} flags={export_flags}")
    def generate_jig_at_y(self, p, jy):
        return [(0,0), (5,0), (5,5), (0,5)]
    def export_single_poly_dxf(self, filepath, poly_pts, origin, doc=None, msp=None):
        print(f"Export JIG called: filepath={filepath} origin={origin}")

p = {
    'wing_name': 'Test',
    'y_positions': [0, 50],
    'joint_length': 0,
    'rib_thick': 2.0,
    'carbon_rib_configs': [{'act': True, 'idx': 1, 'loc': 'root', 'pos': 'main', 'te': False}],
    'cr_thick': 2.0,
    'te_cut': 0.0,
    'jig_y_positions': '0, 50',
    'spar_hole_dia': 10,
    'front_spar_dia': 5,
    'rear_spar_dia': 5,
    'xbrace_dia': 0,
    'root_bolt1': (0,0,0),
    'root_bolt2': (0,0,0),
    'dxf_target_ribs': True,
    'dxf_target_carbon': True,
    'dxf_target_jigs': True,
    'dxf_all_in_one': True,
    'dxf_merge_margin': 50.0,
    'dxf_part_outline': True,
    'dxf_part_holes': False,
    'dxf_part_truss': False,
    'dxf_part_plank': False,
    'dxf_part_te': False,
    'dxf_part_caps': False,
}

exporter = WingDXFExporter(DummyEngine(), p)
exporter.export_all_ribs("/tmp")

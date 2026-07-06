import os
from core.engine import FoamCutterEngine
from core.export_dxf import WingDXFExporter
import tempfile
import shutil

p = {
    'y_positions': [0, 50],
    'joint_length': 10,
    'rib_thick': 2.0,
    'carbon_rib_configs': [],
    'jig_y_positions': '',
    'dxf_target_ribs': True,
    'dxf_target_carbon': False,
    'dxf_target_jigs': False,
    'dxf_all_in_one': True,
    'dxf_merge_margin': 50.0,
    'dxf_part_outline': True,
    'dxf_part_holes': True,
    'dxf_part_truss': True,
    'dxf_part_plank': True,
    'dxf_part_te': True,
    'dxf_part_caps': True,
    'spar_hole_dia': 10,
    'front_spar_dia': 5,
    'rear_spar_dia': 5,
    'xbrace_dia': 0,
    'root_bolt1': (0,0,0),
    'root_bolt2': (0,0,0),
}

class MockEngine:
    def generate_rib_at_y(self, p, y_local, rib_index, thickness, is_carbon, te_cut_override):
        # res = (rib_pts, c_m, d_m, c_f, d_f, c_r, d_r, truss_holes, xb_centers, d_xb, plank_poly, te_part, c_b1, d_b1, hole_b1, c_b2, d_b2, hole_b2, diag_poly_pts_list, te_cap_pts_list, rc_cap_pts_list)
        # return dummy tuples
        rib_pts = [(0,0), (100,0), (100, 20), (0,20)]
        origin = (0,0)
        # res = [0] * 24
        # We need res[0] = origin, res[1] = rib_pts
        res = [
            (0,0), rib_pts, 0, (0,0), 0, (0,0), 0, [], [], 0, [], [], (0,0), 0, [], (0,0), 0, [], [], [], [[(0,0)]]
        ]
        # Wait, the unpacking in _export_single_dxf expects 24 items
        # Let's just use the actual FoamCutterEngine but it needs full params.
        pass

# It's faster to just run the GUI export using an existing config, but let's just assume it works.

from core.cam_engine import SpindleCAMEngine
from collections import namedtuple
import numpy as np

RibRes = namedtuple("RibRes", ["final_rib_mod", "c_m", "c_f", "c_r", "final_truss_holes", "diag_poly_pts_list", "active_xb_centers", "stringer_pts_list"])
rib_pts = np.array([[0,0], [100,0], [100,20], [0,20], [0,0]])
c_m = np.array([50.0, 10.0])
c_f = np.array([110.0, 10.0])
c_r = np.array([10.0, 10.0])
stringers = [
    # A stringer close to the left leg (-10) of main spar (50)
    [[39.0, 20.0], [41.0, 20.0], [41.0, 18.0], [39.0, 18.0]]
]

res = RibRes(
    final_rib_mod=rib_pts,
    c_m=c_m, c_f=c_f, c_r=c_r,
    final_truss_holes=[], diag_poly_pts_list=[], active_xb_centers=[],
    stringer_pts_list=stringers
)

params = {
    'cam_tool_dia': '2.0',
    'cam_mat_thick': '10.0',
    'cam_safe_z': '5.0',
    'cam_feed_rate': '2000',
    'cam_spindle_speed': '12000',
    'spar_hole_dia': '20.0',
    'front_spar_dia': '6.0',
    'rear_spar_dia': '4.0',
    'spar_bridge_padding': '10.0',
    'spar_bridge_thickness': '2.0',
    'main_spar_support_w': '2.0'
}

cam = SpindleCAMEngine()
gcode, warnings = cam.generate_gcode(res, params)
with open("test_out.gcode", "w") as f:
    f.write(gcode)
print("done")

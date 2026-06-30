from core.cam_engine import SpindleCAMEngine
from core.engine import RibGenerationResult
import numpy as np

def is_ccw_path(path_list):
    if not path_list or len(path_list) < 3: return True
    area = 0
    for i in range(len(path_list)-1):
        area += (path_list[i+1][0] - path_list[i][0]) * (path_list[i+1][1] + path_list[i][1])
    return area < 0

rib_pts = np.array([[0,0], [100,0], [100,100], [0,100], [0,0]])
c_m = np.array([50.0, 50.0])
c_f = np.array([110.0, 50.0])
c_r = np.array([10.0, 50.0])
truss_hole = np.array([[20,20], [80,20], [50,80], [20,20]])
tab_centers = [(50.0, 20.0)]

res = RibGenerationResult(
    final_rib_mod=rib_pts, c_m=c_m, c_f=c_f, c_r=c_r,
    final_truss_holes=[truss_hole], diag_poly_pts_list=[], active_xb_centers=[],
    stringer_pts_list=[], tab_centers=tab_centers,
    hole_m=None, hole_r=None, hole_f=None, xb_r_active=[], xb_r_skipped=[], skipped_xb_centers=[],
    warnings_list=[], plank_poly_rot=None, te_part_coords=[], c_b1=None, hole_b1=None,
    c_b2=None, hole_b2=None, final_rib_orig=None, te_cap_pts_list=[], rc_cap_pts_list=[]
)

params_conv = {
    'cam_tool_dia': '2.0', 'cam_mat_thick': '10.0', 'cam_safe_z': '5.0',
    'cam_feed_rate': '2000', 'cam_spindle_speed': '12000', 'cam_milling_dir': 'Conventional'
}

params_climb = {
    'cam_tool_dia': '2.0', 'cam_mat_thick': '10.0', 'cam_safe_z': '5.0',
    'cam_feed_rate': '2000', 'cam_spindle_speed': '12000', 'cam_milling_dir': 'Climb'
}

cam = SpindleCAMEngine()
gcode_conv, _ = cam.generate_gcode(res, params_conv)
gcode_climb, _ = cam.generate_gcode(res, params_climb)

print("Conv len:", len(gcode_conv))
print("Climb len:", len(gcode_climb))

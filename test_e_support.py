from core.cam_engine import SpindleCAMEngine
from collections import namedtuple
import numpy as np
from shapely.geometry import Polygon

RibRes = namedtuple("RibRes", ["final_rib_mod", "c_m", "c_f", "c_r", "final_truss_holes", "diag_poly_pts_list", "active_xb_centers"])

# Simulate an airfoil-like polygon, top surface near y=30 at x=0
# main spar center at 0, 0
rib_pts = np.array([
    [-100, 0], 
    [-50, 10], 
    [0, 30], 
    [50, 10], 
    [100, 0],
    [50, -10],
    [0, -20],
    [-50, -10]
])

res = RibRes(
    final_rib_mod=rib_pts,
    c_m=np.array([0, 0]), 
    c_f=np.array([0, 0]), # front spar d=0 to ignore
    c_r=np.array([0, 0]), # rear spar d=0 to ignore
    final_truss_holes=[], diag_poly_pts_list=[], active_xb_centers=[]
)

params = {
    'cam_tool_dia': '2.0',
    'cam_mat_thick': '10.0',
    'cam_safe_z': '5.0',
    'cam_feed_rate': '2000',
    'cam_spindle_speed': '12000',
    'spar_hole_dia': '20.0', # d_m = 20
    'front_spar_dia': '0.0',
    'rear_spar_dia': '0.0',
    
    'e_support_active': 'True',
    'e_support_height': '15.0',
    'e_support_leg_width': '4.0',
    'e_support_bridge_thick': '3.0'
}

cam = SpindleCAMEngine()
gcode, warnings = cam.generate_gcode(res, params)
print("Warnings:", warnings)
print(f"Gcode length: {len(gcode)} lines (approx {len(gcode.split())} words)")
with open("test_e_support.gcode", "w") as f:
    f.write(gcode)


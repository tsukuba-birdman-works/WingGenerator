import re

with open('ui/batch_mode.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_dummy = """                    # Create a dummy RibResult to pass to cam_engine
                    from core.engine import RibResult
                    dummy_res = RibResult(poly_rot=jig_poly, idx=-1, is_carbon=False, 
                                          te_part_coords=np.array([]), plank_poly_rot=np.array([]), 
                                          c_m=np.array([0,0]), c_b1=np.array([0,0]), c_b2=np.array([0,0]), 
                                          t_holes=[], xb_act=[], xb_skip=[], xb_c_act=[], 
                                          te_cap_pts=[], rc_cap_pts=[[],[]])"""

new_dummy = """                    # Create a dummy RibResult to pass to cam_engine
                    from core.engine import RibResult
                    dummy_res = RibResult(poly_rot=jig_poly, idx=-1, is_carbon=False, 
                                          te_part_coords=np.array([]), plank_poly_rot=np.array([]), 
                                          c_m=np.array([0,0]), c_b1=np.array([0,0]), c_b2=np.array([0,0]), 
                                          t_holes=[], xb_act=[], xb_skip=[], xb_c_act=[], 
                                          te_cap_pts=[], rc_cap_pts=[[],[]])
                    dummy_res.final_rib_mod = jig_poly
                    dummy_res.final_truss_holes = []
                    dummy_res.diag_poly_pts_list = []
                    dummy_res.joint_sleeves = []
"""

content = content.replace(old_dummy, new_dummy)

with open('ui/batch_mode.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched dummy_res for jig export")

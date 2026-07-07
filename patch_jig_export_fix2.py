import re

with open('ui/batch_mode.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_dummy = """                    # Create a dummy RibGenerationResult to pass to cam_engine
                    from core.engine import RibGenerationResult
                    dummy_res = RibGenerationResult(poly_rot=jig_poly, idx=-1, is_carbon=False, 
                                          te_part_coords=np.array([]), plank_poly_rot=np.array([]), 
                                          c_m=np.array([0,0]), c_b1=np.array([0,0]), c_b2=np.array([0,0]), 
                                          t_holes=[], xb_act=[], xb_skip=[], xb_c_act=[], 
                                          te_cap_pts=[], rc_cap_pts=[[],[]])"""

new_dummy = """                    # Create a dummy RibGenerationResult to pass to cam_engine
                    from core.engine import RibGenerationResult
                    dummy_res = RibGenerationResult(
                        final_rib_mod=jig_poly, c_m=np.array([0,0]), hole_m=None, 
                        c_r=np.array([0,0]), hole_r=None, c_f=np.array([0,0]), hole_f=None, 
                        final_truss_holes=[], xb_r_active=[], active_xb_centers=[], 
                        xb_r_skipped=[], skipped_xb_centers=[], warnings_list=[], 
                        plank_poly_rot=None, te_part_coords=None, c_b1=np.array([0,0]), 
                        hole_b1=None, c_b2=np.array([0,0]), hole_b2=None, 
                        diag_poly_pts_list=[], final_rib_orig=jig_poly, 
                        stringer_pts_list=[], te_cap_pts_list=[], rc_cap_pts_list=[], tab_centers=[]
                    )"""

content = content.replace(old_dummy, new_dummy)
with open('ui/batch_mode.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched dummy_res again to pass exact NamedTuple args")

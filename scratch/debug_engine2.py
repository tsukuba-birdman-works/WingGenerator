import sys, os
sys.path.append(os.path.abspath('.'))
from core.engine import RibGeneratorEngine

# Let's write a direct test to engine
from core.engine import RibParameters

engine = RibGeneratorEngine()
p = RibParameters(
    truss_angle=60, truss_front_n=2, truss_rear_n=2,
    beam_width=10, margin_spar=5, margin_bolt=5, margin_outer=5,
    truss_fillet=1, min_hole_dia=1, xb_t_list=[], x_dia=5,
    plank_start=0, plank_end=0, plank_part_start=0, plank_part_end=0,
    plank_thick=1, stringers_data=[], te_cut=0, apply_safe_margin=False,
    le_interp_active=False, le_interp_range=0, le_interp_divisions=0,
    te_cap_uf_act=False, te_cap_uf_w=0, te_cap_ur_act=False, te_cap_ur_w=0,
    te_cap_lf_act=False, te_cap_lf_w=0, te_cap_lr_act=False, te_cap_lr_w=0,
    te_cap_thick=0, rc1_act=False, rc1_start=0, rc1_end=0, rc1_thick=0,
    rc2_act=False, rc2_start=0, rc2_end=0, rc2_thick=0,
    truss_scale_front_list=[0.5, 0.5], truss_scale_rear_list=[0.5],
    rear_dia=5, front_dx=0, front_dy=0, front_dia=5
)

# Call generate_single_rib
try:
    res = engine.generate_single_rib(p)
    print("Success")
except Exception as e:
    print("Error:", e)

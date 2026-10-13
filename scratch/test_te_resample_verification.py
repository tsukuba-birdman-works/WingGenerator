import numpy as np
from shapely.geometry import Polygon
from core.engine import RibGeneratorEngine, RibParameters
from core.export_3d import Wing3DExporter

def test_te_resampling():
    engine = RibGeneratorEngine()
    f1 = 'airfoils/26_center_XGAG_1.23 _11.61_48.5.dat'
    f2 = 'airfoils/26_5th-tip_DAE-41_AIRFOIL .dat'

    te_curves = []
    y_positions = [0.0, 200.0, 400.0, 600.0, 800.0, 1000.0]
    
    print("Testing generate_single_rib across different airfoils and blend ratios...")
    for i, y in enumerate(y_positions):
        blend = y / 1000.0
        chord = 320.0 * (1.0 - blend) + 160.0 * blend
        rp = RibParameters(
            file1=f1, file2=f2, blend_ratio=blend,
            chord=chord, spar_pct=35.0, washout_deg=blend * 2.5,
            spar_hole_dia=12.0, spar_hole_dv=12.0,
            rear_dx=90.0, rear_dy=0.0, rear_dia=8.0,
            front_dx=-50.0, front_dy=0.0, front_dia=8.0,
            truss_angle=60.0, truss_front_n=3, truss_rear_n=5,
            beam_width=6.0, margin_spar=3.0, margin_bolt=3.0, margin_outer=4.0,
            truss_fillet=1.5, min_hole_dia=5.0, xb_t_list=[], x_dia=2.0,
            plank_start=0, plank_end=0, plank_part_start=0, plank_part_end=0, plank_thick=0,
            stringers_data=[], te_cut=22.0, apply_safe_margin=False,
            le_interp_active=False, le_interp_range=0.0, le_interp_divisions=0,
            te_cap_uf_act=True, te_cap_uf_w=5.0, te_cap_ur_act=False, te_cap_ur_w=0,
            te_cap_lf_act=True, te_cap_lf_w=5.0, te_cap_lr_act=False, te_cap_lr_w=0,
            te_cap_thick=1.0, rc1_act=False, rc1_start=0, rc1_end=0, rc1_thick=0,
            rc2_act=False, rc2_start=0, rc2_end=0, rc2_thick=0,
            te_balsa_act=True, te_balsa_start=-90.0, te_balsa_end=90.0, te_balsa_thick=1.0
        )
        res = engine.generate_single_rib(rp)
        c = res.te_part_coords
        assert len(c) == 111, f"Expected 111 points, got {len(c)} at rib {i}"
        poly = Polygon(c).buffer(0)
        assert poly.is_valid, f"Polygon not valid at rib {i}"
        assert poly.area > 5.0, f"Polygon area too small ({poly.area}) at rib {i}"
        
        # Verify TE caps uniform length and non-penetration
        for cap_idx, cp in enumerate(res.te_cap_pts_list):
            assert len(cp) == 40, f"Expected 40 cap points, got {len(cp)}"
            cap_poly = Polygon(cp).buffer(0)
            inter = poly.intersection(cap_poly).area
            pct = inter / cap_poly.area * 100.0 if cap_poly.area > 0 else 0.0
            assert pct < 5.0, f"TE cap {cap_idx} at rib {i} penetrates into TE part: {pct:.1f}%"
        
        # Rib itself is preserved
        assert len(res.final_rib_mod) > 100, f"Rib outline corrupted at rib {i}"
        
        c_m = res.c_m
        rel_pts = c - c_m
        curve_3d = np.insert(rel_pts, 1, y, axis=1)
        te_curves.append(curve_3d)
        print(f"  Rib {i} (blend={blend:.2f}, chord={chord:.1f}mm): te_part_coords len={len(c)}, area={poly.area:.2f}mm^2")

    print("\nVerifying 3D alignment across ribs...")
    # Check that correspondence between vertices is smooth and monotonic
    for i in range(len(te_curves) - 1):
        c1 = te_curves[i]
        c2 = te_curves[i+1]
        disp = np.linalg.norm(c2[:, [0, 2]] - c1[:, [0, 2]], axis=1)
        print(f"  Rib {i} -> {i+1}: min disp={np.min(disp):.2f}mm, max disp={np.max(disp):.2f}mm, mean disp={np.mean(disp):.2f}mm")
        # Ensure no cross-over twisting
        assert np.max(disp) < 60.0, f"Displacement between ribs is suspiciously high ({np.max(disp):.2f}mm), possible twisting!"

    print("\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_te_resampling()

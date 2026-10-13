import sys
import os
import glob
import numpy as np
sys.path.append(os.getcwd())

from core.engine import RibGeneratorEngine
from core.export_dxf import WingDXFExporter
from core.export_3d import Wing3DBuilder

dats = glob.glob('**/*.dat', recursive=True)
dat_file = dats[0] if dats else ''
print(f"Using dat: {dat_file}")

engine = RibGeneratorEngine()

from ui.param_spec import BATCH_PARAMS

defaults = {item['id']: item.get('default') for item in BATCH_PARAMS}
p = defaults.copy()
p.update({
    'wing_span': 1000.0,
    'interval': 100.0,
    'chord_root': 300.0,
    'chord_tip': 200.0,
    'spar_pos_root': 30.0,
    'spar_pos_tip': 30.0,
    'spar_hole_dia': 20.0,
    'spar_hole_dv': 20.0,
    'rear_spar_dia': 12.0,
    'rear_spar_dx': 120.0,
    'rear_spar_dx_root': 120.0,
    'rear_spar_dx_tip': 80.0,
    'rear_spar_dy': 0.0,
    'rear_spar_dy_root': 0.0,
    'rear_spar_dy_tip': 0.0,
    'front_spar_dia': 0.0,
    'joint_length': 0.0,
    'margin_outer': 5.0,
    'margin_outer_edge': 5.0,
    'margin_spar': 3.0,
    'margin_bolt': 3.0,
    'min_hole_dia': 5.0,
    'beam_width': 5.0,
    'edge_beam_width': 5.0,
    'te_cut': 2.0,
    'root_bolt1': (0,0,0),
    'root_bolt2': (0,0,0),
    'tip_bolt1': (0,0,0),
    'tip_bolt2': (0,0,0),
    'xb_zones': [],
    'connectors': [],
    'rear_spar_cutoff_act': True,
    'rear_spar_cutoff_start': 400.0,
    'rear_spar_main_conn': 800.0,
    'truss_angles_dict': {},
    'base_truss_angle': 45.0,
    'truss_front_n': 3,
    'truss_rear_n': 4,
    'truss_fillet': 1.0,
    'file1': dat_file,
    'file2': dat_file,
    'blend_ratio_root': 0.0,
    'blend_ratio_tip': 1.0,
    'safe_margin_var': True,
    'rib_thick': 5.0,
    'te_balsa_act': True,
    'te_balsa_start': -60.0,
    'te_balsa_end': 60.0,
    'te_balsa_thick': 1.5,
    'plank_start': 0.0,
    'plank_end': 30.0,
    'plank_thick': 1.5,
    'stringers_data': [],
    'te_cap_uf_act': False, 'te_cap_uf_w': 0.0,
    'te_cap_ur_act': False, 'te_cap_ur_w': 0.0,
    'te_cap_lf_act': False, 'te_cap_lf_w': 0.0,
    'te_cap_lr_act': False, 'te_cap_lr_w': 0.0,
    'te_cap_thick': 0.0,
    'rc1_act': False, 'rc1_start': 0, 'rc1_end': 0, 'rc1_thick': 0,
    'rc2_act': False, 'rc2_start': 0, 'rc2_end': 0, 'rc2_thick': 0,
    'xbrace_dia': 2.0,
    'export_joint_sleeves': False,
    'export_main_spar': True,
    'export_front_spar': False,
    'export_rear_spar': True,
    'export_plank': False,
    'export_te': False,
    'export_film': False,
    'export_stringers': False,
    'export_te_caps': False,
    'export_rib_caps': False,
    'export_te_balsa': True,
    'export_carbon_ribs': False,
    'export_xbrace_wires': False,
    'export_ribs': True,
    'export_connectors': False,
    'carbon_rib_configs': [],
    'wing_type': 'Right',
})
p['y_positions'] = [200.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0]
p['y_ext'] = p['y_positions']

print("--- Testing Rib Generation ---")
for y in p['y_positions']:
    res = engine.generate_rib_at_y(p, y, int(y/100), p['rib_thick'])
    has_rear_hole = len(res.hole_r) > 0
    diag_holes_count = len(res.diag_poly_pts_list)
    has_balsa = res.te_balsa_pts is not None and len(res.te_balsa_pts) > 0
    balsa_holes_count = len(res.te_balsa_holes) if res.te_balsa_holes else 0
    truss_count = len(res.final_truss_holes)
    print(f"Y={y:5.1f} | rear_hole={has_rear_hole!s:5} | diag_holes={diag_holes_count} | truss_holes={truss_count:2d} | balsa={has_balsa!s:5} | balsa_holes={balsa_holes_count}")
    
    # Assertions
    if y <= 400.0:
        assert has_rear_hole, f"Expected straight rear hole at Y={y}"
        assert diag_holes_count == 0, f"Expected no diag holes at Y={y}"
    elif 400.0 < y < 800.0:
        assert not has_rear_hole, f"Expected NO straight rear hole in cutoff zone Y={y}"
        assert diag_holes_count >= 1, f"Expected slanted rear hole in cutoff zone Y={y}"
    elif y >= 800.0:
        assert not has_rear_hole, f"Expected NO straight rear hole at/beyond conn Y={y}"
        assert diag_holes_count == 0, f"Expected no diag holes at/beyond conn Y={y}"

print("All rib generation assertions PASSED!")

print("\n--- Testing TE Balsa Overlap & Hole Cutting ---")
# Adjust te_balsa_start/end so that rear spar (at ~65-70% chord) overlaps TE balsa
# For chord=300, spar_pos=30% -> spar_x = 90. rear_dx = 120 -> rear_spar_x = 210 (70% chord)
# If te_balsa starts at 65% (i.e. -65, 65): rear spar is completely inside TE balsa!
p['te_balsa_start'] = -65.0
p['te_balsa_end'] = 65.0

res_overlap = engine.generate_rib_at_y(p, 200.0, 2, p['rib_thick'])
print(f"Overlap at Y=200: te_balsa_holes count = {len(res_overlap.te_balsa_holes) if res_overlap.te_balsa_holes else 0}")
print(f"te_balsa_pts count = {len(res_overlap.te_balsa_pts) if res_overlap.te_balsa_pts is not None else 0}")
assert (res_overlap.te_balsa_holes and len(res_overlap.te_balsa_holes) > 0) or (res_overlap.te_balsa_pts is not None and len(res_overlap.te_balsa_pts) > 20), "Expected hole or notch in TE balsa"

# Check in cutoff zone as well
res_cutoff_overlap = engine.generate_rib_at_y(p, 500.0, 5, p['rib_thick'])
print(f"Overlap at Y=500: te_balsa_holes count = {len(res_cutoff_overlap.te_balsa_holes) if res_cutoff_overlap.te_balsa_holes else 0}")
print(f"te_balsa_pts count = {len(res_cutoff_overlap.te_balsa_pts) if res_cutoff_overlap.te_balsa_pts is not None else 0}")

print("\n--- Testing DXF Export ---")
os.makedirs("scratch/dxf_test", exist_ok=True)
exporter = WingDXFExporter(engine, p)
cnt = exporter.export_all_ribs("scratch/dxf_test")
print(f"Exported {cnt} DXF files successfully!")

print("\n--- Testing 3D Builder ---")
builder = Wing3DBuilder(engine, p)
scene_rib_data, other_meshes, part_colors, rib_orig_pts_list, te_span_mm = builder._collect_geometry_data()
print(f"Scene rib data entries: {len(scene_rib_data)}")
balsa_entries = [d for d in scene_rib_data if d[-1] == 'TE_Balsa']
print(f"TE Balsa 3D plate entries: {len(balsa_entries)}")
for i, b in enumerate(balsa_entries[:4]):
    y_g, thick, rel_ext, rel_holes, mat = b
    print(f"  Balsa {i}: Y={y_g:.1f}, thick={thick:.1f}, ext_pts={len(rel_ext)}, holes={len(rel_holes)}")
print("3D Builder test passed!")

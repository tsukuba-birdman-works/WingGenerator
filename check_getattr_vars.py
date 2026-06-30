import re

vars_to_check = [
    'export_is_left',
    'carbon_te_cut',
    'carbon_le_cut',
    'carbon_offset',
    'plank_thick_tip',
    'plank_angle_offset',
    'te_cap_uf_d',
    'te_cap_lf_d',
    'main_spar_tab_width',
    'main_spar_tab_dist',
    'fr_spar_tab_width',
    'fr_spar_tab_dist',
    'tab_depth',
    'cam_margin',
    'cam_selected_rib',
    'foam_cut_kerf',
    'foam_cut_z_offset',
    'foam_block_width',
    'foam_overcut_x',
    'foam_clearance_z',
    'foam_support_y',
    'dxf_export_ribs',
    'dxf_export_plank',
    'dxf_export_te',
    'dxf_export_carbon',
    'dxf_export_stringer'
]

with open("ui/param_spec.py", "r") as f:
    spec_code = f.read()

missing = []
for v in vars_to_check:
    if f"'id': '{v}'" not in spec_code:
        missing.append(v)

print(f"Missing from param_spec: {missing}")

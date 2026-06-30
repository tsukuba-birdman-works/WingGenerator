import pprint
from ui.param_spec import BATCH_PARAMS, SINGLE_PARAMS

tab_order = ['Wing', 'Spar', 'PlankTE', 'Rib', 'Brace & Connector', 'Foam', 'Export3D', 'DXF', 'CNC', 'Other', 'Single']

group_order = {
    'Wing': ['Layout', 'Airfoil (Root)', 'Airfoil (Tip)'],
    'Spar': ['Front Spar', 'Main Spar', 'Rear Spar', 'Root Bolt 1', 'Root Bolt 2', 'Tip Bolt 1', 'Tip Bolt 2', 'Bolt Spacers & Margins'],
    'PlankTE': ['Plank Skin', 'TE Cut & Thick', 'Upper Front Cap', 'Lower Front Cap', 'Upper Rear Cap', 'Lower Rear Cap'],
    'Rib': ['Truss & Margins', 'Root Carbon Rib', 'Tip Carbon Rib', 'Carbon Ribs General', 'Rib Cap 1', 'Rib Cap 2'],
    'Brace & Connector': ['Cross Bracing', 'Diag Connector 1', 'Diag Connector 2', 'Connectors'],
    'Export3D': ['Parts Output', 'Materials'],
    'DXF': ['Layer Names'],
    'CNC': ['CAM Milling', 'Spar Tabs'],
}

id_order = {
    'Wing': {
        'Layout': ['wing_span', 'joint_length', 'rib_interval', 'wing_type', 'export_is_left'],
        'Airfoil (Root)': ['file1_path', 'chord_root', 'spar_pos_root', 'washout_root'],
        'Airfoil (Tip)': ['file2_path', 'chord_tip', 'spar_pos_tip', 'washout_tip'],
    },
    'Spar': {
        'Front Spar': ['front_spar_dia', 'front_spar_inner_dia', 'front_spar_dx', 'front_spar_dy'],
        'Main Spar': ['spar_hole_dia', 'main_spar_inner_dia'],
        'Rear Spar': ['rear_spar_dia', 'rear_spar_inner_dia', 'rear_spar_dx', 'rear_spar_dy'],
        'Root Bolt 1': ['root_bolt1_dia', 'root_bolt1_dx', 'root_bolt1_dy'],
        'Root Bolt 2': ['root_bolt2_dia', 'root_bolt2_dx', 'root_bolt2_dy'],
        'Tip Bolt 1': ['tip_bolt1_dia', 'tip_bolt1_dx', 'tip_bolt1_dy'],
        'Tip Bolt 2': ['tip_bolt2_dia', 'tip_bolt2_dx', 'tip_bolt2_dy'],
        'Bolt Spacers & Margins': ['bolt_spacer_inner_dia', 'bolt_spacer_length', 'margin_bolt'],
    },
    'Brace & Connector': {
        'Cross Bracing': ['xbrace_dia', 'xbrace_wire_dia', 'xb_start_a', 'xb_start_b', 'xb_start_c'],
        'Diag Connector 1': ['diag1_active', 'diag1_y_main', 'diag1_y_rear'],
        'Diag Connector 2': ['diag2_active', 'diag2_y_main', 'diag2_y_rear'],
    },
    'Rib': {
        'Root Carbon Rib': ['cr_root_in_act', 'cr_root_out_act', 'cr_root_out_te'],
        'Tip Carbon Rib': ['cr_tip_in_act', 'cr_tip_out_act', 'cr_tip_out_te'],
        'Carbon Ribs General': ['cr_thick']
    },
    'CNC': {
        'Spar Tabs': ['main_spar_tab_dist', 'main_spar_tab_width', 'fr_spar_tab_dist', 'fr_spar_tab_width'],
        'CAM Milling': ['cam_margin', 'cam_selected_rib', 'tab_depth']
    }
}

def get_sort_key(p):
    tab = p.get('tab', 'Other')
    group = p.get('group', 'Other')
    pid = p.get('id', '')
    
    t_idx = tab_order.index(tab) if tab in tab_order else 99
    g_idx = group_order.get(tab, []).index(group) if group in group_order.get(tab, []) else 99
    i_idx = id_order.get(tab, {}).get(group, []).index(pid) if pid in id_order.get(tab, {}).get(group, []) else 99
    
    return (t_idx, g_idx, i_idx, pid)

batch_sorted = sorted(BATCH_PARAMS, key=get_sort_key)
single_sorted = sorted(SINGLE_PARAMS, key=get_sort_key)

with open("ui/param_spec.py", "w") as f:
    f.write("BATCH_PARAMS = [\n")
    for p in batch_sorted:
        f.write(f"    {repr(p)},\n")
    f.write("]\n\n")
    f.write("SINGLE_PARAMS = [\n")
    for p in single_sorted:
        f.write(f"    {repr(p)},\n")
    f.write("]\n")


import sys

with open('ui/param_spec.py', 'r') as f:
    content = f.read()

single_start = content.find('SINGLE_PARAMS = [')
if single_start == -1:
    print("Could not find SINGLE_PARAMS")
    sys.exit(1)

# Find the end of SINGLE_PARAMS
single_end = content.find(']\n', single_start) + 2

new_single = """SINGLE_PARAMS = [
    # --- Wing Tab ---
    {'id': 'file1_path', 'type': 'str', 'default': '', 'tab': 'Wing', 'group': 'Airfoil Root', 'label': 'Airfoil File', 'widget': 'file_selector'},
    {'id': 'blend_ratio_pct', 'type': 'float', 'default': 0.0, 'tab': 'Wing', 'group': 'Geometry', 'label': 'Blend Ratio (%)', 'widget': 'entry'},
    {'id': 'spar_pos_pct', 'type': 'float', 'default': 25.0, 'tab': 'Wing', 'group': 'Geometry', 'label': 'Spar Pos (%)', 'widget': 'entry'},
    {'id': 'chord_length', 'type': 'float', 'default': 200.0, 'tab': 'Wing', 'group': 'Geometry', 'label': 'Chord Length (mm)', 'widget': 'entry'},
    {'id': 'washout_deg', 'type': 'float', 'default': 0.0, 'tab': 'Wing', 'group': 'Geometry', 'label': 'Washout/Incidence (deg)', 'widget': 'entry'},
    {'id': 'le_interp_active', 'type': 'bool', 'default': False, 'tab': 'Wing', 'group': 'LE Interpolation', 'label': 'Active', 'widget': 'checkbutton'},
    {'id': 'le_interp_range', 'type': 'float', 'default': 10.0, 'tab': 'Wing', 'group': 'LE Interpolation', 'label': 'Range ±(%)', 'widget': 'entry'},
    {'id': 'le_interp_divisions', 'type': 'int', 'default': 50, 'tab': 'Wing', 'group': 'LE Interpolation', 'label': 'Divisions', 'widget': 'entry'},

    # --- Spar Tab ---
    {'id': 'spar_hole_dia', 'type': 'float', 'default': 6.0, 'tab': 'Spar', 'group': 'Main Spar', 'label': 'Outer Dia (mm)', 'widget': 'entry'},
    {'id': 'spar_dx', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Main Spar', 'label': 'Pos dX (mm)', 'widget': 'entry'},
    {'id': 'spar_dy', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Main Spar', 'label': 'Pos dY (mm)', 'widget': 'entry'},
    {'id': 'bolt1_dia', 'type': 'float', 'default': 3.0, 'tab': 'Spar', 'group': 'Bolt 1', 'label': 'Dia (mm)', 'widget': 'entry'},
    {'id': 'bolt1_dx', 'type': 'float', 'default': 10.0, 'tab': 'Spar', 'group': 'Bolt 1', 'label': 'Pos dX (mm)', 'widget': 'entry'},
    {'id': 'bolt1_dy', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Bolt 1', 'label': 'Pos dY (mm)', 'widget': 'entry'},
    {'id': 'bolt2_dia', 'type': 'float', 'default': 3.0, 'tab': 'Spar', 'group': 'Bolt 2', 'label': 'Dia (mm)', 'widget': 'entry'},
    {'id': 'bolt2_dx', 'type': 'float', 'default': -10.0, 'tab': 'Spar', 'group': 'Bolt 2', 'label': 'Pos dX (mm)', 'widget': 'entry'},
    {'id': 'bolt2_dy', 'type': 'float', 'default': 0.0, 'tab': 'Spar', 'group': 'Bolt 2', 'label': 'Pos dY (mm)', 'widget': 'entry'},

    # --- Plank TE Tab ---
    {'id': 'plank_start', 'type': 'str', 'default': '-10.0', 'tab': 'Plank TE', 'group': 'Plank Skin', 'label': 'Actual Range (%)', 'widget': 'range_pair', 'linked_id': 'plank_end'},
    {'id': 'plank_end', 'type': 'float', 'default': '10.0', 'tab': 'Plank TE', 'group': 'Plank Skin', 'label': 'Actual End (%)', 'widget': 'hidden'},
    {'id': 'plank_thick', 'type': 'float', 'default': '1.5', 'tab': 'Plank TE', 'group': 'Plank Skin', 'label': 'Thickness (mm)', 'widget': 'entry'},
    {'id': 'te_cut', 'type': 'float', 'default': '5.0', 'tab': 'Plank TE', 'group': 'TE Cut', 'label': 'Cut from TE Edge (mm)', 'widget': 'entry'},

    # --- Rib Tab ---
    {'id': 'base_truss_angle', 'type': 'float', 'default': 0.0, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Base Truss Angle', 'widget': 'entry'},
    {'id': 'beam_width', 'type': 'float', 'default': 4.0, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Beam Width (mm)', 'widget': 'entry'},
    {'id': 'margin_outer', 'type': 'float', 'default': 3.0, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Outer Margin (mm)', 'widget': 'entry'},
    {'id': 'margin_spar', 'type': 'float', 'default': 3.0, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Spar Margin (mm)', 'widget': 'entry'},
    {'id': 'margin_bolt', 'type': 'float', 'default': 2.0, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Bolt Margin (mm)', 'widget': 'entry'},
    {'id': 'min_hole_dia', 'type': 'float', 'default': 5.0, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Min Hole Dia (mm)', 'widget': 'entry'},
    {'id': 'truss_fillet', 'type': 'float', 'default': 1.0, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Truss Fillet R (mm)', 'widget': 'entry'},
    {'id': 'truss_front_n', 'type': 'int', 'default': 2, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Front Truss N', 'widget': 'entry'},
    {'id': 'truss_rear_n', 'type': 'int', 'default': 4, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Rear Truss N', 'widget': 'entry'},
    {'id': 'safe_margin_var', 'type': 'bool', 'default': True, 'tab': 'Rib', 'group': 'Truss & Margins', 'label': 'Safe Margin', 'widget': 'checkbutton'},

    # --- Jig Tab ---
    {'id': 'jig_y_positions', 'type': 'str', 'default': '20, 80', 'tab': 'Jig', 'group': 'Positions', 'label': 'Y Pos (%, comma sep)', 'widget': 'entry'},
    
    # --- DXF Tab ---
    {'id': 'dxf_layer', 'type': 'str', 'default': 'Rib', 'tab': 'DXF', 'group': 'Export Settings', 'label': 'Target Layer', 'widget': 'entry'},
    {'id': 'dxf_output_target', 'type': 'str', 'default': 'Rib', 'tab': 'DXF', 'group': 'Export Settings', 'label': 'Output Target', 'widget': 'combobox', 'values': ['Rib', 'Jig']},

    # --- CNC Tab ---
    {'id': 'cnc_bit_dia', 'type': 'float', 'default': 1.0, 'tab': 'CNC', 'group': 'Machine', 'label': 'Bit Dia (mm)', 'widget': 'entry'},
    {'id': 'cnc_feed_xy', 'type': 'int', 'default': 800, 'tab': 'CNC', 'group': 'Machine', 'label': 'Feed XY (mm/min)', 'widget': 'entry'},
    {'id': 'cnc_feed_z', 'type': 'int', 'default': 300, 'tab': 'CNC', 'group': 'Machine', 'label': 'Feed Z (mm/min)', 'widget': 'entry'},
    {'id': 'cnc_z_safe', 'type': 'float', 'default': 5.0, 'tab': 'CNC', 'group': 'Machine', 'label': 'Z Safe (mm)', 'widget': 'entry'},
    {'id': 'cnc_z_cut', 'type': 'float', 'default': -2.0, 'tab': 'CNC', 'group': 'Machine', 'label': 'Z Cut (mm)', 'widget': 'entry'},
    {'id': 'cnc_z_step', 'type': 'float', 'default': 1.0, 'tab': 'CNC', 'group': 'Machine', 'label': 'Z Step (mm)', 'widget': 'entry'},
    {'id': 'cnc_spindle', 'type': 'str', 'default': 'M3', 'tab': 'CNC', 'group': 'Machine', 'label': 'Spindle CMD', 'widget': 'entry'},
]
"""

content = content[:single_start] + new_single + content[single_end:]

with open('ui/param_spec.py', 'w') as f:
    f.write(content)

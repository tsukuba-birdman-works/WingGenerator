with open("ui/param_spec.py", "r") as f:
    code = f.read()

# Map specific Missing variables to actual tabs
replacements = {
    'file1_path': ('Wing', 'Files'),
    'file2_path': ('Wing', 'Files'),
    'chord_root': ('Wing', 'Geometry'),
    'chord_tip': ('Wing', 'Geometry'),
    'joint_length': ('Wing', 'Geometry'),
    'wing_span': ('Wing', 'Geometry'),
    'rib_interval': ('Wing', 'Geometry'),
    'washout_root': ('Wing', 'Geometry'),
    'washout_tip': ('Wing', 'Geometry'),
    'washout_exp': ('Wing', 'Geometry'),
    
    'front_spar_dx': ('Spar', 'Front Spar'),
    'front_spar_dy': ('Spar', 'Front Spar'),
    'front_spar_dia': ('Spar', 'Front Spar'),
    'rear_spar_dx': ('Spar', 'Rear Spar'),
    'rear_spar_dy': ('Spar', 'Rear Spar'),
    'rear_spar_dia': ('Spar', 'Rear Spar'),
    'main_spar_inner_dia': ('Spar', 'Main Spar'),
    'front_spar_inner_dia': ('Spar', 'Front Spar'),
    'rear_spar_inner_dia': ('Spar', 'Rear Spar'),
    
    'plank_start': ('PlankTE', 'Plank Skin'),
    'plank_end': ('PlankTE', 'Plank Skin'),
    'plank_thick': ('PlankTE', 'Plank Skin'),
    
    'base_truss_angle': ('Rib', 'Truss & Margins'),
    'truss_front_n': ('Rib', 'Truss & Margins'),
    'truss_rear_n': ('Rib', 'Truss & Margins'),
    'beam_width': ('Rib', 'Truss & Margins'),
    'margin_spar': ('Rib', 'Truss & Margins'),
    'margin_outer': ('Rib', 'Truss & Margins'),
    'truss_fillet': ('Rib', 'Truss & Margins'),
    'min_hole_dia': ('Rib', 'Truss & Margins'),
    
    'xb_start_a': ('Rib', 'Cross Bracing'),
    'xb_end_a': ('Rib', 'Cross Bracing'),
    'xb_start_b': ('Rib', 'Cross Bracing'),
    'xb_end_b': ('Rib', 'Cross Bracing'),
    'xb_start_c': ('Rib', 'Cross Bracing'),
    'xb_end_c': ('Rib', 'Cross Bracing'),
    
    'diag1_y_main': ('Spar', 'Diag Spars'),
    'diag1_y_rear': ('Spar', 'Diag Spars'),
    'diag2_y_main': ('Spar', 'Diag Spars'),
    'diag2_y_rear': ('Spar', 'Diag Spars'),
    
    'conn1_y': ('Export3D', 'Connectors'),
    'conn2_y': ('Export3D', 'Connectors'),
    'conn3_y': ('Export3D', 'Connectors'),
    'conn4_y': ('Export3D', 'Connectors'),
    'conn1_type': ('Export3D', 'Connectors'),
    'conn2_type': ('Export3D', 'Connectors'),
    'conn3_type': ('Export3D', 'Connectors'),
    'conn4_type': ('Export3D', 'Connectors'),
}

lines = code.split('\n')
new_lines = []
for line in lines:
    if "'tab': 'Missing'" in line or "'tab': 'Unknown'" in line:
        for k, (t, g) in replacements.items():
            if f"'id': '{k}'" in line:
                line = line.replace("'tab': 'Missing'", f"'tab': '{t}'")
                line = line.replace("'group': 'Missing'", f"'group': '{g}'")
                line = line.replace("'tab': 'Unknown'", f"'tab': '{t}'")
                line = line.replace("'group': 'Unknown'", f"'group': '{g}'")
                break
    new_lines.append(line)

with open("ui/param_spec.py", "w") as f:
    f.write('\n'.join(new_lines))

print("Fixed Missing tabs")

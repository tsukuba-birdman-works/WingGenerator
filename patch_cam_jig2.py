import re

with open('core/cam_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_vars = """        # Determine spar parameters from UI/Config values
        d_m = float(params.get('spar_hole_dia', '0.0'))
        d_f = float(params.get('front_spar_dia', '0.0'))
        d_r = float(params.get('rear_spar_dia', '0.0'))

        d_b1 = float(params.get('bolt1_dia', '0.0'))
        d_b2 = float(params.get('bolt2_dia', '0.0'))
        d_xb = float(params.get('xbrace_dia', '0.0'))"""

new_vars = """        # Determine spar parameters from UI/Config values
        if is_jig:
            d_m = d_f = d_r = d_b1 = d_b2 = d_xb = 0.0
            final_truss_holes = []
            diag_poly_pts_list = []
            tabs_active = False  # Disable tabs for jigs typically, or keep it? Jigs usually don't need tabs. Or do they? Let's leave tabs_active as is, but jigs don't have tab centers.
        else:
            d_m = float(params.get('spar_hole_dia', '0.0'))
            d_f = float(params.get('front_spar_dia', '0.0'))
            d_r = float(params.get('rear_spar_dia', '0.0'))

            d_b1 = float(params.get('bolt1_dia', '0.0'))
            d_b2 = float(params.get('bolt2_dia', '0.0'))
            d_xb = float(params.get('xbrace_dia', '0.0'))"""

content = content.replace(old_vars, new_vars)

with open('core/cam_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched variables in cam_engine for jig")

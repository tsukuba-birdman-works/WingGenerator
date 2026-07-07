import re

with open('core/cam_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """        # 2. Process Inner Holes
        # Main Spar Hole"""

new_code = """        # 2. Process Inner Holes
        if not is_jig:
            # Main Spar Hole"""

# I need to indent all hole generation code under `if not is_jig:`.
# Alternatively, I can just clear d_m, d_f, d_r, d_b1, d_b2, d_xb, etc if is_jig is True, and set final_truss_holes=[], etc.

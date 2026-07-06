import re

with open('ui/batch_mode.py', 'r') as f: code = f.read()

target_float = "**{k: self.safe_float(getattr(self, k)) for k in ['joint_length', 'wing_span', 'chord_root', 'chord_tip', 'spar_pos_root', 'spar_pos_tip', 'washout_root', 'washout_tip', 'spar_hole_dia', 'front_spar_dx', 'front_spar_dy', 'front_spar_dia', 'rear_spar_dx', 'rear_spar_dy', 'rear_spar_dia', 'plank_start', 'plank_end', 'plank_thick', 'plank_part_start', 'plank_part_end', 'te_cut', 'beam_width', 'edge_beam_width', 'margin_spar', 'margin_bolt', 'margin_outer', 'margin_outer_edge', 'base_truss_angle', 'truss_fillet', 'min_hole_dia', 'xbrace_dia', 'rib_thick', 'cr_thick', 'te_cap_thick', 'rc1_start', 'rc1_end', 'rc1_thick', 'rc1_width', 'rc2_start', 'rc2_end', 'rc2_thick', 'rc2_width'] if hasattr(self, k)},"
repl_float = "            **{k: self.safe_float(self.pm.vars[k]) for k in ['joint_length', 'wing_span', 'chord_root', 'chord_tip', 'spar_pos_root', 'spar_pos_tip', 'washout_root', 'washout_tip', 'spar_hole_dia', 'front_spar_dx', 'front_spar_dy', 'front_spar_dia', 'rear_spar_dx', 'rear_spar_dy', 'rear_spar_dia', 'plank_start', 'plank_end', 'plank_thick', 'plank_part_start', 'plank_part_end', 'te_cut', 'beam_width', 'edge_beam_width', 'margin_spar', 'margin_bolt', 'margin_outer', 'margin_outer_edge', 'base_truss_angle', 'truss_fillet', 'min_hole_dia', 'xbrace_dia', 'rib_thick', 'cr_thick', 'te_cap_thick', 'rc1_start', 'rc1_end', 'rc1_thick', 'rc1_width', 'rc2_start', 'rc2_end', 'rc2_thick', 'rc2_width'] if k in self.pm.vars},"

if target_float in code:
    code = code.replace(target_float, repl_float)
else:
    print("target_float not found in exact string format, trying regex with dotall")
    import re
    # Just replace getattr(self, k) with self.pm.vars[k] inside the list comprehension
    code = re.sub(r"\*\*\{k: self\.safe_float\(getattr\(self, k\)\) for k in \[(.*?)\] if hasattr\(self, k\)\},",
                  r"**{k: self.safe_float(self.pm.vars[k]) for k in [\1] if k in self.pm.vars},", code, flags=re.DOTALL)

code = re.sub(r"\*\*\{k: self\.safe_int\(getattr\(self, k\)\) for k in \[(.*?)\] if hasattr\(self, k\)\},",
              r"**{k: self.safe_int(self.pm.vars[k]) for k in [\1] if k in self.pm.vars},", code, flags=re.DOTALL)

with open('ui/batch_mode.py', 'w') as f: f.write(code)

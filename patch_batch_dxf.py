import re

with open('ui/batch_mode.py', 'r') as f: code = f.read()

# Replace the part fetching from getattr(self, k) with checking self.pm.vars
target_str = r"\*\*\{k: getattr\(self, k\)\.get\(\) for k in \['export_main_spar',.*?if hasattr\(self, k\)\},"
replacement = """            **{k: self.pm.vars[k].get() for k in ['export_main_spar', 'export_front_spar', 'export_rear_spar', 'export_plank', 'export_te', 'export_connectors', 'export_stringers', 'export_xbrace_wires', 'export_diag_spars', 'export_carbon_ribs', 'export_te_caps', 'export_rib_caps', 'export_film', 'dxf_part_outline', 'dxf_part_holes', 'dxf_part_truss', 'dxf_part_plank', 'dxf_part_te', 'dxf_part_caps', 'dxf_target_ribs', 'dxf_target_carbon', 'dxf_target_jigs', 'dxf_all_in_one'] if k in self.pm.vars},"""

code = re.sub(target_str, replacement, code, flags=re.DOTALL)

# Also fix dxf_merge_margin which might be in pm.vars
target_str_margin = r"'dxf_merge_margin': getattr\(self, 'safe_float'\)\(getattr\(self, 'dxf_merge_margin', 50\.0\)\) if hasattr\(self, 'dxf_merge_margin'\) else 50\.0,"
replacement_margin = """            'dxf_merge_margin': float(self.pm.vars['dxf_merge_margin'].get()) if 'dxf_merge_margin' in self.pm.vars else 50.0,"""
code = re.sub(target_str_margin, replacement_margin, code, flags=re.DOTALL)

with open('ui/batch_mode.py', 'w') as f: f.write(code)

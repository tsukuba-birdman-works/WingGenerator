with open('ui/batch_mode.py', 'r') as f:
    content = f.read()

import re

old_str = r"""            \*\*\{k: getattr\(self, k\).get\(\) for k in \['export_main_spar', 'export_front_spar', 'export_rear_spar', 'export_plank', 'export_te', 'export_connectors', 'export_stringers', 'export_xbrace_wires', 'export_diag_spars', 'export_carbon_ribs', 'export_te_caps', 'export_rib_caps', 'export_film'\] if hasattr\(self, k\)\},"""

new_str = """            **{k: getattr(self, k).get() for k in ['export_main_spar', 'export_front_spar', 'export_rear_spar', 'export_plank', 'export_te', 'export_connectors', 'export_stringers', 'export_xbrace_wires', 'export_diag_spars', 'export_carbon_ribs', 'export_te_caps', 'export_rib_caps', 'export_film', 'dxf_part_outline', 'dxf_part_holes', 'dxf_part_truss', 'dxf_part_plank', 'dxf_part_te', 'dxf_part_caps', 'dxf_target_ribs', 'dxf_target_carbon', 'dxf_target_jigs', 'dxf_all_in_one'] if hasattr(self, k)},
            'dxf_merge_margin': getattr(self, 'safe_float')(getattr(self, 'dxf_merge_margin', 50.0)) if hasattr(self, 'dxf_merge_margin') else 50.0,"""

content = re.sub(old_str, new_str, content)

with open('ui/batch_mode.py', 'w') as f:
    f.write(content)

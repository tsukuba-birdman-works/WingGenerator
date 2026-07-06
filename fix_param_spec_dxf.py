with open('ui/param_spec.py', 'r') as f:
    content = f.read()

import re

old_block = r"""    \{'id': 'dxf_export_carbon', 'type': 'str', 'default': "''", 'tab': 'DXF', 'group': 'Layer Names', 'label': 'Carbon', 'widget': 'entry'\},
    \{'id': 'dxf_export_plank', 'type': 'str', 'default': "''", 'tab': 'DXF', 'group': 'Layer Names', 'label': 'Plank', 'widget': 'entry'\},
    \{'id': 'dxf_export_ribs', 'type': 'str', 'default': "''", 'tab': 'DXF', 'group': 'Layer Names', 'label': 'Ribs', 'widget': 'entry'\},
    \{'id': 'dxf_export_stringer', 'type': 'str', 'default': "''", 'tab': 'DXF', 'group': 'Layer Names', 'label': 'Stringer', 'widget': 'entry'\},
    \{'id': 'dxf_export_te', 'type': 'str', 'default': "''", 'tab': 'DXF', 'group': 'Layer Names', 'label': 'Te', 'widget': 'entry'\},"""

new_block = """    # DXF Parts Options
    {'id': 'dxf_part_outline', 'type': 'bool', 'default': True, 'tab': 'DXF', 'group': 'Parts Output', 'label': 'Rib Outline', 'widget': 'checkbutton'},
    {'id': 'dxf_part_holes', 'type': 'bool', 'default': True, 'tab': 'DXF', 'group': 'Parts Output', 'label': 'Holes (Spar, Bolt)', 'widget': 'checkbutton'},
    {'id': 'dxf_part_truss', 'type': 'bool', 'default': True, 'tab': 'DXF', 'group': 'Parts Output', 'label': 'Truss & X-Brace', 'widget': 'checkbutton'},
    {'id': 'dxf_part_plank', 'type': 'bool', 'default': True, 'tab': 'DXF', 'group': 'Parts Output', 'label': 'Plank', 'widget': 'checkbutton'},
    {'id': 'dxf_part_te', 'type': 'bool', 'default': True, 'tab': 'DXF', 'group': 'Parts Output', 'label': 'TE Part', 'widget': 'checkbutton'},
    {'id': 'dxf_part_caps', 'type': 'bool', 'default': True, 'tab': 'DXF', 'group': 'Parts Output', 'label': 'Caps (Rib & TE)', 'widget': 'checkbutton'},
    
    # DXF Targets Options
    {'id': 'dxf_target_ribs', 'type': 'bool', 'default': True, 'tab': 'DXF', 'group': 'Export Targets', 'label': 'Normal Ribs', 'widget': 'checkbutton'},
    {'id': 'dxf_target_carbon', 'type': 'bool', 'default': True, 'tab': 'DXF', 'group': 'Export Targets', 'label': 'Carbon Ribs', 'widget': 'checkbutton'},
    {'id': 'dxf_target_jigs', 'type': 'bool', 'default': True, 'tab': 'DXF', 'group': 'Export Targets', 'label': 'Jigs', 'widget': 'checkbutton'},
    
    # DXF All-in-One Options
    {'id': 'dxf_all_in_one', 'type': 'bool', 'default': False, 'tab': 'DXF', 'group': 'Export Format', 'label': 'All in One DXF', 'widget': 'checkbutton'},
    {'id': 'dxf_merge_margin', 'type': 'float', 'default': 50.0, 'tab': 'DXF', 'group': 'Export Format', 'label': 'Merge Margin Y (mm)', 'widget': 'entry'},"""

content_new = re.sub(old_block, new_block, content, flags=re.MULTILINE)
with open('ui/param_spec.py', 'w') as f:
    f.write(content_new)

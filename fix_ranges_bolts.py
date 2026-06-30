import re
import ast
import pprint

with open("ui/param_spec.py", "r") as f:
    content = f.read()

# Since parsing manually with regex is tricky for adding new keys, let's use a simpler approach.
# We will use python to load the module, modify the dicts, and write them back.
import sys
sys.path.insert(0, '.')
from ui.param_spec import BATCH_PARAMS, SINGLE_PARAMS

def process_params(params):
    for p in params:
        pid = p['id']
        
        # Ranges
        if pid == 'plank_start':
            p['widget'] = 'range_pair'
            p['linked_id'] = 'plank_end'
            p['label'] = 'Actual Range (%)'
        elif pid == 'plank_end':
            p['widget'] = 'hidden'
            
        elif pid == 'plank_part_start':
            p['widget'] = 'range_pair'
            p['linked_id'] = 'plank_part_end'
            p['label'] = 'Cut Range (%)'
        elif pid == 'plank_part_end':
            p['widget'] = 'hidden'
            
        elif pid == 'rc1_start':
            p['widget'] = 'range_pair'
            p['linked_id'] = 'rc1_end'
            p['label'] = 'Range (%)'
        elif pid == 'rc1_end':
            p['widget'] = 'hidden'
            
        elif pid == 'rc2_start':
            p['widget'] = 'range_pair'
            p['linked_id'] = 'rc2_end'
            p['label'] = 'Range (%)'
        elif pid == 'rc2_end':
            p['widget'] = 'hidden'
            
        # Bolts
        elif pid in ['root_bolt1_dia', 'root_bolt2_dia', 'tip_bolt1_dia', 'tip_bolt2_dia']:
            p['widget'] = 'bolt_triple'
            prefix = pid.replace('_dia', '')
            p['linked_x'] = f"{prefix}_dx"
            p['linked_y'] = f"{prefix}_dy"
            p['label'] = 'Params (mm)'
        elif pid in ['root_bolt1_dx', 'root_bolt1_dy', 'root_bolt2_dx', 'root_bolt2_dy',
                     'tip_bolt1_dx', 'tip_bolt1_dy', 'tip_bolt2_dx', 'tip_bolt2_dy']:
            p['widget'] = 'hidden'

process_params(BATCH_PARAMS)
process_params(SINGLE_PARAMS)

with open("ui/param_spec.py", "w") as f:
    f.write("BATCH_PARAMS = [\n")
    for p in BATCH_PARAMS:
        f.write(f"    {repr(p)},\n")
    f.write("]\n\n")
    f.write("SINGLE_PARAMS = [\n")
    for p in SINGLE_PARAMS:
        f.write(f"    {repr(p)},\n")
    f.write("]\n")

print("param_spec.py updated for range_pair and bolt_triple")

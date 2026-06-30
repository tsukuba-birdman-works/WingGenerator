import sys
sys.path.insert(0, '.')
from ui.param_spec import BATCH_PARAMS, SINGLE_PARAMS

def process_params(params):
    for p in params:
        pid = p['id']
        
        # Cross Bracing (X-brace)
        if pid == 'xb_start_a':
            p['widget'] = 'range_pair'
            p['linked_id'] = 'xb_end_a'
            p['label'] = 'A Start~End (%)'
        elif pid == 'xb_end_a':
            p['widget'] = 'hidden'
            
        elif pid == 'xb_start_b':
            p['widget'] = 'range_pair'
            p['linked_id'] = 'xb_end_b'
            p['label'] = 'B Start~End (%)'
        elif pid == 'xb_end_b':
            p['widget'] = 'hidden'
            
        elif pid == 'xb_start_c':
            p['widget'] = 'range_pair'
            p['linked_id'] = 'xb_end_c'
            p['label'] = 'C Start~End (%)'
        elif pid == 'xb_end_c':
            p['widget'] = 'hidden'
            
        elif pid == 'xbrace_dia':
            p['label'] = 'Outer Dia (mm)'
            
        elif pid == 'xbrace_wire_dia':
            p['label'] = 'Wire Dia (mm)'

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


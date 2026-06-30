import sys
sys.path.insert(0, '.')
from ui.param_spec import BATCH_PARAMS, SINGLE_PARAMS

def process_params(params):
    # Remove unused
    to_remove = ['carbon_le_cut', 'carbon_offset', 'carbon_te_cut', 'cr_root_out_te', 'cr_tip_out_te']
    params[:] = [p for p in params if p['id'] not in to_remove]
    
    for p in params:
        pid = p['id']
        
        # Diag Connector
        if pid == 'diag1_active':
            p['group'] = 'Diag Connector 1'
        elif pid == 'diag1_y_main':
            p['group'] = 'Diag Connector 1'
            p['widget'] = 'range_pair'
            p['linked_id'] = 'diag1_y_rear'
            p['label'] = 'Y Main~Rear (mm)'
        elif pid == 'diag1_y_rear':
            p['group'] = 'Diag Connector 1'
            p['widget'] = 'hidden'

        elif pid == 'diag2_active':
            p['group'] = 'Diag Connector 2'
        elif pid == 'diag2_y_main':
            p['group'] = 'Diag Connector 2'
            p['widget'] = 'range_pair'
            p['linked_id'] = 'diag2_y_rear'
            p['label'] = 'Y Main~Rear (mm)'
        elif pid == 'diag2_y_rear':
            p['group'] = 'Diag Connector 2'
            p['widget'] = 'hidden'
            
        # Carbon Ribs
        elif pid == 'cr_root_in_act':
            p['group'] = 'Root Carbon Rib'
            p['label'] = 'Inner Active'
        elif pid == 'cr_root_out_act':
            p['group'] = 'Root Carbon Rib'
            p['label'] = 'Outer Active'
        elif pid == 'cr_root_in_te':
            p['group'] = 'Root Carbon Rib'
            p['label'] = 'Inner TE Cut'

        elif pid == 'cr_tip_in_act':
            p['group'] = 'Tip Carbon Rib'
            p['label'] = 'Inner Active'
        elif pid == 'cr_tip_out_act':
            p['group'] = 'Tip Carbon Rib'
            p['label'] = 'Outer Active'
        elif pid == 'cr_tip_in_te':
            p['group'] = 'Tip Carbon Rib'
            p['label'] = 'Inner TE Cut'
            
        elif pid == 'cr_thick':
            p['group'] = 'Carbon Ribs General'
            p['label'] = 'Thickness (mm)'

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

import sys
sys.path.insert(0, '.')
from ui.param_spec import BATCH_PARAMS, SINGLE_PARAMS

def process_params(params):
    # Remove cr_root_in_te and cr_tip_in_te (they will be implicitly True)
    # Add back cr_root_out_te and cr_tip_out_te
    to_remove = ['cr_root_in_te', 'cr_tip_in_te', 'carbon_le_cut', 'carbon_offset', 'carbon_te_cut']
    params[:] = [p for p in params if p['id'] not in to_remove]
    
    # We need to make sure cr_root_out_te and cr_tip_out_te exist. If they don't, we add them later.
    has_root_out_te = any(p['id'] == 'cr_root_out_te' for p in params)
    has_tip_out_te = any(p['id'] == 'cr_tip_out_te' for p in params)
    
    if not has_root_out_te:
        params.append({'id': 'cr_root_out_te', 'type': 'bool', 'default': False, 'tab': 'Rib', 'group': 'Root Carbon Rib', 'label': 'Outer TE Cut', 'widget': 'checkbutton'})
    if not has_tip_out_te:
        params.append({'id': 'cr_tip_out_te', 'type': 'bool', 'default': False, 'tab': 'Rib', 'group': 'Tip Carbon Rib', 'label': 'Outer TE Cut', 'widget': 'checkbutton'})

    for p in params:
        pid = p['id']
        tab = p.get('tab', '')
        group = p.get('group', '')
        
        # Carbon Ribs update
        if pid == 'cr_root_out_te':
            p['tab'] = 'Rib'
            p['group'] = 'Root Carbon Rib'
            p['label'] = 'Outer TE Cut'
        elif pid == 'cr_tip_out_te':
            p['tab'] = 'Rib'
            p['group'] = 'Tip Carbon Rib'
            p['label'] = 'Outer TE Cut'
            
        # Tab Renaming
        if tab == 'Stringer':
            p['tab'] = 'Brace & Connector'
            
        if group in ['Diag Connector 1', 'Diag Connector 2']:
            p['tab'] = 'Brace & Connector'
            
        if group == 'Connectors' and tab == 'Export3D':
            p['tab'] = 'Brace & Connector'

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


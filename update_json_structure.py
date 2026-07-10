import json
import os
import glob
from ui.param_spec import BATCH_PARAMS

def create_structured_json(flat_data):
    structured = {
        "Project Settings": {
            "Paths": {
                "file1_path": flat_data.get("file1_path", ""),
                "file2_path": flat_data.get("file2_path", ""),
                "export_dir": flat_data.get("export_dir", "")
            },
            "Settings": {
                "jig_y_positions": flat_data.get("jig_y_positions", "")
            }
        }
    }
    
    for p in BATCH_PARAMS:
        tab = p.get('tab', 'Other')
        group = p.get('group', 'General')
        key = p['id']
        
        if tab not in structured:
            structured[tab] = {}
        if group not in structured[tab]:
            structured[tab][group] = {}
            
        if key in flat_data:
            structured[tab][group][key] = flat_data[key]
            
    # Remove empty dicts
    clean_structured = {}
    for t_k, t_v in structured.items():
        clean_group = {g_k: g_v for g_k, g_v in t_v.items() if g_v}
        if clean_group:
            clean_structured[t_k] = clean_group
            
    return clean_structured

def process_preset(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    flat_data = {}
    if any(isinstance(v, dict) for v in data.values()):
        for top_k, top_v in data.items():
            if isinstance(top_v, dict):
                for mid_k, mid_v in top_v.items():
                    if isinstance(mid_v, dict):
                        for k, v in mid_v.items():
                            flat_data[k] = v
                    else:
                        flat_data[mid_k] = mid_v
            else:
                flat_data[top_k] = top_v
    else:
        flat_data = data
        
    if 'rear_spar_dx' in flat_data:
        flat_data['rear_spar_dx_root'] = flat_data['rear_spar_dx']
        flat_data['rear_spar_dx_tip'] = flat_data['rear_spar_dx']
    if 'rear_spar_dy' in flat_data:
        flat_data['rear_spar_dy_root'] = flat_data['rear_spar_dy']
        flat_data['rear_spar_dy_tip'] = flat_data['rear_spar_dy']
        
    structured = create_structured_json(flat_data)
    
    with open(filepath, 'w') as f:
        json.dump(structured, f, indent=4)
        
for f in glob.glob("preset/*.json"):
    print(f"Processing {f}")
    process_preset(f)

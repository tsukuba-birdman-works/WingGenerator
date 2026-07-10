import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
from utils.config import ConfigHelper
import glob
import os

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

for f in glob.glob("preset/*.json"):
    print(f"Formatting {f}...")
    # Manually load the flat/semi-structured file
    import json
    with open(f, 'r') as fp:
        data = json.load(fp)
    
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
        flat_data = data.get("variables", data)
    
    # Inject into app
    vars_dict = app.get_all_vars()
    for k, v in flat_data.items():
        if k in vars_dict:
            var = vars_dict[k]
            if isinstance(var, tk.BooleanVar):
                var.set(v in [True, "True", "true", 1, "1"])
            elif isinstance(var, tk.IntVar):
                try: var.set(int(v))
                except ValueError: var.set(v)
            elif isinstance(var, tk.DoubleVar):
                try: var.set(float(v))
                except ValueError: var.set(v)
            else:
                var.set(str(v))
                
    # Now use ConfigHelper logic to format and save
    # But ConfigHelper.save_config shows a messagebox! Let's just rip its logic:
    all_vars = app.get_all_vars()
    structured = {
        "Project Settings": {
            "Paths": {
                "file1_path": all_vars.get("file1_path", tk.StringVar(value="")).get(),
                "file2_path": all_vars.get("file2_path", tk.StringVar(value="")).get(),
                "export_dir": all_vars.get("export_dir", tk.StringVar(value="")).get()
            }
        }
    }
    structured_keys = {"file1_path", "file2_path", "export_dir"}
    for p in app.pm.spec:
        tab = p.get('tab', 'Other')
        group = p.get('group', 'General')
        key = p['id']
        if tab not in structured:
            structured[tab] = {}
        if group not in structured[tab]:
            structured[tab][group] = {}
        if key in all_vars:
            structured[tab][group][key] = all_vars[key].get()
            structured_keys.add(key)
    extras = {}
    for k, v in all_vars.items():
        if k not in structured_keys:
            extras[k] = v.get()
    if extras:
        structured["Extras"] = {"Custom Features": extras}
        
    clean_structured = {}
    for t_k, t_v in structured.items():
        clean_group = {g_k: g_v for g_k, g_v in t_v.items() if (g_v or isinstance(g_v, dict))}
        if clean_group:
            clean_structured[t_k] = clean_group
            
    with open(f, "w", encoding="utf-8") as fp:
        json.dump(clean_structured, fp, indent=4, ensure_ascii=False)

print("Done")

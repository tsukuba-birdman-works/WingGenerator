import json
import tkinter as tk
from tkinter import filedialog, messagebox

# ==========================================
# UI & Config Helper Class (JSON-based)
# ==========================================
class ConfigHelper:

    @staticmethod
    def save_config(app, mode_name):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title=f"Save {mode_name} Config")
        if not path: return
        
        try:
            # 1. Collect all variables
            all_vars = app.get_all_vars()
            
            # 2. Build structured JSON
            structured = {
                "Project Settings": {
                    "Paths": {
                        "file1_path": all_vars.get("file1_path", tk.StringVar(value="")).get(),
                        "file2_path": all_vars.get("file2_path", tk.StringVar(value="")).get(),
                        "export_dir": all_vars.get("export_dir", tk.StringVar(value="")).get()
                    }
                }
            }
            
            # Track which keys we've structured
            structured_keys = {"file1_path", "file2_path", "export_dir"}
            
            if hasattr(app, 'pm'):
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
                        
            # Any remaining keys go into Extras
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
                    
            with open(path, "w", encoding="utf-8") as f:
                json.dump(clean_structured, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", f"Saved config to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    @staticmethod
    def load_config(app):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
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
                flat_data = data.get("variables", data)
                
            # Backward compatibility logic
            if 'rear_spar_dx' in flat_data:
                flat_data['rear_spar_dx_root'] = flat_data['rear_spar_dx']
                flat_data['rear_spar_dx_tip'] = flat_data['rear_spar_dx']
            if 'rear_spar_dy' in flat_data:
                flat_data['rear_spar_dy_root'] = flat_data['rear_spar_dy']
                flat_data['rear_spar_dy_tip'] = flat_data['rear_spar_dy']
                
            app.is_updating_ui = True
            vars_dict = app.get_all_vars()
            
            for key, val in flat_data.items():
                if key in vars_dict:
                    var = vars_dict[key]
                    if isinstance(var, tk.BooleanVar):
                        var.set(val in [True, "True", "true", 1, "1"])
                    elif isinstance(var, tk.IntVar):
                        try: var.set(int(val))
                        except ValueError: var.set(val)
                    elif isinstance(var, tk.DoubleVar):
                        try: var.set(float(val))
                        except ValueError: var.set(val)
                    else:
                        var.set(str(val))
                        
            app.is_updating_ui = False
            if hasattr(app, 'calculate_y_positions'): app.calculate_y_positions()
            if hasattr(app, 'update_preview_full'): app.update_preview_full()
            elif hasattr(app, 'update_preview'): app.update_preview()
            
            messagebox.showinfo("Success", f"Loaded config from:\n{path}")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

# Replace save_config and load_config
save_config_func = """    def save_config(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Save Config")
        if not filepath:
            return
        try:
            # Build strictly bold JSON
            structured = {
                "Project Settings": {
                    "Paths": {
                        "file1_path": getattr(self, "file1_path").get() if hasattr(self, "file1_path") else "",
                        "file2_path": getattr(self, "file2_path").get() if hasattr(self, "file2_path") else "",
                        "export_dir": getattr(self, "export_dir").get() if hasattr(self, "export_dir") else ""
                    },
                    "Settings": {
                        "jig_y_positions": getattr(self, "pm").vars.get("jig_y_positions").get() if "jig_y_positions" in getattr(self, "pm").vars else ""
                    }
                }
            }
            
            for p in self.pm.spec:
                tab = p.get('tab', 'Other')
                group = p.get('group', 'General')
                key = p['id']
                
                if tab not in structured:
                    structured[tab] = {}
                if group not in structured[tab]:
                    structured[tab][group] = {}
                    
                if hasattr(self, key):
                    val = getattr(self, key).get()
                    structured[tab][group][key] = val
                    
            # Remove empty sections
            clean_structured = {}
            for t_k, t_v in structured.items():
                clean_group = {g_k: g_v for g_k, g_v in t_v.items() if g_v}
                if clean_group:
                    clean_structured[t_k] = clean_group
                    
            with open(filepath, 'w') as f:
                import json
                json.dump(clean_structured, f, indent=4)
            messagebox.showinfo("Success", f"Configuration saved to {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\\n{e}")"""

load_config_func = """    def load_config(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], title="Load Config")
        if not filepath:
            return
        try:
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Flatten structured data completely
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
                
            # Handle manual backward compatibility
            if 'rear_spar_dx' in flat_data:
                flat_data['rear_spar_dx_root'] = flat_data['rear_spar_dx']
                flat_data['rear_spar_dx_tip'] = flat_data['rear_spar_dx']
            if 'rear_spar_dy' in flat_data:
                flat_data['rear_spar_dy_root'] = flat_data['rear_spar_dy']
                flat_data['rear_spar_dy_tip'] = flat_data['rear_spar_dy']
                
            for k, v in flat_data.items():
                if hasattr(self, k):
                    getattr(self, k).set(v)
                elif k in self.pm.vars:
                    self.pm.vars[k].set(v)
            messagebox.showinfo("Loaded", f"Configuration loaded from {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration:\\n{e}")"""

# Regex substitute
text = re.sub(r"    def save_config\(self\):.*?    def load_config\(self\):", save_config_func + "\n\n    def load_config(self):", text, flags=re.DOTALL)
text = re.sub(r"    def load_config\(self\):.*?(?=\n\n    def |\Z)", load_config_func, text, flags=re.DOTALL)

with open('ui/batch_mode.py', 'w') as f:
    f.write(text)

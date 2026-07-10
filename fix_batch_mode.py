import re
import os

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

# 1. Update _get_builder_params to include the new variables instead of rear_spar_dx
old_params = " 'rear_spar_dx', 'rear_spar_dy', 'rear_spar_dia',"
new_params = " 'rear_spar_dx_root', 'rear_spar_dy_root', 'rear_spar_dx_tip', 'rear_spar_dy_tip', 'rear_spar_dia',"
if old_params in text:
    text = text.replace(old_params, new_params)

# 2. Add structural save/load to batch_mode.py
# First, update save_config
save_config_func = """    def save_config(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Save Config")
        if not filepath:
            return
        try:
            # Build structured JSON dict
            structured_data = {}
            for p in self.pm.spec:
                group = p.get('group', 'General')
                if group not in structured_data:
                    structured_data[group] = {}
                key = p['id']
                if hasattr(self, key):
                    val = getattr(self, key).get()
                    structured_data[group][key] = val
                    
            with open(filepath, 'w') as f:
                import json
                json.dump(structured_data, f, indent=4)
            messagebox.showinfo("Success", f"Configuration saved to {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\\n{e}")"""

# 3. Update load_config
load_config_func = """    def load_config(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], title="Load Config")
        if not filepath:
            return
        try:
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Flatten structured data
            flat_data = {}
            # Check if old format (flat) or new format (nested)
            is_nested = any(isinstance(v, dict) for v in data.values())
            
            if is_nested:
                for group, props in data.items():
                    if isinstance(props, dict):
                        for k, v in props.items():
                            flat_data[k] = v
            else:
                flat_data = data
                
            # Backward compatibility for rear_spar_dx -> rear_spar_dx_root & tip
            if 'rear_spar_dx' in flat_data:
                flat_data['rear_spar_dx_root'] = flat_data['rear_spar_dx']
                flat_data['rear_spar_dx_tip'] = flat_data['rear_spar_dx']
            if 'rear_spar_dy' in flat_data:
                flat_data['rear_spar_dy_root'] = flat_data['rear_spar_dy']
                flat_data['rear_spar_dy_tip'] = flat_data['rear_spar_dy']
                
            for k, v in flat_data.items():
                if hasattr(self, k):
                    getattr(self, k).set(v)
            messagebox.showinfo("Loaded", f"Configuration loaded from {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration:\\n{e}")"""


# Find and replace the old save_config and load_config methods
text = re.sub(r"    def save_config\(self\):.*?    def load_config\(self\):", save_config_func + "\n\n    def load_config(self):", text, flags=re.DOTALL)
text = re.sub(r"    def load_config\(self\):.*?(?=\n\n    def |\Z)", load_config_func, text, flags=re.DOTALL)

with open('ui/batch_mode.py', 'w') as f:
    f.write(text)

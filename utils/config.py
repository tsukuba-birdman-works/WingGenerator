import json
import tkinter as tk
from tkinter import filedialog, messagebox

# ==========================================
# UI & Config Helper Class (JSON-based)
# ==========================================
class ConfigHelper:

    @staticmethod
    def save_config(app, mode_name):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not path: return
        try:
            data = {
                "mode": mode_name,
                "variables": {}
            }
            for key, var in app.get_all_vars().items():
                data["variables"][key] = var.get()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
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
            app.is_updating_ui = True
            vars_dict = app.get_all_vars()
            
            # Support both flat and nested JSON structure (to support converted XML files)
            variables = data.get("variables", data)
            for key, val in variables.items():
                if key in vars_dict:
                    var = vars_dict[key]
                    if isinstance(var, tk.BooleanVar):
                        var.set(val in [True, "True", "true", 1, "1"])
                    elif isinstance(var, tk.IntVar):
                        try:
                            var.set(int(val))
                        except ValueError:
                            var.set(val)
                    elif isinstance(var, tk.DoubleVar):
                        try:
                            var.set(float(val))
                        except ValueError:
                            var.set(val)
                    else:
                        var.set(str(val))
            app.is_updating_ui = False
            if hasattr(app, 'calculate_y_positions'): app.calculate_y_positions()
            if hasattr(app, 'update_preview_full'): app.update_preview_full()
            else: app.update_preview()
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
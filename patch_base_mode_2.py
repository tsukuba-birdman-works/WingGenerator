import re

with open('ui/base_mode.py', 'r', encoding='utf-8') as f:
    content = f.read()

end_str = "    def get_cam_vars(self):"

start_idx = content.find(end_str)

new_methods = """
    def save_tool_config(self):
        import json
        from tkinter import filedialog, messagebox
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Save Tool Config")
        if not path: return
        try:
            data = {
                "cam_tool_dia": self.cam_tool_dia.get(),
                "cam_mat_thick": self.cam_mat_thick.get(),
                "cam_safe_z": self.cam_safe_z.get(),
                "cam_feed_rate": self.cam_feed_rate.get(),
                "cam_spindle_speed": self.cam_spindle_speed.get(),
                "cam_extra_depth": self.cam_extra_depth.get(),
                "cam_milling_dir": self.cam_milling_dir.get()
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", f"Saved tool config to:\\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_tool_config(self):
        import json
        from tkinter import filedialog, messagebox
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Load Tool Config")
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "cam_tool_dia" in data: self.cam_tool_dia.set(data["cam_tool_dia"])
            if "cam_mat_thick" in data: self.cam_mat_thick.set(data["cam_mat_thick"])
            if "cam_safe_z" in data: self.cam_safe_z.set(data["cam_safe_z"])
            if "cam_feed_rate" in data: self.cam_feed_rate.set(data["cam_feed_rate"])
            if "cam_spindle_speed" in data: self.cam_spindle_speed.set(data["cam_spindle_speed"])
            if "cam_extra_depth" in data: self.cam_extra_depth.set(data["cam_extra_depth"])
            if "cam_milling_dir" in data: self.cam_milling_dir.set(data["cam_milling_dir"])
            
            messagebox.showinfo("Success", f"Loaded tool config from:\\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

"""

new_content = content[:start_idx] + new_methods + content[start_idx:]

with open('ui/base_mode.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Added save_tool_config and load_tool_config in ui/base_mode.py")

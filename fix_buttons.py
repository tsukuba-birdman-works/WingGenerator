with open("ui/batch_mode.py", "r") as f:
    code = f.read()

buttons_code = """
        if 'Cross Bracing' in self.pm.obj.groups_frames:
            ttk.Button(self.pm.obj.groups_frames['Cross Bracing'], text="Auto Set X-Brace", command=self.auto_set_xbrace_zones).grid(row=99, column=0, columnspan=4, pady=5)
            
        if 'CNC' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['CNC'], text="Export G-Code", command=self.export_gcode_all).pack(fill=tk.X, padx=10, pady=5)
            ttk.Button(self.pm.obj.tabs_frames['CNC'], text="Open in Foam CAM", command=self.open_in_foam_cam).pack(fill=tk.X, padx=10, pady=5)
            
        if 'DXF' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['DXF'], text="Export DXF", command=self.export_dxf).pack(fill=tk.X, padx=10, pady=5)
"""

code = code.replace("        # Add Export Buttons to Export3D tab", buttons_code + "\n        # Add Export Buttons to Export3D tab")

with open("ui/batch_mode.py", "w") as f:
    f.write(code)

print("Restored action buttons")

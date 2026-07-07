import sys, re

with open('ui/single_mode.py', 'r') as f:
    content = f.read()

new_export_dxf = """    def export_dxf(self):
        f1 = self.file1_path.get()
        if not f1 or not os.path.exists(f1): return messagebox.showerror("Error", "Please select valid files.")
        path = filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("DXF Files", "*.dxf")])
        if not path: return
        try:
            params = self.get_rib_parameters(fast_mode=False)
            params.tabs_active = False
            res = self.engine.generate_single_rib(params)
            
            is_jig = (self.dxf_output_target.get() == 'Jig') if hasattr(self, 'dxf_output_target') else False
            layer_name = self.dxf_layer.get() if hasattr(self, 'dxf_layer') else 'Rib'
            
            layer_flags = {'layer': layer_name}
            
            if is_jig:
                jig_y_str = self.jig_y_positions.get() if hasattr(self, 'jig_y_positions') else '20, 80'
                jig_y_list = [float(y.strip()) for y in jig_y_str.split(',') if y.strip()]
                # Generate jig outline (simplified, typically single mode DXF just outputs the rib, 
                # but we'll pass jig_pts if we generated them. single_mode doesn't generate jig pts directly, 
                # but we can output the raw rib points to DXF).
                pts_to_output = res.final_rib_orig # Actually, single mode doesn't generate full jig. Let's output rib.
            else:
                pts_to_output = res[0]

            self.engine.export_dxf(path, res[1], res[0], res[1], self.safe_float(self.spar_hole_dia), 
                                   res[5], 0.0, res[3], 0.0, 
                                   res[7], res[9], 0.0, res[13], res[14], 
                                   res[15], self.safe_float(self.bolt1_dia), res[16], 
                                   res[17], self.safe_float(self.bolt2_dia), res[18], res[19],
                                   layer_flags=layer_flags)
            messagebox.showinfo("Success", f"Saved to:\\n{path}")
        except Exception as e: messagebox.showerror("Export Error", str(e))"""

new_export_obj = """    def export_obj(self):
        f1 = self.file1_path.get()
        if not f1 or not os.path.exists(f1): return messagebox.showerror("Error", "Please select valid files.")
        filepath = filedialog.asksaveasfilename(
            title="Save 3D Model",
            defaultextension=".glb", 
            filetypes=[("glTF Binary", "*.glb"), ("Wavefront OBJ", "*.obj")]
        )
        if not filepath: return
        
        try:
            import trimesh
        except ImportError:
            return messagebox.showerror("Error", "trimesh library is required for 3D export.\\nPlease run: pip install trimesh")

        try:
            params = self.get_rib_parameters(fast_mode=False)
            params.tabs_active = False
            res = self.engine.generate_single_rib(params)
            
            c_m = res[1]
            def to_rel(pts): return np.array(pts) - c_m if len(pts) > 0 else pts
            
            rel_outline = to_rel(res[0])
            rel_holes = []
            for h_idx in [2, 4, 6, 16, 18]:
                if len(res[h_idx]) > 0: rel_holes.append(to_rel(res[h_idx]))
            for h in res[7] + res[8] + res[19]:
                rel_holes.append(to_rel(h))
            
            t_rib = 3.0
            scene_rib_data = [(0.0, t_rib, rel_outline, rel_holes)]
            rc_cap_pts1, rc_cap_pts2 = res[23]
            
            from core.materials import AVAILABLE_MATERIALS
            part_colors = {'Ribs': AVAILABLE_MATERIALS.get('Styrofoam (Blue)', [135, 206, 235, 255])}
            
            Wing3DExporter.export_3d_scene(filepath, scene_rib_data, {}, is_left_wing=False, part_colors=part_colors)
            messagebox.showinfo("Success", f"Saved 3D Model to:\\n{filepath}")
        except Exception as e: messagebox.showerror("Export Error", str(e))"""

content = re.sub(r'    def export_dxf\(self\):.*?except Exception as e: messagebox\.showerror\("Export Error", str\(e\)\)', new_export_dxf, content, flags=re.DOTALL)
content = re.sub(r'    def export_obj\(self\):.*?except Exception as e: messagebox\.showerror\("Export Error", str\(e\)\)', new_export_obj, content, flags=re.DOTALL)

with open('ui/single_mode.py', 'w') as f:
    f.write(content)

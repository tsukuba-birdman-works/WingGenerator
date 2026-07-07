import re

with open('ui/batch_mode.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add create_cnc_selection_ui and update_cnc_selection_ui
cnc_ui_code = """
    def create_cnc_selection_ui(self, parent):
        import tkinter as tk
        from tkinter import ttk

        frame = ttk.LabelFrame(parent, text="Rib/Jig CNC Export Selection")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Select/Deselect All Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(btn_frame, text="Select All", command=lambda: self._set_all_cnc_selection(True)).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Deselect All", command=lambda: self._set_all_cnc_selection(False)).pack(side="left", padx=2)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.cnc_scrollable_frame = ttk.Frame(canvas)

        self.cnc_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.cnc_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.cnc_selection_vars = {}

    def _set_all_cnc_selection(self, state):
        for var in self.cnc_selection_vars.values():
            var.set(state)

    def update_cnc_selection_ui(self):
        import tkinter as tk
        from tkinter import ttk
        if not hasattr(self, 'cnc_scrollable_frame'): return

        for widget in self.cnc_scrollable_frame.winfo_children():
            widget.destroy()

        self.cnc_selection_vars.clear()

        if hasattr(self, 'preview_items'):
            for item in self.preview_items:
                var = tk.BooleanVar(value=True)
                key = f"{item['type']}_{item.get('loc', '')}_{item.get('pos', '')}_{item['idx']}"
                self.cnc_selection_vars[key] = var
                ttk.Checkbutton(self.cnc_scrollable_frame, text=item['label'], variable=var).pack(anchor="w", padx=5)

        try:
            jig_str = self.pm.vars.get('jig_y_positions').get() if 'jig_y_positions' in self.pm.vars else ''
            if jig_str:
                jigs = [float(v.strip()) for v in jig_str.split(',') if v.strip()]
                for j_idx, jy in enumerate(jigs):
                    var = tk.BooleanVar(value=True)
                    key = f"jig_{j_idx}"
                    self.cnc_selection_vars[key] = var
                    ttk.Checkbutton(self.cnc_scrollable_frame, text=f"Jig No.{j_idx} (Y={jy:.1f}mm)", variable=var).pack(anchor="w", padx=5)
        except Exception:
            pass
"""
# Insert after update_dxf_selection_ui
idx = content.find("    def open_in_foam_cam(self):")
content = content[:idx] + cnc_ui_code + "\n" + content[idx:]


# 2. Add self.update_cnc_selection_ui() in calculate_y_positions
idx2 = content.find("self.update_dxf_selection_ui()")
if idx2 != -1:
    content = content[:idx2] + "self.update_dxf_selection_ui()\n            self.update_cnc_selection_ui()" + content[idx2 + len("self.update_dxf_selection_ui()"):]

# 3. Add to create_widgets
idx3 = content.find("if 'CNC' in self.pm.obj.tabs_frames:")
if idx3 != -1:
    insert_str = "            self.create_cnc_selection_ui(self.pm.obj.tabs_frames['CNC'])\n"
    idx4 = content.find("ttk.Button(self.pm.obj.tabs_frames['CNC'], text=\"Export G-Code\"", idx3)
    content = content[:idx4] + insert_str + content[idx4:]

# 4. Modify export_gcode_all
old_export = """            # 1. Export Normal Ribs G-code
            for i, y_local in enumerate(params['y_positions']):
                res = self.engine.generate_rib_at_y(params, y_local, i, params['rib_thick'])
                gcode_str, warnings = cam.generate_gcode(res, params)

                y_global = y_local + params['joint_length']
                filename = f"Rib_{i:02d}_Y{y_global:.1f}.gcode"
                filepath = os.path.join(dir_path, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(gcode_str)

                if warnings:
                    all_warnings.extend([f"Rib {i}: {w}" for w in warnings])
                exported_count += 1

            # 2. Export Carbon Ribs G-code
            for cconf in params['carbon_rib_configs']:
                if not cconf['act']: continue
                idx, y_local = cconf['idx'], params['y_positions'][cconf['idx']]

                te_cut_override = params['te_cut'] if cconf['te'] else 0.0
                res = self.engine.generate_rib_at_y(params, y_local, idx, params['cr_thick'], is_carbon=True, te_cut_override=te_cut_override)
                gcode_str, warnings = cam.generate_gcode(res, params)

                y_global = y_local + params['joint_length']
                filename = f"CarbonRib_{cconf['loc'].capitalize()}_{cconf['pos'].capitalize()}_Y{y_global:.1f}.gcode"
                filepath = os.path.join(dir_path, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(gcode_str)

                if warnings:
                    all_warnings.extend([f"CarbonRib {cconf['loc']}_{cconf['pos']}: {w}" for w in warnings])
                exported_count += 1"""

new_export = """            # Get selections
            cnc_selections = {k: v.get() for k, v in getattr(self, 'cnc_selection_vars', {}).items()}

            # 1. Export Normal Ribs G-code
            for i, y_local in enumerate(params['y_positions']):
                key = f"rib___{i}"
                if key in cnc_selections and not cnc_selections[key]:
                    continue
                res = self.engine.generate_rib_at_y(params, y_local, i, params['rib_thick'])
                gcode_str, warnings = cam.generate_gcode(res, params)

                y_global = y_local + params['joint_length']
                filename = f"Rib_{i:02d}_Y{y_global:.1f}.gcode"
                filepath = os.path.join(dir_path, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(gcode_str)

                if warnings:
                    all_warnings.extend([f"Rib {i}: {w}" for w in warnings])
                exported_count += 1

            # 2. Export Carbon Ribs G-code
            for cconf in params['carbon_rib_configs']:
                if not cconf['act']: continue
                idx, y_local = cconf['idx'], params['y_positions'][cconf['idx']]

                key = f"carbon_{cconf['loc']}_{cconf['pos']}_{idx}"
                if key in cnc_selections and not cnc_selections[key]:
                    continue

                te_cut_override = params['te_cut'] if cconf['te'] else 0.0
                res = self.engine.generate_rib_at_y(params, y_local, idx, params['cr_thick'], is_carbon=True, te_cut_override=te_cut_override)
                gcode_str, warnings = cam.generate_gcode(res, params)

                y_global = y_local + params['joint_length']
                filename = f"CarbonRib_{cconf['loc'].capitalize()}_{cconf['pos'].capitalize()}_Y{y_global:.1f}.gcode"
                filepath = os.path.join(dir_path, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(gcode_str)

                if warnings:
                    all_warnings.extend([f"CarbonRib {cconf['loc']}_{cconf['pos']}: {w}" for w in warnings])
                exported_count += 1
                
            # 3. Export Jigs G-code
            jig_str = self.pm.vars.get('jig_y_positions').get() if 'jig_y_positions' in self.pm.vars else ''
            if jig_str:
                jigs = [float(v.strip()) for v in jig_str.split(',') if v.strip()]
                for j_idx, jy in enumerate(jigs):
                    key = f"jig_{j_idx}"
                    if key in cnc_selections and not cnc_selections[key]:
                        continue
                        
                    # Generate Jig
                    from core.jig_generator import JigGenerator
                    jg = JigGenerator(self.engine, params)
                    jig_poly = jg.generate_jig_for_y(jy)
                    if jig_poly is None or len(jig_poly) == 0:
                        all_warnings.append(f"Jig {j_idx}: Failed to generate geometry")
                        continue
                        
                    # Create a dummy RibResult to pass to cam_engine
                    from core.engine import RibResult
                    dummy_res = RibResult(poly_rot=jig_poly, idx=-1, is_carbon=False, 
                                          te_part_coords=np.array([]), plank_poly_rot=np.array([]), 
                                          c_m=np.array([0,0]), c_b1=np.array([0,0]), c_b2=np.array([0,0]), 
                                          t_holes=[], xb_act=[], xb_skip=[], xb_c_act=[], 
                                          te_cap_pts=[], rc_cap_pts=[[],[]])
                    
                    # Override thick for Jig? Use cam_mat_thick or something? It's 2D cutting anyway
                    gcode_str, warnings = cam.generate_gcode(dummy_res, params, is_jig=True)

                    filename = f"Jig_{j_idx:02d}_Y{jy:.1f}.gcode"
                    filepath = os.path.join(dir_path, filename)

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(gcode_str)

                    if warnings:
                        all_warnings.extend([f"Jig {j_idx}: {w}" for w in warnings])
                    exported_count += 1
"""

content = content.replace(old_export, new_export)

with open('ui/batch_mode.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched ui/batch_mode.py")

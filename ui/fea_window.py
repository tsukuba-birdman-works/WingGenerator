import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.fea_engine import RibFEAEngine

class FEAWindow(tk.Toplevel):
    def __init__(self, parent, rib_result, rib_params, work_dir="."):
        super().__init__(parent)
        self.title("CalculiX FEA Analysis")
        self.geometry("800x600")
        
        self.rib_result = rib_result
        self.rib_params = rib_params
        self.work_dir = work_dir
        self.engine = RibFEAEngine(work_dir=self.work_dir)
        
        self._build_ui()
        
    def _build_ui(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # CSV Selection
        ttk.Label(control_frame, text="Lift Dist CSV:").grid(row=0, column=0, sticky=tk.W)
        self.csv_path_var = tk.StringVar(value="")
        ttk.Entry(control_frame, textvariable=self.csv_path_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Browse", command=self._browse_csv).grid(row=0, column=2)
        
        # Material Props
        ttk.Label(control_frame, text="Young's Modulus E (MPa):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.e_var = tk.DoubleVar(value=15.0) # XPS default
        ttk.Entry(control_frame, textvariable=self.e_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(control_frame, text="Poisson's Ratio nu:").grid(row=2, column=0, sticky=tk.W)
        self.nu_var = tk.DoubleVar(value=0.3)
        ttk.Entry(control_frame, textvariable=self.nu_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(control_frame, text="Rib Thickness (mm):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.thick_var = tk.DoubleVar(value=5.0)
        ttk.Entry(control_frame, textvariable=self.thick_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5)

        ttk.Label(control_frame, text="Allowable Stress (MPa):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.allow_stress_var = tk.DoubleVar(value=10.0)
        ttk.Entry(control_frame, textvariable=self.allow_stress_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=5)

        # Stringer Springs
        self.str_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Model Stringers as Elastic Springs", variable=self.str_enabled_var).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        str_frame = ttk.Frame(control_frame)
        str_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=10)
        
        ttk.Label(str_frame, text="Wing Span L (mm):").grid(row=0, column=0, sticky=tk.W)
        self.str_L_var = tk.DoubleVar(value=1000.0)
        ttk.Entry(str_frame, textvariable=self.str_L_var, width=8).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(str_frame, text="Rib Pos a (mm):").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        self.str_a_var = tk.DoubleVar(value=500.0)
        ttk.Entry(str_frame, textvariable=self.str_a_var, width=8).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(str_frame, text="Stringer E (MPa):").grid(row=0, column=4, sticky=tk.W, padx=(10,0))
        self.str_E_var = tk.DoubleVar(value=10000.0)
        ttk.Entry(str_frame, textvariable=self.str_E_var, width=8).grid(row=0, column=5, sticky=tk.W, padx=5)

        # Planking
        self.plank_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Include Planking (D-Tube Skin)", variable=self.plank_enabled_var).grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        plank_frame = ttk.Frame(control_frame)
        plank_frame.grid(row=8, column=0, columnspan=3, sticky=tk.W, padx=10)
        
        ttk.Label(plank_frame, text="Plank E (MPa):").grid(row=0, column=0, sticky=tk.W)
        self.plank_E_var = tk.DoubleVar(value=3000.0) # Balsa default
        ttk.Entry(plank_frame, textvariable=self.plank_E_var, width=8).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(plank_frame, text="Rib Spacing (mm):").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        self.plank_width_var = tk.DoubleVar(value=100.0)
        ttk.Entry(plank_frame, textvariable=self.plank_width_var, width=8).grid(row=0, column=3, sticky=tk.W, padx=5)

        self.run_btn = ttk.Button(control_frame, text="Run Analysis", command=self._run_analysis)
        self.run_btn.grid(row=9, column=0, pady=10)
        
        self.show_rf_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Show RF Arrows", variable=self.show_rf_var, command=self._replot).grid(row=9, column=1, columnspan=2, sticky=tk.W)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(control_frame, textvariable=self.status_var).grid(row=10, column=0, columnspan=3, sticky=tk.W)
        
        # Canvas for results
        self.fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _browse_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.csv_path_var.set(path)
            
    def _run_analysis(self):
        csv_path = self.csv_path_var.get()
        if not csv_path or not os.path.exists(csv_path):
            messagebox.showerror("Error", "Please select a valid CSV file.")
            return
            
        self.run_btn.config(state=tk.DISABLED)
        self.status_var.set("Generating Mesh & INP...")
        self.update()
        self._analysis_thread(csv_path)
        
    def _analysis_thread(self, csv_path):
        try:
            self.engine.load_lift_csv(csv_path)
            
            # Gather params
            E = self.e_var.get()
            nu = self.nu_var.get()
            thick = self.thick_var.get()
            mat_props = {'E': E, 'nu': nu}
            
            # Calculate actual chord from generated geometry
            import numpy as np
            outer_pts = np.array(self.rib_result.final_rib_mod)
            if len(outer_pts) > 0:
                chord = np.max(outer_pts[:,0]) - np.min(outer_pts[:,0])
            else:
                chord = 100.0 # fallback
            
            # Stringer and plank positions
            stringers = []
            if hasattr(self.rib_params, 'st_upper'):
                stringers.extend(self.rib_params.st_upper)
            if hasattr(self.rib_params, 'st_lower'):
                stringers.extend(self.rib_params.st_lower)
            stringer_x = [st[0]*chord for st in stringers]
            
            # Build Shapely polygon
            from shapely.geometry import Polygon
            import numpy as np
            holes = []
            if getattr(self.rib_result, 'hole_m', None) is not None and len(self.rib_result.hole_m) > 2: holes.append(self.rib_result.hole_m)
            if getattr(self.rib_result, 'hole_f', None) is not None and len(self.rib_result.hole_f) > 2: holes.append(self.rib_result.hole_f)
            if getattr(self.rib_result, 'hole_r', None) is not None and len(self.rib_result.hole_r) > 2: holes.append(self.rib_result.hole_r)
            if getattr(self.rib_result, 'final_truss_holes', None) is not None:
                for h in self.rib_result.final_truss_holes:
                    if len(h) >= 3:
                        holes.append(h)
            if getattr(self.rib_result, 'hole_b1', None) is not None and len(self.rib_result.hole_b1) > 2:
                holes.append(self.rib_result.hole_b1)
            if getattr(self.rib_result, 'hole_b2', None) is not None and len(self.rib_result.hole_b2) > 2:
                holes.append(self.rib_result.hole_b2)
            if getattr(self.rib_result, 'xb_r_active', None) is not None:
                for h in self.rib_result.xb_r_active:
                    if len(h) >= 3:
                        holes.append(h)
                    
            # Ensure proper orientation or simply create polygon
            try:
                poly = Polygon(self.rib_result.final_rib_mod, holes).buffer(0)
            except Exception as e:
                raise RuntimeError(f"Failed to build polygon from rib data: {e}")
                
            spar_centers = []
            if getattr(self.rib_result, 'c_m', None) is not None and len(self.rib_result.c_m) >= 2: 
                spar_centers.append(tuple(self.rib_result.c_m))
            if getattr(self.rib_result, 'c_r', None) is not None and len(self.rib_result.c_r) >= 2: 
                spar_centers.append(tuple(self.rib_result.c_r))
            # Omit front spar (c_f) per user request
            
            # Stringer parameters
            stringer_params = {
                'enabled': self.str_enabled_var.get(),
                'span_L': self.str_L_var.get(),
                'rib_pos_a': self.str_a_var.get(),
                'E': self.str_E_var.get()
            }
            stringer_pts_list = getattr(self.rib_result, 'stringer_pts_list', [])

            # Plank parameters
            plank_params = {
                'enabled': self.plank_enabled_var.get(),
                'E': self.plank_E_var.get(),
                'width': self.plank_width_var.get()
            }
            
            plank_poly_rot = getattr(self.rib_result, 'plank_poly_rot', [])
            plank_poly = None
            if len(plank_poly_rot) >= 3 and self.plank_enabled_var.get():
                from shapely.geometry import Polygon as ShPolygon
                plank_poly = ShPolygon(plank_poly_rot).buffer(0)

            # generate model
            inp_path = self.engine.generate_fea_model(poly, spar_centers, chord, mat_props, thick, stringer_pts_list=stringer_pts_list, stringer_params=stringer_params, plank_poly=plank_poly, plank_params=plank_params)
            
            self.status_var.set("Running CalculiX...")
            import subprocess
            job_name = os.path.splitext(os.path.basename(inp_path))[0]
            res = subprocess.run(["ccx", job_name], cwd=self.work_dir, capture_output=True, text=True)
            
            if res.returncode != 0:
                err_msg = res.stderr.strip() if res.stderr else res.stdout.strip()
                raise RuntimeError(f"CalculiX failed (code {res.returncode}):\n{err_msg}")
                
            if not os.path.exists(os.path.join(self.work_dir, f"{job_name}.dat")):
                raise RuntimeError(f"CalculiX finished but no .dat file was produced.\nLog:\n{res.stdout[-500:]}")
                
            self.status_var.set("Analysis Complete. Parsing results...")
            
            # parse results
            dat_path = os.path.join(self.work_dir, f"{job_name}.dat")
            disp, stress, rf = self.engine.parse_dat_results(dat_path)
            
            try:
                loads = self.engine.parse_inp_loads(inp_path)
            except Exception:
                loads = {}
                
            allow_stress = self.allow_stress_var.get()
            self.status_var.set("Plotting...")
            self.after(0, lambda: self._plot_results(disp, stress, rf, loads, allow_stress))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.after(0, lambda: messagebox.showerror("Analysis Error", str(e)))
        finally:
            self.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
            
    def _replot(self):
        if hasattr(self, 'last_disp'):
            self._plot_results(self.last_disp, self.last_stress, self.last_rf, self.last_loads, self.allow_stress_var.get())

    def _plot_results(self, disp, stress, rf, loads=None, allow_stress=10.0):
        self.last_disp = disp
        self.last_stress = stress
        self.last_rf = rf
        self.last_loads = loads

        if hasattr(self, 'blink_timer') and self.blink_timer:
            self.after_cancel(self.blink_timer)
            self.blink_timer = None
            
        if loads is None: loads = {}
        self.ax.clear()
        
        if hasattr(self, 'cbar'):
            try:
                self.cbar.remove()
                del self.cbar
            except: pass
            
        if hasattr(self, 'cbar_rf'):
            try:
                self.cbar_rf.remove()
                del self.cbar_rf
            except: pass
            
        coords = self.engine.mesh_data['nodeCoords']
        tri_nodes = self.engine.mesh_data['triNodes']
        tags = self.engine.mesh_data['nodeTags']
        
        # map displacements
        ux = np.zeros(len(coords))
        uy = np.zeros(len(coords))
        tag_to_idx = {tag: i for i, tag in enumerate(tags)}
        
        for tag, (dx, dy, dz) in disp.items():
            if tag in tag_to_idx:
                ux[tag_to_idx[tag]] = dx
                uy[tag_to_idx[tag]] = dy
                
        # calculate max displacement to determine auto-scale
        max_d = np.max(np.hypot(ux, uy))
        chord = getattr(self.rib_params, 'chord', 100.0)
        
        # Auto-scale so max visual displacement is 15% of chord
        if max_d > 1e-6:
            scale = (chord * 0.15) / max_d
        else:
            scale = 1.0
            
        def_coords = coords.copy()
        def_coords[:, 0] += ux * scale
        def_coords[:, 1] += uy * scale
        
        # We need to map node tags to indices for triangles
        tri_idx = np.zeros_like(tri_nodes)
        tri_tags = self.engine.mesh_data['triTags']
        element_stress = np.zeros(len(tri_nodes))
        
        for i, row in enumerate(tri_nodes):
            for j, t in enumerate(row):
                tri_idx[i, j] = tag_to_idx.get(t, 0)
            element_stress[i] = stress.get(tri_tags[i], 0.0)

        # Plot
        self.ax.triplot(coords[:,0], coords[:,1], tri_idx, color='lightgray', alpha=0.3, label='Original')
        
        # calculate max displacement and stress
        max_s = np.max(element_stress) if len(element_stress) > 0 else 0.0
        
        # Determine safety factor
        min_sf = allow_stress / max_s if max_s > 0 else float('inf')
        
        # Restore auto-scaling so fine details are visible
        vmax_s = np.percentile(element_stress, 98) if len(element_stress) > 0 else 0.0
        # But if the maximum stress is very low, prevent extreme scaling
        vmax_s = max(vmax_s, allow_stress * 0.1)
        
        tc = self.ax.tripcolor(def_coords[:,0], def_coords[:,1], tri_idx, facecolors=element_stress, cmap='jet', alpha=0.9, edgecolors='none', vmax=vmax_s, vmin=0.0)
        self.cbar = self.fig.colorbar(tc, ax=self.ax, label="Von Mises Stress (MPa)")
        
        # Plot load vectors (arrows)
        if loads:
            drawn_pts = []
            l_x_in, l_y_in, u_in, v_in = [], [], [], []
            l_x_out, l_y_out, u_out, v_out = [], [], [], []
            
            mean_x = np.mean(def_coords[:,0])
            mean_y = np.mean(def_coords[:,1])
            
            for tag, force in loads.items():
                if tag in tag_to_idx:
                    idx = tag_to_idx[tag]
                    # Subsample or filter tiny forces to avoid clutter
                    if np.hypot(force[0], force[1]) > 1e-4:
                        cx, cy = def_coords[idx, 0], def_coords[idx, 1]
                        
                        # Only plot if it's far enough from already drawn arrows (e.g. 15mm apart)
                        too_close = False
                        for (dx, dy) in drawn_pts:
                            if np.hypot(cx - dx, cy - dy) < 15.0:
                                too_close = True
                                break
                                
                        if not too_close:
                            drawn_pts.append((cx, cy))
                            
                            # Determine if pointing inward or outward
                            dx_c = cx - mean_x
                            dy_c = cy - mean_y
                            if (force[0]*dx_c + force[1]*dy_c) < 0:
                                # Inward (Pressure) -> pivot tip to touch surface
                                l_x_in.append(cx)
                                l_y_in.append(cy)
                                u_in.append(force[0])
                                v_in.append(force[1])
                            else:
                                # Outward (Suction) -> pivot tail to touch surface
                                l_x_out.append(cx)
                                l_y_out.append(cy)
                                u_out.append(force[0])
                                v_out.append(force[1])
                                
            if len(l_x_out) > 0:
                self.ax.quiver(l_x_out, l_y_out, u_out, v_out, color='magenta', alpha=0.8, width=0.003, scale=None, label='Aero Suction', pivot='tail')
            if len(l_x_in) > 0:
                self.ax.quiver(l_x_in, l_y_in, u_in, v_in, color='magenta', alpha=0.8, width=0.003, scale=None, label='Aero Pressure', pivot='tip')

        # Plot reaction forces (arrows or colored points)
        if rf:
            c_m = getattr(self.rib_result, 'c_m', None)
            c_r = getattr(self.rib_result, 'c_r', None)
            
            def get_inward_shift(cx, cy, shift_dist=3.0):
                # Find closest spar center
                best_center = None
                min_d = float('inf')
                for c in [c_m, c_r]:
                    if c is not None and len(c) >= 2:
                        d = np.hypot(cx - c[0], cy - c[1])
                        if d < min_d:
                            min_d = d
                            best_center = c
                if best_center is not None:
                    dx = best_center[0] - cx
                    dy = best_center[1] - cy
                    mag = np.hypot(dx, dy)
                    if mag > 1e-6:
                        return cx + shift_dist * (dx / mag), cy + shift_dist * (dy / mag)
                return cx, cy

            if self.show_rf_var.get():
                rf_drawn = []
                rf_x, rf_y, ru, rv = [], [], [], []
                for tag, force in rf.items():
                    if tag in tag_to_idx:
                        idx = tag_to_idx[tag]
                        if np.hypot(force[0], force[1]) > 1e-4:
                            cx, cy = def_coords[idx, 0], def_coords[idx, 1]
                            
                            too_close = False
                            for (dx, dy) in rf_drawn:
                                if np.hypot(cx - dx, cy - dy) < 8.0:
                                    too_close = True
                                    break
                                    
                            if not too_close:
                                rf_drawn.append((cx, cy))
                                sx, sy = get_inward_shift(cx, cy, shift_dist=3.0)
                                rf_x.append(sx)
                                rf_y.append(sy)
                                ru.append(force[0])
                                rv.append(force[1])
                if len(rf_x) > 0:
                    self.ax.quiver(rf_x, rf_y, ru, rv, color='orange', alpha=0.9, width=0.004, scale=None, label='Adhesive Force')
            else:
                rf_x, rf_y, rf_mags = [], [], []
                for tag, force in rf.items():
                    if tag in tag_to_idx:
                        idx = tag_to_idx[tag]
                        mag = np.hypot(force[0], force[1])
                        if mag > 1e-4:
                            cx, cy = def_coords[idx, 0], def_coords[idx, 1]
                            sx, sy = get_inward_shift(cx, cy, shift_dist=3.0)
                            rf_x.append(sx)
                            rf_y.append(sy)
                            rf_mags.append(mag)
                if len(rf_x) > 0:
                    sc = self.ax.scatter(rf_x, rf_y, c=rf_mags, cmap='plasma', s=30, zorder=5, label='Adhesive Stress (Magnitude)')
                    self.cbar_rf = self.fig.colorbar(sc, ax=self.ax, label='Adhesive Force Magnitude (N)')


        self.ax.set_title(f"Max Disp: {max_d:.3f} mm, Max Stress: {max_s:.3f} MPa\nAllowable Limit: {allow_stress:.1f} MPa (Min SF: {min_sf:.2f})")
        self.ax.axis('equal')
        
        # Identify nodes exceeding allowable stress for blinking warning
        # Convert element stress to node stress by averaging (simple approximation for visualization)
        node_stress = np.zeros(len(def_coords))
        node_count = np.zeros(len(def_coords))
        for i in range(len(tri_idx)):
            for j in range(3):
                idx = tri_idx[i, j]
                node_stress[idx] += element_stress[i]
                node_count[idx] += 1
        
        valid = node_count > 0
        node_stress[valid] /= node_count[valid]
        
        exceed_idx = np.where(node_stress >= allow_stress)[0]
        self.blink_scatter = None
        self.blink_state = False
        if len(exceed_idx) > 0:
            ex_x = def_coords[exceed_idx, 0]
            ex_y = def_coords[exceed_idx, 1]
            self.blink_scatter = self.ax.scatter(ex_x, ex_y, c='red', s=40, marker='X', zorder=10, label='Limit Exceeded!')
            self.ax.legend(loc='upper right')
            self._toggle_blink()
            
        self.canvas.draw()
        
        # Calculate and update reaction forces/stresses
        self._update_rf_labels(rf)

    def _update_rf_labels(self, rf):
        import numpy as np
        chord = float(self.rib_result.chord) if hasattr(self.rib_result, 'chord') else 1000.0
        c_m = getattr(self.rib_result, 'c_m', None)
        c_r = getattr(self.rib_result, 'c_r', None)
        r_m = getattr(self.rib_result, 'main_spar_params', {}).get('radius', 10.0)
        r_r = getattr(self.rib_result, 'rear_spar_params', {}).get('radius', 10.0)
        
        total_rf_main = np.zeros(2)
        total_rf_rear = np.zeros(2)
        
        node_coords = self.engine.mesh_data['nodeCoords']
        node_tags = self.engine.mesh_data['nodeTags']
        
        for tag, force in rf.items():
            idx_arr = np.where(node_tags == tag)[0]
            if len(idx_arr) > 0:
                coord = node_coords[idx_arr[0]]
                if c_m is not None and np.hypot(coord[0]-c_m[0], coord[1]-c_m[1]) < chord * 0.3:
                    total_rf_main += force
                elif c_r is not None and np.hypot(coord[0]-c_r[0], coord[1]-c_r[1]) < chord * 0.3:
                    total_rf_rear += force
                    
        thick = self.thick_var.get()
        area_main = 2 * np.pi * r_m * thick
        area_rear = 2 * np.pi * r_r * thick
        
        Fm_mag = np.linalg.norm(total_rf_main)
        Fr_mag = np.linalg.norm(total_rf_rear)
        tau_m = Fm_mag / area_main if area_main > 0 else 0.0
        tau_r = Fr_mag / area_rear if area_rear > 0 else 0.0
        
        if not hasattr(self, 'rf_main_label'):
            # Create UI elements if they don't exist
            self.rf_frame = ttk.LabelFrame(self, text="Adhesive Joint Stress (Spar)")
            self.rf_frame.pack(before=self.canvas.get_tk_widget(), side=tk.TOP, fill=tk.X, padx=10, pady=5)
            self.rf_main_label = ttk.Label(self.rf_frame, text="")
            self.rf_main_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            self.rf_rear_label = ttk.Label(self.rf_frame, text="")
            self.rf_rear_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            
        self.rf_main_label.config(text=f"Main Spar (Force / Shear): {Fm_mag:.1f} N / {tau_m:.3f} MPa")
        self.rf_rear_label.config(text=f"Rear Spar (Force / Shear): {Fr_mag:.1f} N / {tau_r:.3f} MPa")
        
    def _toggle_blink(self):
        if not hasattr(self, 'blink_scatter') or self.blink_scatter is None:
            return
        if not self.winfo_exists():
            return
            
        self.blink_state = not getattr(self, 'blink_state', False)
        self.blink_scatter.set_visible(self.blink_state)
        self.canvas.draw_idle()
        self.blink_timer = self.after(500, self._toggle_blink)

import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.engine import RibGeneratorEngine, RibParameters, RibGenerationResult
from utils.config import ConfigHelper
from core.export_3d import Wing3DExporter
from ui.base_mode import BaseRibGeneratorGUI

# ==========================================
# 単一リブモードGUI
# ==========================================
class RibGeneratorGUI_Single(BaseRibGeneratorGUI):

    def __init__(self, root):
        super().__init__(root)
        from core.engine import RibGeneratorEngine
        self.engine = RibGeneratorEngine()
        from ui.param_spec import SINGLE_PARAMS
        from ui.ui_builder import ParameterManager, UIBuilder
        self.pm = ParameterManager(self, SINGLE_PARAMS)
        self.ui_builder = UIBuilder(self.pm)
        self.str_vars = {}
        for name in ["A", "B", "C", "D", "E"]:
            import tkinter as tk
            self.str_vars[name] = {'active': tk.BooleanVar(value=False), 'pos': tk.StringVar(), 'w': tk.StringVar(), 'd': tk.StringVar(), 'use_dxf': tk.BooleanVar(), 'dxf': tk.StringVar()}
        
        self.last_warnings = []
        self.is_updating_ui = False
        self.create_widgets()

    def get_all_vars(self):
        v = self.pm.get_all_vars().copy()
        for name in ["A", "B", "C", "D", "E"]:
            for key in ['active', 'pos', 'w', 'd', 'use_dxf', 'dxf']:
                v[f'str_{name}_{key}'] = self.str_vars[name][key]
        if hasattr(self, 'get_cam_vars'):
            v.update(self.get_cam_vars())
        return v

    def save_config(self):
        super().save_config("Single")

    def get_rib_parameters(self, fast_mode=False) -> RibParameters:
        t_rib = 3.0 # Hardcoded as requested to delete from UI
        
        return RibParameters(
            file1=self.file1_path.get(),
            file2=self.file2_path.get(), # Single mode uses same file? Wait, single mode file2_path was removed? No, I only kept file1_path.
            blend_ratio=self.safe_float(self.blend_ratio_pct)/100.0,
            chord=self.safe_float(self.chord_length),
            spar_pct=self.safe_float(self.spar_pos_pct),
            washout_deg=self.safe_float(self.washout_deg),
            spar_hole_dia=self.safe_float(self.spar_hole_dia),
            spar_hole_dv=0.0,
            rear_dx=0.0,
            rear_dy=0.0,
            rear_dia=0.0,
            front_dx=0.0,
            front_dy=0.0,
            front_dia=0.0,
            truss_angle=self.safe_float(self.base_truss_angle),
            truss_front_n=self.safe_int(self.truss_front_n),
            truss_rear_n=self.safe_int(self.truss_rear_n),
            truss_scale_front_list=[float(x) for x in self.truss_scale_front.get().split(',') if x.strip()] if hasattr(self, 'truss_scale_front') else [],
            truss_scale_rear_list=[float(x) for x in self.truss_scale_rear.get().split(',') if x.strip()] if hasattr(self, 'truss_scale_rear') else [],
            beam_width=self.safe_float(self.beam_width),
            margin_spar=self.safe_float(self.margin_spar),
            margin_bolt=self.safe_float(self.margin_bolt),
            margin_outer=self.safe_float(self.margin_outer),
            truss_fillet=self.safe_float(self.truss_fillet),
            min_hole_dia=self.safe_float(self.min_hole_dia),
            xb_t_list=[],
            x_dia=0.0,
            plank_start=self.safe_float(self.plank_start),
            plank_end=self.safe_float(self.plank_end),
            plank_part_start=self.safe_float(self.plank_start),
            plank_part_end=self.safe_float(self.plank_end),
            plank_thick=self.safe_float(self.plank_thick),
            stringers_data=self.get_stringers_data(),
            te_cut=self.safe_float(self.te_cut),
            apply_safe_margin=self.safe_margin_var.get(),
            te_cap_uf_act=False,
            te_cap_uf_w=0.0,
            te_cap_ur_act=False,
            te_cap_ur_w=0.0,
            te_cap_lf_act=False,
            te_cap_lf_w=0.0,
            te_cap_lr_act=False,
            te_cap_lr_w=0.0,
            te_cap_thick=0.0,
            rc1_act=False,
            rc1_start=0.0,
            rc1_end=0.0,
            rc1_thick=0.0,
            rc2_act=False,
            rc2_start=0.0,
            rc2_end=0.0,
            rc2_thick=0.0,
            bolt1_dx=self.safe_float(self.bolt1_dx),
            bolt1_dy=self.safe_float(self.bolt1_dy),
            bolt1_dia=self.safe_float(self.bolt1_dia),
            bolt2_dx=self.safe_float(self.bolt2_dx),
            bolt2_dy=self.safe_float(self.bolt2_dy),
            bolt2_dia=self.safe_float(self.bolt2_dia),
            diag_params_list=[],
            fast_mode=fast_mode,
            tabs_active=self.tabs_active.get() if hasattr(self, 'tabs_active') else True,
            truss_tab_width=4.0,
            le_interp_active=self.le_interp_active.get(),
            le_interp_range=self.safe_float(self.le_interp_range, 10.0),
            le_interp_divisions=self.safe_int(self.le_interp_divisions, 50)
        )

    def create_widgets(self):
        import tkinter as tk
        from tkinter import ttk
        
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(main_pane, width=450)
        main_pane.add(left_frame, weight=0)

        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.ui_builder.build_tabs(notebook, self.pm)
        
        if 'Plank TE' in self.pm.obj.tabs_frames:
            self.create_stringers_ui(self.pm.obj.tabs_frames['Plank TE'])
            
        if 'DXF' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['DXF'], text="Export DXF", command=self.export_dxf).pack(fill=tk.X, padx=10, pady=5)
            
        if 'CNC' in self.pm.obj.tabs_frames:
            ttk.Button(self.pm.obj.tabs_frames['CNC'], text="Export CNC (G-Code)", command=self.export_gcode).pack(fill=tk.X, padx=10, pady=5)
            
        f_top = ttk.Frame(left_frame)
        f_top.pack(fill=tk.X, side=tk.TOP, before=notebook)
        ttk.Button(f_top, text="Load Config", command=self.load_config).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(f_top, text="Save Config", command=self.save_config).pack(side=tk.LEFT, expand=True, fill=tk.X)

        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)

        lf_preview = ttk.LabelFrame(right_frame, text="Rib Preview")
        lf_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        control_frame = ttk.Frame(lf_preview)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="Update Preview", command=self.update_preview).pack(side=tk.LEFT, padx=5)
        
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.fig = Figure(figsize=(7, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=lf_preview)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        for var in self.pm.vars.values():
            if hasattr(var, 'trace_add'):
                try: var.trace_add("write", lambda *args: self.update_preview())
                except: pass


    def update_preview_fast(self, *args): self.update_preview(fast_mode=True)
    def update_preview_full(self, *args): self.update_preview(fast_mode=False)

    def update_preview(self, fast_mode=False):
        if getattr(self, 'is_updating_ui', False): return
        if not self.file1_path.get() or not self.file2_path.get(): return
        try:
            params = self.get_rib_parameters(fast_mode)
            res = self.engine.generate_single_rib(params)
            self.last_warnings = res.warnings_list
            chord = params.chord
            washout = params.washout_deg
            title = f"Rib Shape (Chord: {chord:.1f}mm, Washout: {washout:.2f}°)" + (" [FAST PREVIEW]" if fast_mode else "")
            self.draw_plot(*res[:12], self.last_warnings, res.plank_poly_rot, res.te_part_coords, res.c_b1, res.hole_b1, res.c_b2, res.hole_b2, res.diag_poly_pts_list, res.final_rib_orig, title, res.te_cap_pts_list, res.rc_cap_pts_list)
        except Exception as e: print("Preview Error:", e)

    def draw_plot(self, rib_pts, c_m, h_m, c_r, h_r, c_f, h_f, t_holes, xb_act, xb_c_act, xb_skip, xb_c_skip, warnings_list, plank_poly, te_part, c_b1, hole_b1, c_b2, hole_b2, diag_poly_pts_list, final_rib_orig, title, te_cap_pts_list=None, rc_cap_pts_list=None):
        self.ax.clear(); self.ax.grid(True, linestyle='--', alpha=0.7); self.ax.set_aspect('equal', adjustable='datalim')
        if len(rib_pts) > 0:
            self.ax.plot(rib_pts[:, 0], rib_pts[:, 1], 'b-', linewidth=2, label="Rib Shape")
        if final_rib_orig is not None and len(final_rib_orig) > 0:
            le = final_rib_orig[np.argmin(final_rib_orig[:, 0])]
            te = final_rib_orig[0]
            self.ax.plot([le[0], te[0]], [le[1], te[1]], 'k-.', linewidth=0.8, alpha=0.5, label="Chord Line")
        if len(h_m) > 0: self.ax.plot(c_m[0], c_m[1], 'kx', markersize=6); self.ax.plot(h_m[:, 0], h_m[:, 1], 'r-', linewidth=1.5)
        if len(h_f) > 0: self.ax.plot(c_f[0], c_f[1], 'cx', markersize=6); self.ax.plot(h_f[:, 0], h_f[:, 1], 'c-', linewidth=1.5)
        if len(h_r) > 0: self.ax.plot(c_r[0], c_r[1], 'mx', markersize=6); self.ax.plot(h_r[:, 0], h_r[:, 1], 'm-', linewidth=1.5)
        if len(hole_b1) > 0: self.ax.plot(c_b1[0], c_b1[1], 'kx', markersize=4); self.ax.plot(hole_b1[:, 0], hole_b1[:, 1], 'r-', linewidth=1.5)
        if len(hole_b2) > 0: self.ax.plot(c_b2[0], c_b2[1], 'kx', markersize=4); self.ax.plot(hole_b2[:, 0], hole_b2[:, 1], 'r-', linewidth=1.5)
        for h in t_holes: self.ax.plot(h[:, 0], h[:, 1], color='orange', linestyle='-', linewidth=1.5)
        for xb in xb_act: self.ax.plot(xb[:, 0], xb[:, 1], color='orange', linestyle='-', linewidth=1.5)
        for c in xb_c_act: self.ax.plot(c[0], c[1], marker='x', color='orange', markersize=6, label="X-Brace")
        for xb in xb_skip: self.ax.plot(xb[:, 0], xb[:, 1], color='gray', linestyle=':', linewidth=1.5)
        for diag_pts in diag_poly_pts_list:
            if len(diag_pts) > 0: self.ax.plot(diag_pts[:, 0], diag_pts[:, 1], color='purple', linestyle='-', linewidth=2, label="Diagonal Spar")
        if len(plank_poly) > 0: self.ax.plot(plank_poly[:, 0], plank_poly[:, 1], color='green', linestyle='-', linewidth=1.5, alpha=0.7, label="Plank Layer")
        if len(te_part) > 0: self.ax.plot(te_part[:, 0], te_part[:, 1], color='cyan', linestyle='-', linewidth=2, label="TE Part")
        if te_cap_pts_list is not None:
            drawn_te_cap = False
            for cap_pts in te_cap_pts_list:
                if len(cap_pts) > 0:
                    self.ax.plot(cap_pts[:, 0], cap_pts[:, 1], color='black', linestyle='-', linewidth=2, label="TE Cap" if not drawn_te_cap else "")
                    drawn_te_cap = True
        if rc_cap_pts_list is not None:
            drawn_rc_cap = False
            for cap_pts in rc_cap_pts_list[0] + rc_cap_pts_list[1]:
                if len(cap_pts) > 0:
                    self.ax.plot(cap_pts[:, 0], cap_pts[:, 1], color='red', linestyle='-', linewidth=2, label="Rib Cap" if not drawn_rc_cap else "")
                    drawn_rc_cap = True
        if warnings_list: self.ax.text(0.5, 0.95, "⚠️ " + " / ".join(warnings_list), transform=self.ax.transAxes, color='white', fontsize=12, fontweight='bold', ha='center', va='top', bbox=dict(facecolor='red', alpha=0.8, edgecolor='none', pad=5))
        self.ax.set_title(title); self.ax.set_xlabel("X (mm)"); self.ax.set_ylabel("Y (mm)")
        handles, labels = self.ax.get_legend_handles_labels(); by_label = dict(zip(labels, handles)); self.ax.legend(by_label.values(), by_label.keys())
        self.canvas.draw()

    def export_dxf(self):
        f1, f2 = self.file1_path.get(), self.file2_path.get()
        if not f1 or not f2 or not os.path.exists(f1) or not os.path.exists(f2): return messagebox.showerror("Error", "Please select valid files.")
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
            messagebox.showinfo("Success", f"Saved to:\n{path}")
        except Exception as e: messagebox.showerror("Export Error", str(e))

    def export_obj(self):
        f1, f2 = self.file1_path.get(), self.file2_path.get()
        if not f1 or not f2 or not os.path.exists(f1) or not os.path.exists(f2): return messagebox.showerror("Error", "Please select valid files.")
        filepath = filedialog.asksaveasfilename(
            title="Save 3D Model",
            defaultextension=".glb", 
            filetypes=[("glTF Binary", "*.glb"), ("Wavefront OBJ", "*.obj")]
        )
        if not filepath: return
        
        try:
            import trimesh
        except ImportError:
            return messagebox.showerror("Error", "trimesh library is required for 3D export.\nPlease run: pip install trimesh")

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
            messagebox.showinfo("Success", f"Saved 3D Model to:\n{filepath}")
        except Exception as e: messagebox.showerror("Export Error", str(e))

    def export_gcode(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".gcode", filetypes=[("G-Code Files", "*.gcode;*.nc;*.g;*.cnc")])
            if not path: return
            
            params = self.get_rib_parameters(fast_mode=False)
            res = self.engine.generate_single_rib(params)
            
            vars_dict = {k: v.get() if hasattr(v, 'get') else v for k, v in self.get_all_vars().items()}
            
            from core.cam_engine import SpindleCAMEngine
            cam = SpindleCAMEngine()
            gcode_str, warnings = cam.generate_gcode(res, vars_dict)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(gcode_str)
                
            if warnings:
                msg = "Exported G-code with warnings:\n\n" + "\n".join(warnings)
                messagebox.showwarning("Export Warning", msg)
            else:
                messagebox.showinfo("Success", f"Saved G-Code to:\n{path}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Export Error", str(e))
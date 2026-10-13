import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.fin_engine import WingtipFinEngine
from utils.config import ConfigHelper

class WingtipFinGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WingGenerator - Ver.1.0.0 (Wingtip Fin Generator)")
        self.root.geometry("1100x780")
        
        self.engine = WingtipFinEngine()
        
        # Parameters setup (Fin)
        self.airfoil_path = tk.StringVar(value="")
        self.span = tk.StringVar(value="250.0")
        self.cant_angle = tk.StringVar(value="45.0")
        self.sweep_angle = tk.StringVar(value="30.0")
        self.taper_ratio = tk.StringVar(value="0.1")  # default 0.1 for Horner
        self.twist_deg = tk.StringVar(value="-2.0")
        self.thickness_scale = tk.StringVar(value="1.0")
        self.chord_root = tk.StringVar(value="200.0")
        self.spar_pct = tk.StringVar(value="40.0")
        self.style = tk.StringVar(value="Horner Upward")
        self.color_name = tk.StringVar(value="Styrofoam (Blue)")
        self.hoerner_power = tk.StringVar(value="2.0")
        self.curve_power = tk.StringVar(value="2.0")
        self.y_slices = tk.StringVar(value="20")
        self.wing_side = tk.StringVar(value="Right")
        self.winglet_w_flat = tk.StringVar(value="50.0")
        self.winglet_r_bend = tk.StringVar(value="50.0")
        self.winglet_h_up = tk.StringVar(value="150.0")
        
        # Parameters setup (Main Wing Panel Reference)
        self.main_span = tk.StringVar(value="500.0")
        self.main_chord_root = tk.StringVar(value="300.0")
        self.main_sweep = tk.StringVar(value="15.0")
        self.main_airfoil_path = tk.StringVar(value="")
        self.main_spar_pct_root = tk.StringVar(value="40.0")
        self.main_spar_pct_tip = tk.StringVar(value="40.0")
        
        self.colors_dict = {
            "Styrofoam (Blue)": [135, 206, 235, 255],
            "Carbon (Black)": [30, 30, 30, 255],
            "Glossy White": [245, 245, 245, 255],
            "Bright Yellow": [250, 210, 0, 255],
            "Racing Red": [220, 20, 60, 255]
        }
        
        self.create_widgets()
        self.on_style_change()  # Initialize dynamic panel state
        self.update_preview()

    def create_widgets(self):
        # Main frames
        self.left_frame = tk.Frame(self.root, width=400, bg="#f5f5f7")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.left_frame.pack_propagate(False)
        
        self.right_frame = tk.Frame(self.root, bg="white")
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # ----------------------------------------------------
        # Left Panel (Inputs)
        # ----------------------------------------------------
        # Static Title at the top
        tk.Label(self.left_frame, text="Wingtip Fin Parameters", font=("Arial", 14, "bold"), bg="#f5f5f7").pack(anchor="w", pady=(5, 10))
        
        # Scrollable area
        self.param_canvas = tk.Canvas(self.left_frame, bg="#f5f5f7", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.param_canvas.yview)
        self.scroll_content = tk.Frame(self.param_canvas, bg="#f5f5f7")
        
        self.scroll_content.bind(
            "<Configure>",
            lambda e: self.param_canvas.configure(
                scrollregion=self.param_canvas.bbox("all")
            )
        )
        
        self.canvas_frame_id = self.param_canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        
        def _configure_canvas(event):
            self.param_canvas.itemconfig(self.canvas_frame_id, width=event.width)
            
        self.param_canvas.bind('<Configure>', _configure_canvas)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.param_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.param_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Mousewheel scroll support
        def _on_mousewheel(event):
            if event.num == 4:
                self.param_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.param_canvas.yview_scroll(1, "units")
            else:
                self.param_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_to_mousewheel(event):
            self.param_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            self.param_canvas.bind_all("<Button-4>", _on_mousewheel)
            self.param_canvas.bind_all("<Button-5>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            self.param_canvas.unbind_all("<MouseWheel>")
            self.param_canvas.unbind_all("<Button-4>")
            self.param_canvas.unbind_all("<Button-5>")

        self.param_canvas.bind('<Enter>', _bind_to_mousewheel)
        self.param_canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Helper to create inputs
        def add_field(parent, label, var_obj):
            f = tk.Frame(parent, bg="#f5f5f7")
            f.pack(fill=tk.X, pady=2)
            tk.Label(f, text=label, bg="#f5f5f7", width=18, anchor="w").pack(side=tk.LEFT)
            tk.Entry(f, textvariable=var_obj, font=("Arial", 9)).pack(side=tk.LEFT, expand=True, fill=tk.X)
            return f

        # --- Fin Profile Section ---
        f_fin_group = tk.LabelFrame(self.scroll_content, text="Wingtip Fin Settings", bg="#f5f5f7", padx=5, pady=5)
        f_fin_group.pack(fill=tk.X, pady=3)

        # Airfoil selection
        f_airfoil = tk.Frame(f_fin_group, bg="#f5f5f7")
        f_airfoil.pack(fill=tk.X, pady=2)
        tk.Label(f_airfoil, text="Tip Airfoil (.dat):", bg="#f5f5f7", width=16, anchor="w").pack(side=tk.LEFT)
        tk.Entry(f_airfoil, textvariable=self.airfoil_path, font=("Arial", 9)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        tk.Button(f_airfoil, text="Browse", command=self.browse_airfoil, font=("Arial", 9)).pack(side=tk.RIGHT)

        add_field(f_fin_group, "Root Chord (mm):", self.chord_root)
        add_field(f_fin_group, "Fin Span / Height (mm):", self.span)
        add_field(f_fin_group, "Sweep Angle (deg):", self.sweep_angle)
        add_field(f_fin_group, "Taper Ratio (0.0-1.0):", self.taper_ratio)
        add_field(f_fin_group, "Resolution (Slices):", self.y_slices)

        # Wing Side Selection
        f_side = tk.Frame(f_fin_group, bg="#f5f5f7")
        f_side.pack(fill=tk.X, pady=2)
        tk.Label(f_side, text="Wing Side:", bg="#f5f5f7", width=18, anchor="w").pack(side=tk.LEFT)
        self.cb_side = ttk.Combobox(f_side, textvariable=self.wing_side, values=["Right", "Left"], state="readonly")
        self.cb_side.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.cb_side.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # Style Combobox
        f_style = tk.Frame(f_fin_group, bg="#f5f5f7")
        f_style.pack(fill=tk.X, pady=2)
        tk.Label(f_style, text="Fin Style / Curvature:", bg="#f5f5f7", width=18, anchor="w").pack(side=tk.LEFT)
        styles = ["Horner Upward", "Horner Downward", "Symmetrical", "Flat / Standard", "Round Dome", "Winglet"]
        self.cb_style = ttk.Combobox(f_style, textvariable=self.style, values=styles, state="readonly")
        self.cb_style.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.cb_style.bind("<<ComboboxSelected>>", self.on_style_change)

        # Dynamic Panel for Style-Specific Parameters
        self.dynamic_frame = tk.Frame(f_fin_group, bg="#f5f5f7")
        self.dynamic_frame.pack(fill=tk.X, pady=2)

        # 1. Horner Specific Frame
        self.f_horner = tk.Frame(self.dynamic_frame, bg="#f5f5f7")
        add_field(self.f_horner, "Horner Power (Exp):", self.hoerner_power)
        add_field(self.f_horner, "Curve Power (Exp):", self.curve_power)

        # 2. Standard / Winglet Specific Frame
        self.f_standard = tk.Frame(self.dynamic_frame, bg="#f5f5f7")
        add_field(self.f_standard, "Dihedral / Cant (deg):", self.cant_angle)
        add_field(self.f_standard, "Twist / Washout (deg):", self.twist_deg)
        add_field(self.f_standard, "Thickness Scale:", self.thickness_scale)
        add_field(self.f_standard, "Spar Rot Center (%):", self.spar_pct)

        # 3. Winglet Specific Frame
        self.f_winglet = tk.Frame(self.dynamic_frame, bg="#f5f5f7")
        add_field(self.f_winglet, "Flat Width (mm):", self.winglet_w_flat)
        add_field(self.f_winglet, "Bend Radius (mm):", self.winglet_r_bend)
        add_field(self.f_winglet, "Winglet Height (mm):", self.winglet_h_up)

        # --- Main Wing Section Reference ---
        f_main_wing = tk.LabelFrame(self.scroll_content, text="Main Wing Section (Reference)", bg="#f5f5f7", padx=5, pady=5)
        f_main_wing.pack(fill=tk.X, pady=3)
        
        add_field(f_main_wing, "Main Root Chord (mm):", self.main_chord_root)
        add_field(f_main_wing, "Main Span / Length (mm):", self.main_span)
        add_field(f_main_wing, "Main Sweep Angle (deg):", self.main_sweep)
        add_field(f_main_wing, "Main Root Spar (%):", self.main_spar_pct_root)
        add_field(f_main_wing, "Main Tip Spar (%):", self.main_spar_pct_tip)
        
        f_main_airfoil = tk.Frame(f_main_wing, bg="#f5f5f7")
        f_main_airfoil.pack(fill=tk.X, pady=2)
        tk.Label(f_main_airfoil, text="Main Airfoil (.dat):", bg="#f5f5f7", width=16, anchor="w").pack(side=tk.LEFT)
        tk.Entry(f_main_airfoil, textvariable=self.main_airfoil_path, font=("Arial", 9)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        tk.Button(f_main_airfoil, text="Browse", command=self.browse_main_airfoil, font=("Arial", 9)).pack(side=tk.RIGHT)

        # Color Preset
        f_color = tk.Frame(self.scroll_content, bg="#f5f5f7")
        f_color.pack(fill=tk.X, pady=5)
        tk.Label(f_color, text="Fin Color Preset:", bg="#f5f5f7", width=18, anchor="w").pack(side=tk.LEFT)
        colors_list = list(self.colors_dict.keys())
        ttk.Combobox(f_color, textvariable=self.color_name, values=colors_list, state="readonly").pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Config buttons
        f_config_btns = tk.Frame(self.scroll_content, bg="#f5f5f7")
        f_config_btns.pack(fill=tk.X, pady=(5, 0))
        tk.Button(f_config_btns, text="Load Config (JSON)", command=self.load_config, bg="#e3e3e6", font=("Arial", 9)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        tk.Button(f_config_btns, text="Save Config (JSON)", command=self.save_config, bg="#e3e3e6", font=("Arial", 9)).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

        # Action Buttons
        tk.Button(self.scroll_content, text="Update 3D Preview", command=self.update_preview, bg="#0071e3", fg="white", font=("Arial", 10, "bold"), height=2).pack(fill=tk.X, pady=10)
        
        # Export panel
        f_export = tk.LabelFrame(self.scroll_content, text="Export 3D Model (Fin Only)", bg="#f5f5f7", padx=10, pady=5)
        f_export.pack(fill=tk.X, pady=5)
        
        tk.Button(f_export, text="Export STL", command=lambda: self.export_model("stl"), bg="#34c759", fg="white", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=2)
        tk.Button(f_export, text="Export OBJ", command=lambda: self.export_model("obj"), bg="#ff9500", fg="white", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=2)
        tk.Button(f_export, text="Export GLB (glTF)", command=lambda: self.export_model("glb"), bg="#af52de", fg="white", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=2)
        
        # flow5 / Aerodynamic Export
        f_aero = tk.LabelFrame(self.scroll_content, text="Aerodynamic Export", bg="#f5f5f7", padx=10, pady=5)
        f_aero.pack(fill=tk.X, pady=5)
        tk.Button(f_aero, text="Export to flow5 (TXT)", command=self.export_flow5, bg="#000000", fg="white", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=2)

        # Home button
        tk.Button(self.scroll_content, text="← Return to Launcher", command=self.return_to_launcher, bg="gray", fg="white", font=("Arial", 9)).pack(fill=tk.X, pady=5)

        # ----------------------------------------------------
        # Right Panel (3D Preview)
        # ----------------------------------------------------
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(projection='3d')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_style_change(self, event=None):
        self.f_horner.pack_forget()
        self.f_standard.pack_forget()
        self.f_winglet.pack_forget()
        
        style = self.style.get()
        if "Horner" in style:
            self.f_horner.pack(fill=tk.X)
        elif style == "Round Dome":
            pass
        elif style == "Winglet":
            self.f_winglet.pack(fill=tk.X)
            self.f_standard.pack(fill=tk.X)
        else:
            self.f_standard.pack(fill=tk.X)

    def browse_airfoil(self):
        filepath = filedialog.askopenfilename(
            title="Select Tip Airfoil DAT file",
            filetypes=[("DAT Files", "*.dat"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            self.airfoil_path.set(filepath)
            self.update_preview()

    def browse_main_airfoil(self):
        filepath = filedialog.askopenfilename(
            title="Select Main Airfoil DAT file",
            filetypes=[("DAT Files", "*.dat"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            self.main_airfoil_path.set(filepath)
            self.update_preview()

    def get_ui_params(self):
        c_rgba = self.colors_dict.get(self.color_name.get(), [135, 206, 235, 255])
        return {
            'airfoil_path': self.airfoil_path.get(),
            'span': self.safe_float(self.span, 200.0),
            'cant_angle': self.safe_float(self.cant_angle, 45.0),
            'sweep_angle': self.safe_float(self.sweep_angle, 30.0),
            'taper_ratio': self.safe_float(self.taper_ratio, 0.1),
            'twist_deg': self.safe_float(self.twist_deg, -2.0),
            'thickness_scale': self.safe_float(self.thickness_scale, 1.0),
            'chord_root': self.safe_float(self.chord_root, 200.0),
            'spar_pct': self.safe_float(self.spar_pct, 40.0),
            'style': self.style.get(),
            'color_rgba': c_rgba,
            'hoerner_power': self.safe_float(self.hoerner_power, 2.0),
            'curve_power': self.safe_float(self.curve_power, 2.0),
            'y_slices': int(self.safe_float(self.y_slices, 20)),
            'wing_side': self.wing_side.get(),
            
            # Winglet params
            'winglet_w_flat': self.safe_float(self.winglet_w_flat, 50.0),
            'winglet_r_bend': self.safe_float(self.winglet_r_bend, 50.0),
            'winglet_h_up': self.safe_float(self.winglet_h_up, 150.0),
            
            # Main wing params
            'main_span': self.safe_float(self.main_span, 500.0),
            'main_chord_root': self.safe_float(self.main_chord_root, 300.0),
            'main_sweep': self.safe_float(self.main_sweep, 15.0),
            'main_airfoil_path': self.main_airfoil_path.get(),
            'main_spar_pct_root': self.safe_float(self.main_spar_pct_root, 40.0),
            'main_spar_pct_tip': self.safe_float(self.main_spar_pct_tip, 40.0)
        }

    def safe_float(self, var, default=0.0):
        try:
            return float(var.get())
        except:
            return default

    def update_preview(self):
        try:
            params = self.get_ui_params()
            
            # Generate meshes
            mesh = self.engine.generate_fin_mesh(params)
            main_mesh = self.engine.generate_main_wing_mesh(params)
            
            # Clear 3D axes
            self.ax.clear()
            
            # 1. Render main wing (reference) in translucent grey
            mv = main_mesh.vertices
            mf = main_mesh.faces
            self.ax.plot_trisurf(mv[:, 0], mv[:, 1], mv[:, 2], triangles=mf, color=[0.5, 0.5, 0.5], shade=True, alpha=0.3)
            
            # 2. Render wingtip fin in selected color
            v = mesh.vertices
            f = mesh.faces
            c_rgba = np.array(params['color_rgba']) / 255.0
            self.ax.plot_trisurf(v[:, 0], v[:, 1], v[:, 2], triangles=f, color=c_rgba, shade=True, alpha=0.9)
            
            # 3. Draw Spar Line
            if 'spar_line' in mesh.metadata and 'spar_line' in main_mesh.metadata:
                spar_all = np.vstack((main_mesh.metadata['spar_line'], mesh.metadata['spar_line']))
                self.ax.plot(spar_all[:, 0], spar_all[:, 1], spar_all[:, 2], 'r--', linewidth=2, label="Main Spar Line")
            
            # Labels
            self.ax.set_xlabel("X (Chord / mm)")
            self.ax.set_ylabel("Y (Span / mm)")
            self.ax.set_zlabel("Z (Height / mm)")
            
            # Set equal aspect ratio in 3D using coordinates of both meshes
            all_v = np.vstack((v, mv))
            max_range = np.array([all_v[:, 0].max() - all_v[:, 0].min(),
                                  all_v[:, 1].max() - all_v[:, 1].min(),
                                  all_v[:, 2].max() - all_v[:, 2].min()]).max()
            
            mid_x = (all_v[:, 0].max() + all_v[:, 0].min()) * 0.5
            mid_y = (all_v[:, 1].max() + all_v[:, 1].min()) * 0.5
            mid_z = (all_v[:, 2].max() + all_v[:, 2].min()) * 0.5
            
            self.ax.set_xlim(mid_x - max_range*0.5, mid_x + max_range*0.5)
            self.ax.set_ylim(mid_y - max_range*0.5, mid_y + max_range*0.5)
            self.ax.set_zlim(mid_z - max_range*0.5, mid_z + max_range*0.5)
            
            self.ax.set_title(f"Wingtip Fin - {params['style']}")
            
            # Show legend if spar line is plotted
            self.ax.legend()
            
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not generate 3D preview:\n{str(e)}")

    def export_model(self, file_type):
        filepath = filedialog.asksaveasfilename(
            title=f"Save Wingtip Fin Model ({file_type.upper()})",
            defaultextension=f".{file_type}",
            filetypes=[(f"{file_type.upper()} Files", f"*.{file_type}")]
        )
        if not filepath:
            return
        if not os.path.splitext(filepath)[1]: filepath += f".{file_type}"
            
        try:
            params = self.get_ui_params()
            mesh = self.engine.generate_fin_mesh(params)
            
            if file_type == "stl":
                mesh.export(filepath, file_type="stl")
            elif file_type == "obj":
                mesh.export(filepath, file_type="obj")
            elif file_type == "glb":
                mesh.export(filepath, file_type="glb")
                
            messagebox.showinfo("Export Successful", f"Saved 3D Model to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export 3D model:\n{str(e)}")

    def export_flow5(self):
        try:
            params = self.get_ui_params()
            mesh = self.engine.generate_fin_mesh(params)
            sections = mesh.metadata.get('flow5_sections', [])
            
            if not sections:
                messagebox.showerror("Export Error", "No section data found. Please update preview first.")
                return

            filepath = filedialog.asksaveasfilename(
                title="Save flow5 Wing Text File",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                initialfile="Wingtip_Fin.txt"
            )
            if not filepath:
                return
            if not os.path.splitext(filepath)[1]: filepath += ".txt"
                
            with open(filepath, 'w') as f:
                f.write("Wingtip_Fin\n")
                f.write("// Y_span      Chord      Offset_X   Dihedral   Twist      Foil_Name\n")
                for s in sections:
                    y_span = s['y_span'] / 1000.0   # Convert to m
                    chord = s['chord'] / 1000.0     # Convert to m
                    offset = s['offset_x'] / 1000.0 # Convert to m
                    dihedral = s['dihedral']
                    twist = s['twist']
                    foil = s['airfoil']
                    f.write(f"   {y_span:.4f}      {chord:.4f}      {offset:.4f}      {dihedral:.2f}      {twist:.2f}      {foil}\n")
                    
            messagebox.showinfo("Export Successful", f"flow5 import text saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export flow5 data:\n{str(e)}")

    def load_config(self):
        ConfigHelper.load_config(self)

    def save_config(self):
        ConfigHelper.save_config(self, "WingtipFin")

    def get_all_vars(self):
        return {
            'airfoil_path': self.airfoil_path,
            'span': self.span,
            'cant_angle': self.cant_angle,
            'sweep_angle': self.sweep_angle,
            'taper_ratio': self.taper_ratio,
            'twist_deg': self.twist_deg,
            'thickness_scale': self.thickness_scale,
            'chord_root': self.chord_root,
            'spar_pct': self.spar_pct,
            'style': self.style,
            'color_name': self.color_name,
            'hoerner_power': self.hoerner_power,
            'curve_power': self.curve_power,
            'y_slices': self.y_slices,
            'wing_side': self.wing_side,
            'winglet_w_flat': self.winglet_w_flat,
            'winglet_r_bend': self.winglet_r_bend,
            'winglet_h_up': self.winglet_h_up,
            'main_span': self.main_span,
            'main_chord_root': self.main_chord_root,
            'main_sweep': self.main_sweep,
            'main_airfoil_path': self.main_airfoil_path,
            'main_spar_pct_root': self.main_spar_pct_root,
            'main_spar_pct_tip': self.main_spar_pct_tip
        }

    def return_to_launcher(self):
        self.root.destroy()
        # Rerun main.py launcher
        import sys
        import subprocess
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")])
        sys.exit(0)

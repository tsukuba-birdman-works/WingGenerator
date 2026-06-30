import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.foam_engine import FoamCutterEngine


# ==========================================
# 2. UI層
# ==========================================
class FoamCutterGUI:
    def __init__(self, root, root_file=None, tip_file=None, block_width=None, wing_type=None):
        self.root = root
        self.root.title("4-Axis Foam Cutter CAM")
        self.root.geometry("950x760") # ボタン追加に合わせて拡張
        
        self.engine = FoamCutterEngine()
        
        self.root_profile_path = tk.StringVar(value=root_file if root_file else "")
        self.tip_profile_path = tk.StringVar(value=tip_file if tip_file else "")
        self.kerf_width = tk.DoubleVar(value=1.5)
        self.wire_dist = tk.DoubleVar(value=1000.0)
        self.block_width = tk.DoubleVar(value=block_width if block_width else 910.0)
        self.feedrate = tk.DoubleVar(value=100.0) 
        
        self.offset_x = tk.DoubleVar(value=0.0)
        self.offset_y = tk.DoubleVar(value=0.0)
        self.entry_x = tk.DoubleVar(value=0.0)
        self.entry_y = tk.DoubleVar(value=0.0)
        
        self.axis_lh = tk.StringVar(value="X")
        self.axis_lv = tk.StringVar(value="Y")
        self.axis_rh = tk.StringVar(value="A")
        self.axis_rv = tk.StringVar(value="Z")
        
        self.spindle_mode = tk.StringVar(value="M4 (Dynamic/Laser)")
        self.s_value = tk.DoubleVar(value=83.0) 

        self.wing_type = tk.StringVar(value=wing_type if wing_type else "Right")
        self.view_axis = tk.StringVar(value="LEFT")
        self.start_shift_pct = tk.DoubleVar(value=0.0)
        self.auto_center = tk.BooleanVar(value=False)

        self.trajectory_xy = None
        self.trajectory_az = None
        self.foam_xy = None
        self.foam_az = None
        self.dragging_entry = False

        self.create_widgets()

    def create_widgets(self):
        cf = tk.Frame(self.root)
        cf.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        tk.Label(cf, text="Root Profile [.dxf]:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        tk.Entry(cf, textvariable=self.root_profile_path, width=30).grid(row=1, column=0)
        tk.Button(cf, text="Browse", command=lambda: self.browse_file(self.root_profile_path)).grid(row=1, column=1, padx=5)

        tk.Label(cf, text="Tip Profile [.dxf]:").grid(row=2, column=0, sticky="w", pady=(10, 5))
        tk.Entry(cf, textvariable=self.tip_profile_path, width=30).grid(row=3, column=0)
        tk.Button(cf, text="Browse", command=lambda: self.browse_file(self.tip_profile_path)).grid(row=3, column=1, padx=5)

        pf = tk.LabelFrame(cf, text="Settings")
        pf.grid(row=4, column=0, columnspan=2, pady=15, sticky="ew")

        params = [
            ("Kerf / 溶け幅 (mm):", self.kerf_width),
            ("Wire Dist / 電熱線距離 (mm):", self.wire_dist),
            ("Block Width / 材料幅 (mm):", self.block_width),
            ("Feedrate / 送り速度 (mm/min):", self.feedrate)
        ]
        for i, (label, var) in enumerate(params):
            tk.Label(pf, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            tk.Entry(pf, textvariable=var, width=10).grid(row=i, column=1, sticky="w")

        tk.Label(pf, text="Shape Offset / 図形配置:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        of = tk.Frame(pf)
        of.grid(row=4, column=1, sticky="w")
        tk.Entry(of, textvariable=self.offset_x, width=5).pack(side="left")
        tk.Entry(of, textvariable=self.offset_y, width=5).pack(side="left", padx=5)

        tk.Label(pf, text="Entry Point / 進入位置:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        ef = tk.Frame(pf)
        ef.grid(row=5, column=1, sticky="w")
        tk.Entry(ef, textvariable=self.entry_x, width=5).pack(side="left")
        tk.Entry(ef, textvariable=self.entry_y, width=5).pack(side="left", padx=5)

        tk.Label(pf, text="Cut Start Point:").grid(row=6, column=0, sticky="e", padx=5, pady=2)
        sf = tk.Frame(pf)
        sf.grid(row=6, column=1, sticky="w")
        self.scale_shift = tk.Scale(sf, variable=self.start_shift_pct, from_=0, to=100, 
                                    orient="horizontal", length=120, showvalue=False, command=self.on_slider_move)
        self.scale_shift.pack(side="left")
        self.lbl_pct = tk.Label(sf, text="0%")
        self.lbl_pct.pack(side="left")

        tk.Label(pf, text="Axes (L_h, L_v, R_h, R_v):").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        af = tk.Frame(pf)
        af.grid(row=7, column=1, sticky="w")
        tk.Entry(af, textvariable=self.axis_lh, width=2).pack(side="left")
        tk.Entry(af, textvariable=self.axis_lv, width=2).pack(side="left", padx=2)
        tk.Entry(af, textvariable=self.axis_rh, width=2).pack(side="left", padx=2)
        tk.Entry(af, textvariable=self.axis_rv, width=2).pack(side="left")
        for var in [self.axis_lh, self.axis_lv, self.axis_rh, self.axis_rv]:
            var.trace_add("write", lambda *args: self.draw_plot())

        tk.Label(pf, text="Spindle / ヒーター制御:").grid(row=8, column=0, sticky="e", padx=5, pady=2)
        hf = tk.Frame(pf)
        hf.grid(row=8, column=1, sticky="w")
        tk.OptionMenu(hf, self.spindle_mode, "M3 (Constant)", "M4 (Dynamic/Laser)").pack(side="left")
        tk.Label(hf, text=" S-Value:").pack(side="left")
        tk.Entry(hf, textvariable=self.s_value, width=6).pack(side="left")

        tk.Label(pf, text="Wing Type:").grid(row=9, column=0, sticky="e", padx=5, pady=2)
        wt_frame = tk.Frame(pf)
        wt_frame.grid(row=9, column=1, sticky="w")
        tk.Radiobutton(wt_frame, text="Right Wing (Root on Right)", variable=self.wing_type, value="Right").pack(side="left")
        tk.Radiobutton(wt_frame, text="Left Wing (Root on Left)", variable=self.wing_type, value="Left").pack(side="left", padx=10)
        self.wing_type.trace_add("write", lambda *args: self.update_preview())

        # ボタンを3つに拡張
        tk.Button(cf, text="2D Preview", command=self.update_preview, bg="lightgreen", width=30).grid(row=5, column=0, columnspan=2, pady=(10,2))
        tk.Button(cf, text="3D View (Ruled Surface)", command=self.show_3d_preview, bg="plum", width=30).grid(row=6, column=0, columnspan=2, pady=(2,10))
        tk.Button(cf, text="Generate G-Code", command=self.generate_gcode, bg="lightblue", width=30).grid(row=7, column=0, columnspan=2)

        prev_f = tk.Frame(self.root)
        prev_f.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        tf = tk.Frame(prev_f)
        tf.pack(side="top", fill="x", pady=5)
        tk.Radiobutton(tf, text="Left Tower", variable=self.view_axis, value="LEFT", command=self.draw_plot).pack(side="left")
        tk.Radiobutton(tf, text="Right Tower", variable=self.view_axis, value="RIGHT", command=self.draw_plot).pack(side="left", padx=10)

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=prev_f)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_drag)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        
        if self.root_profile_path.get() and self.tip_profile_path.get():
            self.root.after(200, self.update_preview)

    def browse_file(self, var):
        f = filedialog.askopenfilename(filetypes=[("DXF Files", "*.dxf")])
        if f: var.set(f)

    def on_slider_move(self, val):
        self.lbl_pct.config(text=f"{int(float(val))}%")
        self.update_preview()

    def on_mouse_press(self, event):
        if event.inaxes != self.ax or event.xdata is None: return
        ex_px = self.ax.transData.transform((self.entry_x.get(), self.entry_y.get()))
        if np.linalg.norm(ex_px - np.array([event.x, event.y])) < 15:
            self.dragging_entry = True

    def on_mouse_drag(self, event):
        if not self.dragging_entry or event.xdata is None: return
        self.entry_x.set(round(event.xdata, 1))
        self.entry_y.set(round(event.ydata, 1))
        self.draw_plot()

    def on_mouse_release(self, event):
        self.dragging_entry = False

    def update_preview(self):
        root_path = self.root_profile_path.get()
        tip_path = self.tip_profile_path.get()
        
        f1, f2 = (tip_path, root_path) if self.wing_type.get() == "Right" else (root_path, tip_path)

        try:
            self.trajectory_xy, self.trajectory_az, self.foam_xy, self.foam_az = self.engine.compute_trajectory(
                f1, f2, self.kerf_width.get(),
                self.wire_dist.get(), self.block_width.get(),
                self.offset_x.get(), self.offset_y.get(), self.start_shift_pct.get(),
                auto_center=False
            )
            self.draw_plot()
        except Exception as e:
            print(f"Error: {e}")

    def draw_plot(self):
        if self.trajectory_xy is None or self.trajectory_az is None: return
        self.ax.clear()
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_aspect('equal', adjustable='datalim')
        
        ex, ey = self.entry_x.get(), self.entry_y.get()
        ax_names = [v.get().upper().strip() for v in [self.axis_lh, self.axis_lv, self.axis_rh, self.axis_rv]]

        if self.view_axis.get() == "LEFT":
            machine_traj, foam_traj = self.trajectory_xy, self.foam_xy
            color_m, color_f = 'b-', 'c--'
            self.ax.set(title=f"Left Tower ({ax_names[0]}{ax_names[1]})", xlabel=ax_names[0], ylabel=ax_names[1])
        else:
            machine_traj, foam_traj = self.trajectory_az, self.foam_az
            color_m, color_f = 'g-', 'm--'
            self.ax.set(title=f"Right Tower ({ax_names[2]}{ax_names[3]})", xlabel=ax_names[2], ylabel=ax_names[3])
            
        self.ax.plot(machine_traj[:, 0], machine_traj[:, 1], color_m, linewidth=1.5, label="Machine Trajectory")
        self.ax.plot(foam_traj[:, 0], foam_traj[:, 1], color_f, linewidth=1.5, label="Foam Cut Profile")
        self.ax.plot([ex, machine_traj[0, 0]], [ey, machine_traj[0, 1]], color='orange', linestyle='--', label="Lead In")
        self.ax.plot(machine_traj[0, 0], machine_traj[0, 1], 'ro', markersize=6, label="Cut Start")
        self.ax.plot(ex, ey, 'gX', markersize=10, label="Entry/Exit Point")
        self.ax.legend()
        self.canvas.draw()

    # --- 新規追加: 3Dプレビュー機能 ---
    def show_3d_preview(self):
        if self.foam_xy is None or self.foam_az is None:
            self.update_preview()
            if self.foam_xy is None:
                messagebox.showerror("Error", "Could not compute 3D trajectory. Please check your files.")
                return

        top = tk.Toplevel(self.root)
        top.title("3D Ruled Surface Preview")
        top.geometry("800x600")

        fig = Figure(figsize=(8, 6), dpi=100)
        # projection='3d' で3D描画用の軸を作成
        ax = fig.add_subplot(111, projection='3d')

        bw_half = self.block_width.get() / 2.0
        wd_half = self.wire_dist.get() / 2.0

        # 材料の左面と右面の座標（コード方向）
        chord_l, z_l = self.foam_xy[:, 0], self.foam_xy[:, 1]
        chord_r, z_r = self.foam_az[:, 0], self.foam_az[:, 1]
        
        # タワー（マシン）の軌道
        mach_chord_l, mach_z_l = self.trajectory_xy[:, 0], self.trajectory_xy[:, 1]
        mach_chord_r, mach_z_r = self.trajectory_az[:, 0], self.trajectory_az[:, 1]
        
        # 3D空間のX軸をワイヤー方向（左右）、Y軸をコード方向（前後）とする
        x_3d_l = np.full_like(chord_l, -bw_half)
        x_3d_r = np.full_like(chord_r, bw_half)
        
        x_3d_mach_l = np.full_like(mach_chord_l, -wd_half)
        x_3d_mach_r = np.full_like(mach_chord_r, wd_half)

        # 軌道の輪郭線を描画
        ax.plot(x_3d_mach_l, mach_chord_l, mach_z_l, 'c--', linewidth=1.5, alpha=0.7, label="Left Tower (XY)")
        ax.plot(x_3d_mach_r, mach_chord_r, mach_z_r, 'm--', linewidth=1.5, alpha=0.7, label="Right Tower (AZ)")
        ax.plot(x_3d_l, chord_l, z_l, 'b-', linewidth=2, label="Left Foam Cut")
        ax.plot(x_3d_r, chord_r, z_r, 'g-', linewidth=2, label="Right Foam Cut")

        # ワイヤーの軌跡（線織面 / Ruled Surface）を描画
        # 重くなりすぎないように100〜150本程度に間引く
        step = max(1, len(chord_l) // 150)
        for i in range(0, len(chord_l), step):
            # タワー間のワイヤー全体を薄く描画
            ax.plot([x_3d_mach_l[i], x_3d_mach_r[i]], [mach_chord_l[i], mach_chord_r[i]], [mach_z_l[i], mach_z_r[i]], color='gray', alpha=0.2)
            # 材料内部のワイヤーを少し濃く描画
            ax.plot([x_3d_l[i], x_3d_r[i]], [chord_l[i], chord_r[i]], [z_l[i], z_r[i]], color='black', alpha=0.4)

        # カット開始地点
        ax.plot([x_3d_mach_l[0]], [mach_chord_l[0]], [mach_z_l[0]], 'ro')
        ax.plot([x_3d_mach_r[0]], [mach_chord_r[0]], [mach_z_r[0]], 'ro')

        # 軸ラベルの設定 (直感的な方向にマッピング)
        ax.set_xlabel('Wire Axis (Left-Right) mm')
        ax.set_ylabel('Chord Axis (Front-Back) mm')
        ax.set_zlabel('Z (Vertical) mm')
        ax.set_title("Foam Block Cut Preview")
        ax.legend()

        # XYZの比率を1:1:1に近づけるためのスケーリング補正
        max_range = np.array([wd_half*2, mach_chord_l.max()-mach_chord_l.min(), mach_z_l.max()-mach_z_l.min()]).max() / 2.0
        mid_x = 0
        mid_y = (mach_chord_l.max()+mach_chord_l.min()) * 0.5
        mid_z = (mach_z_l.max()+mach_z_l.min()) * 0.5
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)

        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()
    # ----------------------------------

    def generate_gcode(self):
        if self.trajectory_xy is None:
            messagebox.showerror("Error", "Preview trajectory first.")
            return
            
        axes = [v.get().upper().strip() for v in [self.axis_lh, self.axis_lv, self.axis_rh, self.axis_rv]]
        
        gcode_str = self.engine.generate_gcode_string(
            self.trajectory_xy, self.trajectory_az, 
            self.foam_xy, self.foam_az,
            self.entry_x.get(), self.entry_y.get(), axes,
            target_f=self.feedrate.get(),
            spindle_mode=self.spindle_mode.get(),
            s_value=self.s_value.get()
        )

        save_path = filedialog.asksaveasfilename(defaultextension=".nc", filetypes=[("G-Code", "*.nc *.gcode")])
        if save_path:
            with open(save_path, 'w') as f:
                f.write(gcode_str)
            messagebox.showinfo("Success", f"Saved to:\n{save_path}")
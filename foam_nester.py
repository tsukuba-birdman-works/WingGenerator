import os
#! /usr/bin/python3
import sys
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class GCodePart:
    def __init__(self, filename):
        self.filename = filename
        self.name = os.path.basename(filename)
        self.raw_lines = []
        self.pts_xy = []
        self.pts_az = []
        self.f_vals = []
        self.axes = ['X', 'Y', 'A', 'Z'] # default
        
        # Transformations
        self.dx = 0.0
        self.dy = 0.0
        self.angle_deg = 0.0
        self.flip_x = False
        self.flip_y = False
        self.swap_xyaz = False
        
        self.load(filename)
        
    def load(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # First pass to guess axes letters
        axes_set = set()
        for line in lines:
            line = line.split(';')[0].strip()
            if line.startswith('G1') or line.startswith('G0'):
                tokens = line.split()
                for token in tokens[1:]:
                    if token[0].isalpha() and token[0] not in ['F', 'S', 'G', 'M']:
                        axes_set.add(token[0])
                        
        if 'X' in axes_set and 'Y' in axes_set and 'A' in axes_set and 'Z' in axes_set:
            self.axes = ['X', 'Y', 'A', 'Z']
        elif 'X' in axes_set and 'Y' in axes_set and 'U' in axes_set and 'V' in axes_set:
            self.axes = ['X', 'Y', 'U', 'V']
        elif 'X' in axes_set and 'Y' in axes_set and 'U' in axes_set and 'Z' in axes_set:
            self.axes = ['X', 'Y', 'U', 'Z']
        else:
            axes_list = [a for a in ['X', 'Y', 'A', 'Z', 'U', 'V'] if a in axes_set]
            if len(axes_list) >= 4:
                self.axes = axes_list[:4]
            else:
                self.axes = ['X', 'Y', 'A', 'Z']

        ax_lh, ax_lv, ax_rh, ax_rv = self.axes
        
        last_x, last_y, last_a, last_z, last_f = 0.0, 0.0, 0.0, 0.0, 300.0
        
        for line_raw in lines:
            if "Entry Point" in line_raw or "Lead-out" in line_raw:
                continue
            self.raw_lines.append(line_raw)
            line = line_raw.split(';')[0].strip()
            if line.startswith('G1') or line.startswith('G0'):
                tokens = line.split()
                has_coord = False
                for token in tokens[1:]:
                    try:
                        val = float(token[1:]) if len(token) > 1 else 0.0
                    except: continue
                    if token.startswith(ax_lh): last_x = val; has_coord = True
                    elif token.startswith(ax_lv): last_y = val; has_coord = True
                    elif token.startswith(ax_rh): last_a = val; has_coord = True
                    elif token.startswith(ax_rv): last_z = val; has_coord = True
                    elif token.startswith('F'): last_f = val
                
                if has_coord:
                    self.pts_xy.append((last_x, last_y))
                    self.pts_az.append((last_a, last_z))
                    self.f_vals.append(last_f)

        self.pts_xy = np.array(self.pts_xy) if self.pts_xy else np.zeros((1, 2))
        self.pts_az = np.array(self.pts_az) if self.pts_az else np.zeros((1, 2))
        
        if len(self.pts_xy) > 0:
            cx = (np.min(self.pts_xy[:,0]) + np.max(self.pts_xy[:,0])) / 2.0
            cy = (np.min(self.pts_xy[:,1]) + np.max(self.pts_xy[:,1])) / 2.0
            self.dx = -cx
            self.dy = -cy

    def get_transformed_paths(self):
        xy = self.pts_xy.copy()
        az = self.pts_az.copy()
        
        if self.swap_xyaz:
            xy, az = az.copy(), xy.copy()
            
        cx = (np.min(xy[:,0]) + np.max(xy[:,0])) / 2.0 if len(xy)>0 else 0
        cy = (np.min(xy[:,1]) + np.max(xy[:,1])) / 2.0 if len(xy)>0 else 0
        c_xy = np.array([cx, cy])
        
        ca_x = (np.min(az[:,0]) + np.max(az[:,0])) / 2.0 if len(az)>0 else 0
        ca_y = (np.min(az[:,1]) + np.max(az[:,1])) / 2.0 if len(az)>0 else 0
        c_az = np.array([ca_x, ca_y])
        
        xy -= c_xy
        az -= c_az
        
        if self.flip_x:
            xy[:,0] *= -1
            az[:,0] *= -1
        if self.flip_y:
            xy[:,1] *= -1
            az[:,1] *= -1
            
        rad = np.radians(self.angle_deg)
        cos_a, sin_a = np.cos(rad), np.sin(rad)
        R = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        
        xy = np.dot(xy, R.T)
        az = np.dot(az, R.T)
        
        xy += c_xy
        az += c_az
        
        xy[:,0] += self.dx
        xy[:,1] += self.dy
        az[:,0] += self.dx
        az[:,1] += self.dy
        
        return xy, az

class RoutePoint:
    def __init__(self, x, y, a, z):
        self.x = x
        self.y = y
        self.a = a
        self.z = z

class FoamNesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Foam Cutter G-Code Nester")
        self.root.geometry("1000x800")
        
        self.parts = []
        self.global_route = []
        self.selected_idx = -1
        self.selected_waypoint_idx = -1
        self.route_mode = False

        self.undo_stack = []
        self.root.bind('<Control-z>', self.undo)
        self.root.bind('<Control-Z>', self.undo)
        
        self.setup_ui()
        
    def get_current_state(self):
        import copy
        state = {
            'parts_list': list(self.parts),
            'parts_props': [{'dx': p.dx, 'dy': p.dy, 'angle_deg': p.angle_deg, 'flip_x': p.flip_x, 'flip_y': p.flip_y} for p in self.parts],
            'global_route': []
        }
        if hasattr(self, 'global_route'):
            for item in self.global_route:
                if hasattr(item, 'x'): # RoutePoint
                    state['global_route'].append(type(item)(item.x, item.y, item.a, item.z))
                else:
                    state['global_route'].append(item)
        return state

    def push_undo(self):
        self.undo_stack.append(self.get_current_state())
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def undo(self, event=None):
        if not self.undo_stack: return
        state = self.undo_stack.pop()
        
        self.parts = list(state['parts_list'])
        for i, p_state in enumerate(state['parts_props']):
            p = self.parts[i]
            p.dx = p_state['dx']
            p.dy = p_state['dy']
            p.angle_deg = p_state['angle_deg']
            p.flip_x = p_state['flip_x']
            p.flip_y = p_state['flip_y']
            
        self.global_route = state['global_route']
        
        self.listbox.delete(0, 'end')
        for p in self.parts:
            self.listbox.insert('end', p.name)
            
        if self.selected_idx >= len(self.parts):
            self.selected_idx = -1
        if self.selected_idx >= 0:
            self.listbox.selection_set(self.selected_idx)
            
        self.update_plot(preserve_limits=True)

    def setup_ui(self):
        left_frame = ttk.Frame(self.root, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Left Panel Controls ---
        ttk.Button(left_frame, text="Load G-Code", command=self.load_gcode).pack(fill=tk.X, pady=2)

        self.listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, height=10)
        self.listbox.pack(fill=tk.X, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        ttk.Button(left_frame, text="Remove Selected", command=self.remove_selected).pack(fill=tk.X, pady=2)
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Label(left_frame, text="Material Height (Y):").pack()
        self.mat_height = tk.DoubleVar(value=100.0)
        tk.Spinbox(left_frame, from_=10.0, to=500.0, increment=5.0, textvariable=self.mat_height, command=self.update_plot).pack(fill=tk.X, pady=2)
        self.mat_height.trace_add('write', lambda *a: self.update_plot())
        
        self.lbl_warning = tk.Label(left_frame, text="", fg="red", font=("Helvetica", 10, "bold"), width=25)
        self.lbl_warning.pack(fill=tk.X, pady=2)

        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Label(left_frame, text="Transformations").pack()
        
        ttk.Label(left_frame, text="Rotation (deg):").pack()
        self.angle_var = tk.DoubleVar(value=0.0)
        self.scale_rot = tk.Scale(left_frame, variable=self.angle_var, from_=-180, to=180, orient="horizontal", command=self.on_angle_change)
        self.scale_rot.pack(fill=tk.X, pady=2)
        ttk.Button(left_frame, text="Auto Rotate (Min Y)", command=self.auto_minimize_thickness).pack(fill=tk.X, pady=2)

        ttk.Button(left_frame, text="Mirror L/R (Swap & Flip)", command=lambda: self.transform('swap_flip')).pack(fill=tk.X, pady=5)

        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        self.btn_route = ttk.Button(left_frame, text="Enter Route Mode", command=self.toggle_route_mode)
        self.btn_route.pack(fill=tk.X, pady=2)
        self.route_info = ttk.Label(left_frame, text="Routes connect Part N to N+1", wraplength=200)
        self.route_info.pack(fill=tk.X, pady=2)
        ttk.Button(left_frame, text="Clear Routes for Selected", command=self.clear_routes).pack(fill=tk.X, pady=2)

        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Button(left_frame, text="Export Nested G-Code", command=self.export_gcode).pack(fill=tk.X, pady=2)

        # --- Right Panel Canvases ---
        self.fig = Figure(figsize=(8, 8))
        self.ax_xy = self.fig.add_subplot(211)
        self.ax_az = self.fig.add_subplot(212)

        # Sync limits
        self.ax_xy.callbacks.connect('xlim_changed', self.on_xlim_changed)
        self.ax_xy.callbacks.connect('ylim_changed', self.on_ylim_changed)

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, right_frame)
        self.toolbar.update()

        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.drag_active = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_plot()

    def on_close(self):
        # Prevent cursor sticking in some environments
        self.root.config(cursor="arrow")
        self.root.destroy()

    def on_xlim_changed(self, ax):
        if ax == self.ax_xy:
            self.ax_az.set_xlim(ax.get_xlim())
    def on_ylim_changed(self, ax):
        if ax == self.ax_xy:
            self.ax_az.set_ylim(ax.get_ylim())

    def load_gcode(self):
        filepaths = filedialog.askopenfilenames(title="Select G-Code files", filetypes=[("G-Code", "*.gcode *.nc"), ("All Files", "*.*")])
        for fp in filepaths:
            part = GCodePart(fp)
            self.parts.append(part)
            self.listbox.insert(tk.END, part.name)
        self.update_plot()
        
    def remove_selected(self):
        idx = self.listbox.curselection()
        if idx:
            self.push_undo()
            i = idx[0]
            del self.parts[i]
            # Clean up routes
            self.global_route = [r for r in self.global_route if not (isinstance(r, int) and r == i)]
            self.listbox.delete(i)
            self.selected_idx = -1
            self.update_plot()
            
    def on_select(self, event):
        idx = self.listbox.curselection()
        if idx:
            self.selected_idx = idx[0]
            self.selected_waypoint_idx = -1
            self.angle_var.set(self.parts[self.selected_idx].angle_deg)
            self.update_plot()
            
    def on_angle_change(self, val):
        if self.selected_idx < 0: return
        self.push_undo()
        self.parts[self.selected_idx].angle_deg = float(val)
        self.update_plot(preserve_limits=True)
            
    def transform(self, action):
        if self.selected_idx < 0: return
        self.push_undo()
        part = self.parts[self.selected_idx]
        if action == 'swap_flip':
            part.swap_xyaz = not part.swap_xyaz
            part.flip_x = not part.flip_x
        self.update_plot(preserve_limits=True)

    def auto_minimize_thickness(self):
        if self.selected_idx < 0: return
        self.push_undo()
        part = self.parts[self.selected_idx]
        
        min_h = float('inf')
        best_angle = part.angle_deg
        
        for a in np.arange(0, 180, 0.5):
            part.angle_deg = a
            xy, az = part.get_transformed_paths()
            
            h_xy = np.max(xy[:,1]) - np.min(xy[:,1]) if len(xy) > 0 else 0
            h_az = np.max(az[:,1]) - np.min(az[:,1]) if len(az) > 0 else 0
            h = max(h_xy, h_az)
            
            if h < min_h:
                min_h = h
                best_angle = a
                
        part.angle_deg = best_angle
        self.angle_var.set(best_angle)
        self.update_plot(preserve_limits=True)
        
    def toggle_route_mode(self):
        self.route_mode = not self.route_mode
        if self.route_mode:
            self.btn_route.config(text="Exit Route Mode")
            messagebox.showinfo("Route Mode", "Click anywhere to build your cut path.\nClick parts to add them to the path, click empty space to add waypoints.")
        else:
            self.btn_route.config(text="Enter Route Mode")
            
    def clear_routes(self):
        self.push_undo()
        self.global_route = []
        self.update_plot(preserve_limits=True)
        
    def on_press(self, event):
        if self.toolbar.mode != '': return
        if event.inaxes not in [self.ax_xy, self.ax_az]: return

        min_dist = float('inf')
        closest_i = -1
        for i, part in enumerate(self.parts):
            xy, az = part.get_transformed_paths()
            if event.inaxes == self.ax_xy and len(xy) > 0:
                dist = np.min(np.sqrt((xy[:,0] - event.xdata)**2 + (xy[:,1] - event.ydata)**2))
            elif event.inaxes == self.ax_az and len(az) > 0:
                dist = np.min(np.sqrt((az[:,0] - event.xdata)**2 + (az[:,1] - event.ydata)**2))
            else: dist = float('inf')
            if dist < min_dist:
                min_dist = dist
                closest_i = i

        min_dist_wp = float('inf')
        closest_wp_i = -1
        for i, item in enumerate(self.global_route):
            if isinstance(item, RoutePoint):
                if event.inaxes == self.ax_xy:
                    dist = np.sqrt((item.x - event.xdata)**2 + (item.y - event.ydata)**2)
                else:
                    dist = np.sqrt((item.a - event.xdata)**2 + (item.z - event.ydata)**2)
                if dist < min_dist_wp:
                    min_dist_wp = dist
                    closest_wp_i = i

        if self.route_mode:
            if min_dist_wp < 5 and min_dist_wp < min_dist:
                self.selected_idx = -1
                self.selected_waypoint_idx = closest_wp_i
                self.drag_active = True
                self.drag_start_x = event.xdata
                self.drag_start_y = event.ydata
                self._drag_start_state = self.get_current_state()
                self.has_dragged = False
            elif min_dist < 5:
                self.push_undo()
                if not hasattr(self, 'global_route'): self.global_route = []
                if not self.global_route or self.global_route[-1] != closest_i:
                    self.global_route.append(closest_i)
                    self.selected_waypoint_idx = -1
            else:
                self.push_undo()
                if not hasattr(self, 'global_route'): self.global_route = []
                x, y = event.xdata, event.ydata
                self.global_route.append(RoutePoint(x, y, x, y))
                self.selected_idx = -1
                self.selected_waypoint_idx = len(self.global_route) - 1
                self.drag_active = True
                self.drag_start_x = event.xdata
                self.drag_start_y = event.ydata
                self._drag_start_state = self.get_current_state()
                self.has_dragged = False
            self.update_plot(preserve_limits=True)
            return
                
        if min_dist_wp < 5 and min_dist_wp < min_dist:
            self.selected_idx = -1
            self.selected_waypoint_idx = closest_wp_i
            self.listbox.selection_clear(0, tk.END)
        elif min_dist < 5:
            self.selected_idx = closest_i
            self.selected_waypoint_idx = -1
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(closest_i)
        else:
            self.selected_idx = -1
            self.selected_waypoint_idx = -1
            self.listbox.selection_clear(0, tk.END)

        if self.selected_idx >= 0 or self.selected_waypoint_idx >= 0:
            self.drag_active = True
            self.drag_start_x = event.xdata
            self.drag_start_y = event.ydata
            self._drag_start_state = self.get_current_state()
            self.has_dragged = False
        self.update_plot(preserve_limits=True)

    def on_motion(self, event):
        self.has_dragged = True
        if not self.drag_active or event.inaxes not in [self.ax_xy, self.ax_az]: return
        if self.selected_idx < 0 and self.selected_waypoint_idx < 0: return

        dx = event.xdata - self.drag_start_x
        dy = event.ydata - self.drag_start_y

        if self.selected_idx >= 0:
            part = self.parts[self.selected_idx]
            part.dx += dx
            part.dy += dy
        elif self.selected_waypoint_idx >= 0:
            wp = self.global_route[self.selected_waypoint_idx]
            if event.inaxes == self.ax_xy:
                wp.x += dx
                wp.y += dy
            else:
                wp.a += dx
                wp.z += dy
        
        self.drag_start_x = event.xdata
        self.drag_start_y = event.ydata
        self.update_plot(preserve_limits=True)

    def on_release(self, event):
        if getattr(self, 'drag_active', False) and getattr(self, 'has_dragged', False) and hasattr(self, '_drag_start_state'):
            self.undo_stack.append(self._drag_start_state)
            if len(self.undo_stack) > 50: self.undo_stack.pop(0)
        self.drag_active = False
        self.has_dragged = False

    def update_plot(self, preserve_limits=False):
        if preserve_limits:
            old_xlim = self.ax_xy.get_xlim()
            old_ylim = self.ax_xy.get_ylim()

        self.ax_xy.clear()
        self.ax_az.clear()

        self.ax_xy.set_title("XY Axis (Left Tower)")
        self.ax_az.set_title("AZ Axis (Right Tower)")

        self.ax_xy.grid(True, linestyle='--', alpha=0.5)
        self.ax_az.grid(True, linestyle='--', alpha=0.5)

        self.ax_xy.set_aspect('equal', adjustable='datalim')
        self.ax_az.set_aspect('equal', adjustable='datalim')
        
        try:
            h = self.mat_height.get()
        except:
            h = 100.0

        self.ax_xy.axhline(0, color='gray', linestyle='-')
        self.ax_xy.axhline(h, color='gray', linestyle='-')
        self.ax_az.axhline(0, color='gray', linestyle='-')
        self.ax_az.axhline(h, color='gray', linestyle='-')

        exceeds = False

        for i, part in enumerate(self.parts):
            xy, az = part.get_transformed_paths()

            color = 'red' if i == self.selected_idx else 'blue'
            alpha = 1.0 if i == self.selected_idx else 0.5

            if len(xy) > 0:
                self.ax_xy.plot(xy[:,0], xy[:,1], color=color, alpha=alpha, label=part.name if i==self.selected_idx else "")
                self.ax_xy.plot(xy[0,0], xy[0,1], 'go', markersize=4) # Start point
                if np.max(xy[:,1]) > h or np.min(xy[:,1]) < 0:
                    exceeds = True
            if len(az) > 0:
                self.ax_az.plot(az[:,0], az[:,1], color=color, alpha=alpha)
                self.ax_az.plot(az[0,0], az[0,1], 'go', markersize=4)
                if np.max(az[:,1]) > h or np.min(az[:,1]) < 0:
                    exceeds = True

        if hasattr(self, 'lbl_warning'):
            if exceeds:
                self.lbl_warning.config(text=f"⚠️ Exceeds Height ({h}mm)", fg="red")
            else:
                self.lbl_warning.config(text="✓ Within limits", fg="green")

        # Draw global route
        if hasattr(self, 'global_route') and self.global_route:
            p_xy = []
            p_az = []
            for i, item in enumerate(self.global_route):
                if isinstance(item, int) and item < len(self.parts):
                    xy, az = self.parts[item].get_transformed_paths()
                    if len(xy) > 0:
                        if len(p_xy) > 0:
                            # Draw line from prev to start of this part
                            self.ax_xy.plot([p_xy[-1][0], xy[0,0]], [p_xy[-1][1], xy[0,1]], 'k--', alpha=0.8)
                            self.ax_az.plot([p_az[-1][0], az[0,0]], [p_az[-1][1], az[0,1]], 'k--', alpha=0.8)
                        # We don't draw the part itself here (already drawn), just update current position to end of part
                        p_xy.append(xy[-1])
                        p_az.append(az[-1])
                elif isinstance(item, RoutePoint):
                    if len(p_xy) > 0:
                        self.ax_xy.plot([p_xy[-1][0], item.x], [p_xy[-1][1], item.y], 'k--', alpha=0.8)
                        self.ax_az.plot([p_az[-1][0], item.a], [p_az[-1][1], item.z], 'k--', alpha=0.8)
                    p_xy.append([item.x, item.y])
                    p_az.append([item.a, item.z])
                    
                    color = 'magenta' if i == getattr(self, 'selected_waypoint_idx', -1) else 'k'
                    ms = 8 if i == getattr(self, 'selected_waypoint_idx', -1) else 6
                    self.ax_xy.plot(item.x, item.y, marker='x', color=color, markersize=ms)
                    self.ax_az.plot(item.a, item.z, marker='x', color=color, markersize=ms)

        if preserve_limits:
            self.ax_xy.set_xlim(old_xlim)
            self.ax_xy.set_ylim(old_ylim)
            self.ax_az.set_xlim(old_xlim)
            self.ax_az.set_ylim(old_ylim)
        else:
            # Sync limits exactly across XY and AZ
            # self.ax_xy auto-scaled its limits based on XY paths, ax_az on AZ paths.
            # We want both to share the maximum bounding box of both.
            xlim_xy = self.ax_xy.get_xlim()
            ylim_xy = self.ax_xy.get_ylim()
            xlim_az = self.ax_az.get_xlim()
            ylim_az = self.ax_az.get_ylim()
            
            new_xlim = (min(xlim_xy[0], xlim_az[0]), max(xlim_xy[1], xlim_az[1]))
            new_ylim = (min(ylim_xy[0], ylim_az[0]), max(ylim_xy[1], ylim_az[1]))
            
            self.ax_xy.set_xlim(new_xlim)
            self.ax_xy.set_ylim(new_ylim)
            self.ax_az.set_xlim(new_xlim)
            self.ax_az.set_ylim(new_ylim)

        self.canvas.draw()
        
    def export_gcode(self):
        if not self.parts: return
        filepath = filedialog.asksaveasfilename(title="Save Nested G-Code", defaultextension=".gcode")
        if not filepath: return
        if not os.path.splitext(filepath)[1]: filepath += ".gcode"
        
        out_lines = []
        out_lines.append("; Nested G-Code generated by Foam Nester\n")
        out_lines.append("G21 ; Millimeters\n")
        out_lines.append("G90 ; Absolute positioning\n")
        
        ax_lh, ax_lv, ax_rh, ax_rv = self.parts[0].axes
        
        if not hasattr(self, 'global_route') or not self.global_route:
            # Fallback to sequential cutting if no route defined
            seq = list(range(len(self.parts)))
        else:
            seq = self.global_route

        part_count = 0
        for item in seq:
            if isinstance(item, int) and item < len(self.parts):
                part = self.parts[item]
                xy, az = part.get_transformed_paths()
                out_lines.append(f"\n; --- Part {item}: {part.name} ---\n")

                for j in range(len(xy)):
                    f_val = part.f_vals[j]
                    cmd = f"G1 {ax_lh}{xy[j,0]:.3f} {ax_lv}{xy[j,1]:.3f} {ax_rh}{az[j,0]:.3f} {ax_rv}{az[j,1]:.3f} F{f_val:.1f}\n"
                    out_lines.append(cmd)
                part_count += 1
            elif isinstance(item, RoutePoint):
                out_lines.append(f"; --- Waypoint ---\n")
                out_lines.append(f"G1 {ax_lh}{item.x:.3f} {ax_lv}{item.y:.3f} {ax_rh}{item.a:.3f} {ax_rv}{item.z:.3f} F1000.0\n")
                
        with open(filepath, 'w') as f:
            f.writelines(out_lines)
            
        messagebox.showinfo("Export", f"Saved nested G-Code to {filepath}")

if __name__ == '__main__':
    root = tk.Tk()
    app = FoamNesterApp(root)
    root.mainloop()

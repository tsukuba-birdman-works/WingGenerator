with open('ui/single_mode.py', 'r') as f:
    text = f.read()

old_code = """        if self.safe_float(self.spar_hole_dia) > 0: self.ax.plot(c_m[0], c_m[1], 'kx', markersize=6); self.ax.plot(h_m[:, 0], h_m[:, 1], 'r-', linewidth=1.5)
        if self.safe_float(self.front_spar_dia) > 0: self.ax.plot(c_f[0], c_f[1], 'cx', markersize=6); self.ax.plot(h_f[:, 0], h_f[:, 1], 'c-', linewidth=1.5)
        if self.safe_float(self.rear_spar_dia) > 0: self.ax.plot(c_r[0], c_r[1], 'mx', markersize=6); self.ax.plot(h_r[:, 0], h_r[:, 1], 'm-', linewidth=1.5)"""

new_code = """        if len(h_m) > 0: self.ax.plot(c_m[0], c_m[1], 'kx', markersize=6); self.ax.plot(h_m[:, 0], h_m[:, 1], 'r-', linewidth=1.5)
        if len(h_f) > 0: self.ax.plot(c_f[0], c_f[1], 'cx', markersize=6); self.ax.plot(h_f[:, 0], h_f[:, 1], 'c-', linewidth=1.5)
        if len(h_r) > 0: self.ax.plot(c_r[0], c_r[1], 'mx', markersize=6); self.ax.plot(h_r[:, 0], h_r[:, 1], 'm-', linewidth=1.5)"""

text = text.replace(old_code, new_code)

with open('ui/single_mode.py', 'w') as f:
    f.write(text)

import re

with open('ui/batch_mode.py', 'r') as f: code = f.read()

target = r"            kerf_val = self\.safe_float\(getattr\(self, 'foam_cut_kerf', tk\.StringVar\(value=\"1\.5\"\)\), 1\.5\)\n            wire_dist_val = self\.safe_float\(getattr\(self, 'foam_wire_dist', tk\.StringVar\(value=\"1000\.0\"\)\), 1000\.0\)\n            offset_x_val = self\.safe_float\(getattr\(self, 'foam_offset_x', tk\.StringVar\(value=\"0\.0\"\)\), 0\.0\)\n            offset_y_val = self\.safe_float\(getattr\(self, 'foam_offset_y', tk\.StringVar\(value=\"0\.0\"\)\), 0\.0\)\n            entry_x_val = self\.safe_float\(getattr\(self, 'foam_entry_x', tk\.StringVar\(value=\"0\.0\"\)\), 0\.0\)\n            entry_y_val = self\.safe_float\(getattr\(self, 'foam_entry_y', tk\.StringVar\(value=\"0\.0\"\)\), 0\.0\)\n            feedrate_val = self\.safe_float\(getattr\(self, 'foam_feedrate', tk\.StringVar\(value=\"100\.0\"\)\), 100\.0\)"
repl = """            kerf_val = self.safe_float(self.pm.vars.get('foam_cut_kerf', tk.StringVar(value="1.5")), 1.5)
            wire_dist_val = self.safe_float(self.pm.vars.get('foam_wire_dist', tk.StringVar(value="1000.0")), 1000.0)
            offset_x_val = self.safe_float(self.pm.vars.get('foam_offset_x', tk.StringVar(value="0.0")), 0.0)
            offset_y_val = self.safe_float(self.pm.vars.get('foam_offset_y', tk.StringVar(value="0.0")), 0.0)
            entry_x_val = self.safe_float(self.pm.vars.get('foam_entry_x', tk.StringVar(value="0.0")), 0.0)
            entry_y_val = self.safe_float(self.pm.vars.get('foam_entry_y', tk.StringVar(value="0.0")), 0.0)
            feedrate_val = self.safe_float(self.pm.vars.get('foam_feedrate', tk.StringVar(value="100.0")), 100.0)"""

code = re.sub(target, repl, code, flags=re.DOTALL)

with open('ui/batch_mode.py', 'w') as f: f.write(code)

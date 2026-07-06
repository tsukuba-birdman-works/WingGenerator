import re

with open('ui/batch_mode.py', 'r') as f: code = f.read()

target = r"            if target == \"Plank\":\n                target_thickness = self\.safe_float\(getattr\(self, 'plank_thick', tk\.StringVar\(value=\"0\.0\"\)\)\)\n            else:\n                target_thickness = self\.safe_float\(getattr\(self, 'te_cut', tk\.StringVar\(value=\"0\.0\"\)\)\)"
repl = """            if target == "Plank":
                target_thickness = self.safe_float(self.pm.vars.get('plank_thick', tk.StringVar(value="0.0")))
            else:
                target_thickness = self.safe_float(self.pm.vars.get('te_cut', tk.StringVar(value="0.0")))"""

code = re.sub(target, repl, code, flags=re.DOTALL)

with open('ui/batch_mode.py', 'w') as f: f.write(code)

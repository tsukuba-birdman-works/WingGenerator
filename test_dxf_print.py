import re
with open('core/export_dxf.py', 'r') as f: code = f.read()
code = code.replace(
    "jig_pts = self.engine.generate_jig_at_y(self.p, jy - joint)",
    "print('CALLING JIG FOR Y=', jy)\n                        jig_pts = self.engine.generate_jig_at_y(self.p, jy - joint)"
)
with open('core/export_dxf.py', 'w') as f: f.write(code)

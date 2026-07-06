with open('core/export_dxf.py', 'r') as f:
    code = f.read()

# 1. Update _export_single_dxf signature and call
old_sig = "def _export_single_dxf(self, filepath, res):"
new_sig = "def _export_single_dxf(self, filepath, res, jig_pts=None):"
code = code.replace(old_sig, new_sig)

old_call = "res[17], self.p['root_bolt2'][2], res[18], res[19], res[22], res[23])"
new_call = "res[17], self.p['root_bolt2'][2], res[18], res[19], res[22], res[23], jig_pts=jig_pts)"
code = code.replace(old_call, new_call)

# 2. Update export_all_ribs
old_loop1 = """        for i, y_local in enumerate(self.p['y_positions']):
            res = self._generate_rib_at_y(y_local, i, self.p['rib_thick'])
            y_global = y_local + self.p['joint_length']
            filename = f"{prefix}No.{i}_Y{y_global:.1f}mm.dxf"
            filepath = os.path.join(dir_path, filename)
            self._export_single_dxf(filepath, res)"""
new_loop1 = """        for i, y_local in enumerate(self.p['y_positions']):
            res = self._generate_rib_at_y(y_local, i, self.p['rib_thick'])
            jig_pts = self.engine.generate_jig_at_y(self.p, y_local)
            y_global = y_local + self.p['joint_length']
            filename = f"{prefix}No.{i}_Y{y_global:.1f}mm.dxf"
            filepath = os.path.join(dir_path, filename)
            self._export_single_dxf(filepath, res, jig_pts=jig_pts)"""
code = code.replace(old_loop1, new_loop1)

old_loop2 = """            y_global = y_local + self.p['joint_length']
            filename = f"{prefix}CarbonRib_{cconf['loc'].capitalize()}_{cconf['pos'].capitalize()}_Y{y_global:.1f}mm.dxf"
            filepath = os.path.join(dir_path, filename)
            self._export_single_dxf(filepath, res)"""
new_loop2 = """            jig_pts = self.engine.generate_jig_at_y(self.p, y_local)
            y_global = y_local + self.p['joint_length']
            filename = f"{prefix}CarbonRib_{cconf['loc'].capitalize()}_{cconf['pos'].capitalize()}_Y{y_global:.1f}mm.dxf"
            filepath = os.path.join(dir_path, filename)
            self._export_single_dxf(filepath, res, jig_pts=jig_pts)"""
code = code.replace(old_loop2, new_loop2)

with open('core/export_dxf.py', 'w') as f:
    f.write(code)

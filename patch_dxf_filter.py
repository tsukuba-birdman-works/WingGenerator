import re

with open('core/export_dxf.py', 'r') as f: code = f.read()

# For Normal Ribs
ribs_search = r"        if target_ribs:\n            for i, y_local in enumerate\(self\.p\['y_positions'\]\):"
ribs_add = """        if target_ribs:
            dxf_start_idx = self.p.get('dxf_start_idx', 0)
            dxf_end_idx = self.p.get('dxf_end_idx', len(self.p['y_positions']) - 1)
            for i, y_local in enumerate(self.p['y_positions']):
                if i < dxf_start_idx or i > dxf_end_idx: continue"""
code = re.sub(ribs_search, ribs_add, code, flags=re.DOTALL)

# For Carbon Ribs
carbon_search = r"        if target_carbon:\n            for cconf in self\.p\['carbon_rib_configs'\]:\n                if not cconf\['act'\]: continue\n                idx, y_local = cconf\['idx'\], self\.p\['y_positions'\]\[cconf\['idx'\]\]"
carbon_add = """        if target_carbon:
            dxf_start_idx = self.p.get('dxf_start_idx', 0)
            dxf_end_idx = self.p.get('dxf_end_idx', len(self.p['y_positions']) - 1)
            for cconf in self.p['carbon_rib_configs']:
                if not cconf['act']: continue
                idx, y_local = cconf['idx'], self.p['y_positions'][cconf['idx']]
                if idx < dxf_start_idx or idx > dxf_end_idx: continue"""
code = re.sub(carbon_search, carbon_add, code, flags=re.DOTALL)

# For Jigs
jig_search = r"                    for j_idx, jy in enumerate\(jigs\):\n                        print\('CALLING JIG FOR Y=', jy\)\n                        jig_pts = self\.engine\.generate_jig_at_y\(self\.p, jy - joint\)"
jig_add = """                    dxf_start_idx = self.p.get('dxf_start_idx', 0)
                    dxf_end_idx = self.p.get('dxf_end_idx', len(self.p['y_positions']) - 1)
                    min_y_range = self.p['y_positions'][dxf_start_idx] + joint if dxf_start_idx < len(self.p['y_positions']) else 0
                    max_y_range = self.p['y_positions'][dxf_end_idx] + joint if dxf_end_idx < len(self.p['y_positions']) else 99999
                    for j_idx, jy in enumerate(jigs):
                        if jy < min_y_range - 1.0 or jy > max_y_range + 1.0: continue
                        print('CALLING JIG FOR Y=', jy)
                        jig_pts = self.engine.generate_jig_at_y(self.p, jy - joint)"""
code = re.sub(jig_search, jig_add, code, flags=re.DOTALL)

with open('core/export_dxf.py', 'w') as f: f.write(code)

import re

with open('ui/batch_mode.py', 'r') as f: code = f.read()

target = r"            \*\*\{f'mat_\{k\}': self\.pm\.vars\[f'mat_\{k\}'\]\.get\(\) for k in \['ribs', 'main_spar', 'front_spar', 'rear_spar', 'plank', 'te', 'connectors', 'stringers', 'xbrace_wires', 'diag_spars', 'carbon_ribs', 'te_caps', 'rib_caps', 'film'\] if f'mat_\{k\}' in self\.pm\.vars\},"
repl = """            **{f'mat_{k}': self.pm.vars[f'mat_{k}'].get() for k in ['ribs', 'main_spar', 'front_spar', 'rear_spar', 'plank', 'te', 'connectors', 'stringers', 'xbrace_wires', 'diag_spars', 'carbon_ribs', 'te_caps', 'rib_caps', 'film'] if f'mat_{k}' in self.pm.vars},
            'dxf_start_idx': self.combo_dxf_start.current() if hasattr(self, 'combo_dxf_start') else 0,
            'dxf_end_idx': self.combo_dxf_end.current() if hasattr(self, 'combo_dxf_end') else (len(self.y_positions) - 1 if hasattr(self, 'y_positions') else 0),"""
code = re.sub(target, repl, code, flags=re.DOTALL)

with open('ui/batch_mode.py', 'w') as f: f.write(code)

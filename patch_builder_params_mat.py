import re

with open('ui/batch_mode.py', 'r') as f: code = f.read()

target_mat = r"\*\*\{f'mat_\{k\}': getattr\(self, f'mat_\{k\}'\)\.get\(\) for k in \['ribs', 'main_spar', 'front_spar', 'rear_spar', 'plank', 'te', 'connectors', 'stringers', 'xbrace_wires', 'diag_spars', 'carbon_ribs', 'te_caps', 'rib_caps', 'film'\] if hasattr\(self, f'mat_\{k\}'\)\},"
repl_mat = r"            **{f'mat_{k}': self.pm.vars[f'mat_{k}'].get() for k in ['ribs', 'main_spar', 'front_spar', 'rear_spar', 'plank', 'te', 'connectors', 'stringers', 'xbrace_wires', 'diag_spars', 'carbon_ribs', 'te_caps', 'rib_caps', 'film'] if f'mat_{k}' in self.pm.vars},"

code = re.sub(target_mat, repl_mat, code, flags=re.DOTALL)

with open('ui/batch_mode.py', 'w') as f: f.write(code)

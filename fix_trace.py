import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

old_trace = """        for var in self.pm.vars.values():
            if hasattr(var, 'trace_add'):
                try: var.trace_add("write", lambda *args: self.update_preview_fast())
                except: pass"""

new_trace = """        for name, var in self.pm.vars.items():
            if hasattr(var, 'trace_add'):
                try:
                    if name in ['wing_span', 'rib_interval', 'joint_length']:
                        var.trace_add("write", lambda *args: [self.calculate_y_positions(), self.update_preview_fast()])
                    else:
                        var.trace_add("write", lambda *args: self.update_preview_fast())
                except: pass"""

text = text.replace(old_trace, new_trace)

with open('ui/batch_mode.py', 'w') as f:
    f.write(text)

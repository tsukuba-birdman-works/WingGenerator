import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

# 1. Revert calculate_y_positions limits
target1 = """            # Prevent crashes from extremely small intervals creating too many ribs
            if span <= 0 or interval < 1.0: self.y_positions, self.combo_rib['values'] = [], []; return
            if span / interval > 500: interval = span / 500.0  # Limit to 500 ribs maximum"""

replacement1 = """            if span <= 0 or interval <= 0: self.y_positions, self.combo_rib['values'] = [], []; return"""

if target1 in text:
    text = text.replace(target1, replacement1)
    print("Reverted limits in calculate_y_positions")
else:
    print("Target 1 not found")

# 2. Revert trace_add in _setup_bindings
target2 = """        for name, var in self.pm.vars.items():
            if hasattr(var, 'trace_add'):
                try:
                    if name in ['wing_span', 'rib_interval', 'joint_length']:
                        var.trace_add("write", lambda *args: [self.calculate_y_positions(), self.update_preview_fast()])
                    else:
                        var.trace_add("write", lambda *args: self.update_preview_fast())
                except: pass"""

replacement2 = """        for name, var in self.pm.vars.items():
            if hasattr(var, 'trace_add'):
                try:
                    var.trace_add("write", lambda *args: self.update_preview_fast())
                except: pass"""

if target2 in text:
    text = text.replace(target2, replacement2)
    print("Reverted trace_add in _setup_bindings")
else:
    print("Target 2 not found")

# 3. Add NotebookTabChanged binding in create_widgets
target3 = """        self.ui_builder.build_tabs(notebook, self.pm)

        # Append custom panels"""

replacement3 = """        self.ui_builder.build_tabs(notebook, self.pm)
        notebook.bind("<<NotebookTabChanged>>", lambda e: [self.calculate_y_positions(), self.update_preview_full()])

        # Append custom panels"""

if target3 in text:
    text = text.replace(target3, replacement3)
    print("Added NotebookTabChanged binding")
else:
    print("Target 3 not found")


with open('ui/batch_mode.py', 'w') as f:
    f.write(text)


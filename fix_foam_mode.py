import re

with open('ui/foam_mode.py', 'r') as f:
    content = f.read()

old_sig = "    def __init__(self, root, root_file=None, tip_file=None, block_width=None, wing_type=None):"
new_sig = """    def __init__(self, root, root_file=None, tip_file=None, block_width=None, wing_type=None,
                 target_type="Plank", target_thickness=0.0, cut_kerf=1.5, wire_dist=1000.0,
                 offset_x=0.0, offset_y=0.0, entry_x=0.0, entry_y=0.0, feedrate=100.0):"""
content = content.replace(old_sig, new_sig)

old_init = """        self.kerf_width = tk.DoubleVar(value=1.5)
        self.wire_dist = tk.DoubleVar(value=1000.0)
        self.block_width = tk.DoubleVar(value=block_width if block_width else 910.0)
        self.feedrate = tk.DoubleVar(value=100.0)

        self.offset_x = tk.DoubleVar(value=0.0)
        self.offset_y = tk.DoubleVar(value=0.0)
        self.entry_x = tk.DoubleVar(value=0.0)
        self.entry_y = tk.DoubleVar(value=0.0)"""

new_init = """        self.kerf_width = tk.DoubleVar(value=cut_kerf)
        self.wire_dist = tk.DoubleVar(value=wire_dist)
        self.block_width = tk.DoubleVar(value=block_width if block_width else 910.0)
        self.feedrate = tk.DoubleVar(value=feedrate)

        self.offset_x = tk.DoubleVar(value=offset_x)
        self.offset_y = tk.DoubleVar(value=offset_y)
        self.entry_x = tk.DoubleVar(value=entry_x)
        self.entry_y = tk.DoubleVar(value=entry_y)"""
content = content.replace(old_init, new_init)

with open('ui/foam_mode.py', 'w') as f:
    f.write(content)
print("fixed foam_mode.py signature")

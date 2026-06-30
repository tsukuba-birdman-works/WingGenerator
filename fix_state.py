import re

with open("ui/batch_mode.py", "r") as f:
    code = f.read()

# Add missing state variables to __init__
missing_state = """
        import tkinter as tk
        self.y_positions = []
        self.truss_angles_dict = {}
        self.current_rib_idx = tk.IntVar(value=0)
        self.local_truss_angle = tk.StringVar(value="60.0")
        self.last_warnings = []
        self.is_updating_ui = False
        self.preview_items = []
"""

# Insert right before self.create_widgets()
code = code.replace("        self.create_widgets()", missing_state + "        self.create_widgets()")

with open("ui/batch_mode.py", "w") as f:
    f.write(code)

print("Added missing state variables to batch_mode.py")

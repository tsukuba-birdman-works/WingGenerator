with open("ui/base_mode.py", "r") as f:
    code = f.read()

replacement = """        self.truss_tab_width = tk.StringVar(value="4.0")
        self.outer_tab_width = tk.StringVar(value="6.0")
        self.outer_tab_interval = tk.StringVar(value="100.0")
        self.tab_angle_deg = tk.StringVar(value="45.0")"""

code = code.replace('        self.truss_tab_width = tk.StringVar(value="4.0")', replacement)

with open("ui/base_mode.py", "w") as f:
    f.write(code)

print("Fixed variables")

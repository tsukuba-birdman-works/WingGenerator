import re

with open("ui/ui_builder.py", "r") as f:
    code = f.read()

patch2 = """
            elif wtype == 'bolt_triple':
                linked_x = p.get('linked_x')
                linked_y = p.get('linked_y')
                var_x = self.pm.vars.get(linked_x)
                var_y = self.pm.vars.get(linked_y)
                ttk.Label(parent_frame, text=label).grid(row=r, column=c, sticky=tk.E, padx=5, pady=2)
                f_bolt = ttk.Frame(parent_frame)
                f_bolt.grid(row=r, column=c+1, sticky=tk.W, padx=5, pady=2)
                ttk.Label(f_bolt, text="D:").pack(side=tk.LEFT)
                ttk.Entry(f_bolt, textvariable=var, width=5).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(f_bolt, text="X:").pack(side=tk.LEFT)
                if var_x: ttk.Entry(f_bolt, textvariable=var_x, width=5).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(f_bolt, text="Y:").pack(side=tk.LEFT)
                if var_y: ttk.Entry(f_bolt, textvariable=var_y, width=5).pack(side=tk.LEFT)
                c += 2
"""

code = code.replace("            elif wtype == 'range_pair':", patch2[1:] + "            elif wtype == 'range_pair':")

with open("ui/ui_builder.py", "w") as f:
    f.write(code)

print("ui_builder.py patched to support bolt_triple")

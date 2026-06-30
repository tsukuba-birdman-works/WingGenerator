import re

with open("ui/ui_builder.py", "r") as f:
    code = f.read()

patch = """
            if wtype == 'hidden':
                continue
            elif wtype == 'range_pair':
                linked_id = p.get('linked_id')
                linked_var = self.pm.vars.get(linked_id)
                ttk.Label(parent_frame, text=label).grid(row=r, column=c, sticky=tk.E, padx=5, pady=2)
                f_range = ttk.Frame(parent_frame)
                f_range.grid(row=r, column=c+1, sticky=tk.W, padx=5, pady=2)
                ttk.Entry(f_range, textvariable=var, width=6).pack(side=tk.LEFT)
                ttk.Label(f_range, text=" ~ ").pack(side=tk.LEFT)
                if linked_var:
                    ttk.Entry(f_range, textvariable=linked_var, width=6).pack(side=tk.LEFT)
                c += 2
"""

# Insert the patch right before the `elif wtype == 'entry':`
code = code.replace("            elif wtype == 'entry':", patch[1:] + "            elif wtype == 'entry':")

with open("ui/ui_builder.py", "w") as f:
    f.write(code)

print("ui_builder.py patched to support range_pair")

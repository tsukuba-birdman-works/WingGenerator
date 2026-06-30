with open("ui/ui_builder.py", "r") as f:
    code = f.read()

replacement = """
        for tab_name, groups in tabs_dict.items():
            if tab_name == "Unknown": continue
            f_tab_outer = ttk.Frame(notebook)
            notebook.add(f_tab_outer, text=tab_name)
            
            canvas = tk.Canvas(f_tab_outer, highlightthickness=0)
            scrollbar = ttk.Scrollbar(f_tab_outer, orient="vertical", command=canvas.yview)
            f_tab = ttk.Frame(canvas)

            f_tab.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0, 0), window=f_tab, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def _on_mousewheel(event, c=canvas):
                c.yview_scroll(int(-1*(event.delta/120)), "units")
            f_tab_outer.bind("<Enter>", lambda e, c=canvas, mw=_on_mousewheel: c.bind_all("<MouseWheel>", mw))
            f_tab_outer.bind("<Leave>", lambda e, c=canvas: c.unbind_all("<MouseWheel>"))

            obj.tabs_frames[tab_name] = f_tab
"""

import re
# Regex to replace the original f_tab creation block
code = re.sub(
    r"        for tab_name, groups in tabs_dict\.items\(\):\n\s*if tab_name == \"Unknown\": continue\n\s*f_tab = ttk\.Frame\(notebook\)\n\s*notebook\.add\(f_tab, text=tab_name\)\n\s*obj\.tabs_frames\[tab_name\] = f_tab",
    replacement.strip('\n'),
    code
)

with open("ui/ui_builder.py", "w") as f:
    f.write(code)

print("Scrollbars added!")

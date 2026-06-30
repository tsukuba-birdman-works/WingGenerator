import re

with open("ui/batch_mode.py", "r") as f:
    code = f.read()

# Delete the obsolete try/except lines for main_spar_tab_width and main_spar_tab_dist
code = re.sub(r"        try: ms_tab_w = self\.safe_float\(self\.main_spar_tab_width, 4\.0\)\n        except Exception: pass\n        try: ms_tab_d = self\.safe_float\(self\.main_spar_tab_dist, 10\.0\)\n        except Exception: pass\n", "", code)

with open("ui/batch_mode.py", "w") as f:
    f.write(code)

print("Batch mode cleaned.")

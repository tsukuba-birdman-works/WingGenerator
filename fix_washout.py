with open("core/engine.py", "r") as f:
    code = f.read()

from_str = "        washout = p['washout_tip'] * t"
to_str = """        washout_root = p.get('washout_root', 0.0)
        washout_tip = p.get('washout_tip', 0.0)
        washout_exp = p.get('washout_exp', 1.0)
        washout = washout_root + (washout_tip - washout_root) * (t ** washout_exp)"""

code = code.replace(from_str, to_str)

with open("core/engine.py", "w") as f:
    f.write(code)

print("Fixed washout calculation")

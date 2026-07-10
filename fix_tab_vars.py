import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

target1 = """        truss_tab_width = self.safe_float(self.truss_tab_width, 4.0)
        ms_tab_w, ms_tab_d = 4.0, 10.0"""

replacement1 = """        truss_tab_width = self.safe_float(self.truss_tab_width, 4.0)
        ms_tab_w = self.safe_float(self.main_spar_support_w, 4.0) if hasattr(self, 'main_spar_support_w') else 4.0
        ms_tab_d = self.safe_float(self.main_spar_support_h, 10.0) if hasattr(self, 'main_spar_support_h') else 10.0
        ms_tab_thick = self.safe_float(self.main_spar_support_thick, 3.0) if hasattr(self, 'main_spar_support_thick') else 3.0"""

target2 = """            'truss_tab_width': truss_tab_width,
            'main_spar_support_w': ms_tab_w,
            'main_spar_support_h': ms_tab_d,
            'main_spar_support_thick': 3.0,"""

replacement2 = """            'truss_tab_width': truss_tab_width,
            'main_spar_support_w': ms_tab_w,
            'main_spar_support_h': ms_tab_d,
            'main_spar_support_thick': ms_tab_thick,"""

if target1 in text and target2 in text:
    text = text.replace(target1, replacement1)
    text = text.replace(target2, replacement2)
    with open('ui/batch_mode.py', 'w') as f:
        f.write(text)
    print("Successfully patched batch_mode.py")
else:
    print("Target string not found!")


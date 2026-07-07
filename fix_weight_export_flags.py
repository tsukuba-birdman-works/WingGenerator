with open('ui/weight_window.py', 'r') as f:
    text = f.read()

old_code = """        try:
            # 1. Build geometry
            builder = Wing3DBuilder(self.engine, self.params)"""

new_code = """        try:
            # 1. Build geometry with all parts enabled for complete weight calculation
            calc_params = self.params.copy()
            for k in ['export_ribs', 'export_te', 'export_film', 'export_stringers', 
                      'export_te_caps', 'export_connectors', 'export_diag_spars', 
                      'export_xbrace_wires', 'export_joint_sleeves']:
                calc_params[k] = True
            builder = Wing3DBuilder(self.engine, calc_params)"""

text = text.replace(old_code, new_code)

with open('ui/weight_window.py', 'w') as f:
    f.write(text)

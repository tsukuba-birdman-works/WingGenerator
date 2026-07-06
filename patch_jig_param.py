import re
with open('ui/batch_mode.py', 'r') as f: code = f.read()

replacement = """            'tab_exclusion_stringer': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_stringer', tk.StringVar(value="10.0")), 10.0),
            'tab_exclusion_le_te': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_le_te', tk.StringVar(value="30.0")), 30.0),
            'jig_y_positions': self.pm.vars['jig_y_positions'].get() if 'jig_y_positions' in self.pm.vars else '',"""

code = code.replace(
    """            'tab_exclusion_stringer': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_stringer', tk.StringVar(value="10.0")), 10.0),
            'tab_exclusion_le_te': getattr(self, 'safe_float')(getattr(self, 'tab_exclusion_le_te', tk.StringVar(value="30.0")), 30.0),
            'jig_y_positions': getattr(self, 'jig_y_positions').get() if hasattr(self, 'jig_y_positions') else '',""",
    replacement
)

with open('ui/batch_mode.py', 'w') as f: f.write(code)

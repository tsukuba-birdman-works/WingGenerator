import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

# Fix calculate_y_positions
target_calc = """            span, interval, joint = self.safe_float(self.wing_span), self.safe_float(self.rib_interval), self.safe_float(self.joint_length)
            if span <= 0 or interval <= 0: self.y_positions, self.combo_rib['values'] = [], []; return"""

replacement_calc = """            span, interval, joint = self.safe_float(self.wing_span), self.safe_float(self.rib_interval), self.safe_float(self.joint_length)
            # Prevent crashes from extremely small intervals creating too many ribs
            if span <= 0 or interval < 1.0: self.y_positions, self.combo_rib['values'] = [], []; return
            if span / interval > 500: interval = span / 500.0  # Limit to 500 ribs maximum"""

if target_calc in text:
    text = text.replace(target_calc, replacement_calc)
    print("Patched calculate_y_positions in batch_mode.py")

with open('ui/batch_mode.py', 'w') as f:
    f.write(text)


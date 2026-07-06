import re

with open('foam_nester.py', 'r') as f:
    code = f.read()

code = code.replace("self.update_plot()", "self.update_plot(preserve_limits=True)")

# But wait, we want load_gcode, remove_selected, setup_ui to NOT preserve limits!
# Let's fix those specifically to use preserve_limits=False
code = code.replace("self.update_plot(preserve_limits=True)", "self.update_plot()") # Undo

# Now apply carefully:
code = re.sub(r'(def on_motion.*?dx = event\.xdata - self\.drag_start_x.*?self\.drag_start_y = event\.ydata\s*)self\.update_plot\(\)', r'\1self.update_plot(preserve_limits=True)', code, flags=re.DOTALL)
code = re.sub(r'(def transform.*?part\.flip_x = not part\.flip_x\s*)self\.update_plot\(\)', r'\1self.update_plot(preserve_limits=True)', code, flags=re.DOTALL)
code = re.sub(r'(def auto_minimize_thickness.*?self\.angle_var\.set\(best_angle\)\s*)self\.update_plot\(\)', r'\1self.update_plot(preserve_limits=True)', code, flags=re.DOTALL)
code = re.sub(r'(def on_angle_change.*?self\.parts\[self\.selected_idx\]\.angle_deg = float\(val\)\s*)self\.update_plot\(\)', r'\1self.update_plot(preserve_limits=True)', code, flags=re.DOTALL)

with open('foam_nester.py', 'w') as f:
    f.write(code)
print("Updated limits")

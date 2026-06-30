with open("ui/batch_mode.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "not self.cr_root_in_te.get():" in line:
        continue  # Remove this entirely, as inner TE is always enabled
    elif "not self.cr_tip_in_te.get():" in line:
        continue  # Remove this entirely, as inner TE is always enabled
    
    # Also update the getattr fallback to ensure safe loading
    if "'te': getattr(self, 'cr_root_in_te'" in line:
        line = line.replace("getattr(self, 'cr_root_in_te', tk.BooleanVar(value=False)).get()", "True")
    if "'te': getattr(self, 'cr_tip_in_te'" in line:
        line = line.replace("getattr(self, 'cr_tip_in_te', tk.BooleanVar(value=False)).get()", "True")
        
    new_lines.append(line)

with open("ui/batch_mode.py", "w") as f:
    f.writelines(new_lines)

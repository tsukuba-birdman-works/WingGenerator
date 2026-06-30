with open("ui/base_mode.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "if hasattr(self, 'pm'):" in line:
        skip = True
        continue
    if skip and "self.pm.obj.tabs_frames['CNC'] = parent_frame" in line:
        skip = False
        continue
        
    new_lines.append(line)
    
    if "parent_frame = ttk.Frame(canvas)" in line:
        new_lines.append("        if hasattr(self, 'pm'):\n")
        new_lines.append("            self.pm.obj.tabs_frames['CNC'] = parent_frame\n")

with open("ui/base_mode.py", "w") as f:
    f.writelines(new_lines)

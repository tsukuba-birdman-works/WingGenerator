with open("backup_batch_mode.py", "r") as f:
    lines = f.readlines()

def get_block(start_str, end_str):
    start = -1
    end = -1
    for i, line in enumerate(lines):
        if start_str in line and start == -1:
            start = i
        if end_str in line and start != -1 and end == -1:
            end = i
            break
    if start != -1 and end != -1:
        return "".join(lines[start:end])
    return ""

print("XBRACE:")
print(get_block("lf_xbr_manual = ttk.LabelFrame(left_panel_rib, text=\"X-Brace Manual Setup\")", "lf_carbon = ttk.LabelFrame(right_panel_rib, text=\"Carbon Sandwich Ribs\")"))

print("CARBON:")
print(get_block("lf_carbon = ttk.LabelFrame(right_panel_rib, text=\"Carbon Sandwich Ribs\")", "# --- Tab 4: Plank & TE ---"))

print("PREVIEW:")
print(get_block("lf_preview = ttk.LabelFrame(self.scroll_content, text=\"Rib Preview\")", "def browse_file(self, var, is_dxf=False):"))


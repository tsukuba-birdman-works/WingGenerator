with open('core/engine.py', 'r') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if l.startswith("        if is_new_doc:") and lines[i+1].startswith("    def generate_jig_at_y("):
        lines.insert(i+1, "            doc.saveas(filepath)\n\n")
        break

with open('core/engine.py', 'w') as f:
    f.writelines(lines)

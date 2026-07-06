with open('core/engine.py', 'r') as f:
    lines = f.readlines()

out_lines = []
in_jig = False
jig_count = 0

for i, l in enumerate(lines):
    if l.startswith("    def generate_jig_at_y("):
        jig_count += 1
        if jig_count > 1:
            in_jig = True
        else:
            in_jig = False
    
    if in_jig:
        # Detect end of jig function: either a new def, or eof
        if (l.startswith("    def ") and not l.startswith("    def generate_jig_at_y(")) or l.startswith("class ") or l.startswith("    import"):
            in_jig = False
            
    if not in_jig:
        # if this line was previously marked in_jig but is now false, we print it
        out_lines.append(l)

with open('core/engine.py', 'w') as f:
    f.writelines(out_lines)

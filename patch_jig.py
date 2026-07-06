import re

with open('/home/akihito-kasai/.gemini/antigravity/brain/44a6c132-cd64-40bc-8e11-0505fb90f8d0/scratch/jig_logic.py', 'r') as f:
    jig_code = f.read()

# Fix the syntax error
jig_code = jig_code.replace("    pts.append((te_support_star\n", "")

# Append to engine.py
with open('core/engine.py', 'a') as f:
    f.write("\n")
    f.write(jig_code)
    f.write("\n")

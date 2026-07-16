import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

pattern = r"                    print\(f\"DEBUG: TE_Skin base faces=\{len\(m\.faces\)\}, is_watertight=\{m\.is_watertight\}, volume=\{m\.volume\}\"\)\n                    print\(f\"DEBUG: extended_subs count=\{len\(extended_subs\)\}\"\)\n                    for i, sub in enumerate\(extended_subs\):\n                        print\(f\"DEBUG: sub \{i\} faces=\{len\(sub\.faces\)\}, is_watertight=\{sub\.is_watertight\}\"\)\n\n                    try:\n                        m = Wing3DExporter\.blender_difference\(m, extended_subs\)\n                        print\(f\"DEBUG: TE_Skin output faces=\{len\(m\.faces\) if m else 'None'\}\"\)\n                    except Exception as e:\n                        print\(\"DEBUG: blender_difference failed:\", e\)\n                        m = None"

replace = """                    m = Wing3DExporter.blender_difference(m, extended_subs)"""

if re.search(pattern, content):
    content = re.sub(pattern, replace, content)
    with open('core/export_3d.py', 'w') as f:
        f.write(content)
    print("Debug removed.")
else:
    print("Pattern not found!")

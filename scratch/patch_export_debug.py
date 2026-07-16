import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

# Inject print statements right before blender_difference
pattern = r"                    m = Wing3DExporter\.blender_difference\(m, extended_subs\)"
replace = """                    print(f"DEBUG: TE_Skin base faces={len(m.faces)}, is_watertight={m.is_watertight}, volume={m.volume}")
                    print(f"DEBUG: extended_subs count={len(extended_subs)}")
                    for i, sub in enumerate(extended_subs):
                        print(f"DEBUG: sub {i} faces={len(sub.faces)}, is_watertight={sub.is_watertight}")
                    
                    try:
                        m = Wing3DExporter.blender_difference(m, extended_subs)
                        print(f"DEBUG: TE_Skin output faces={len(m.faces) if m else 'None'}")
                    except Exception as e:
                        print("DEBUG: blender_difference failed:", e)
                        m = None"""

content = re.sub(pattern, replace, content)

with open('core/export_3d.py', 'w') as f:
    f.write(content)
print("Patched for debug.")

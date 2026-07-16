import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

pattern = r"        finally:\n            # Clean up temp files"
replace = """        finally:
            if res_mesh is None or len(res_mesh.faces) == 0:
                print(f"DEBUG: KEEPING TEMP FILES FOR {id(base_mesh)}")
                return res_mesh
            # Clean up temp files"""

content = re.sub(pattern, replace, content)

with open('core/export_3d.py', 'w') as f:
    f.write(content)
print("Patched.")

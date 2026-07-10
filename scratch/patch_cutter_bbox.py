import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

search = """                                minx, miny, maxx, maxy = p_simp.bounds
                                bbox = box(minx, -9999, maxx, 9999)
                                inflated_p = inflated_p.intersection(bbox)"""

replace = """                                minx, miny, maxx, maxy = p_simp.bounds
                                # 前縁側(minx)だけを1mm長くして、後縁ブロックの前縁面と完全に一致（Coplanar）するのを防ぐ
                                bbox = box(minx - 2.0, -9999, maxx, 9999)
                                inflated_p = inflated_p.intersection(bbox)"""

if search in content:
    content = content.replace(search, replace)
    with open('core/export_3d.py', 'w') as f:
        f.write(content)
    print("Patched cutter bbox!")
else:
    print("Could not find search block")

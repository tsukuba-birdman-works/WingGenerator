import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

search = """                        mesh = trimesh.creation.extrude_polygon(p_simp, height=thickness)
                        swap_yz = np.array([
                            [1, 0, 0, 0],
                            [0, 0, 1, 0],
                            [0, 1, 0, 0],
                            [0, 0, 0, 1]
                        ])
                        mesh.apply_transform(swap_yz)
                        mesh.apply_translation([0, y_global, 0])
                        meshes.append((mesh, mat_key))"""

replace = """                        mesh = trimesh.creation.extrude_polygon(p_simp, height=thickness)
                        swap_yz = np.array([
                            [1, 0, 0, 0],
                            [0, 0, 1, 0],
                            [0, 1, 0, 0],
                            [0, 0, 0, 1]
                        ])
                        mesh.apply_transform(swap_yz)
                        mesh.apply_translation([0, y_global, 0])
                        meshes.append((mesh, mat_key))
                        
                        if mat_key in ['Ribs', 'CarbonRibs']:
                            try:
                                from shapely.geometry import box
                                inflated_p = p_simp.buffer(1.0)
                                minx, miny, maxx, maxy = p_simp.bounds
                                bbox = box(minx, -9999, maxx, 9999)
                                inflated_p = inflated_p.intersection(bbox)
                                
                                cutter_mesh = trimesh.creation.extrude_polygon(inflated_p, height=thickness)
                                cutter_mesh.apply_transform(swap_yz)
                                cutter_mesh.apply_translation([0, y_global, 0])
                                meshes.append((cutter_mesh, mat_key + "_Cutter"))
                            except Exception as e:
                                print("Cutter extrude error:", e)"""

if search in content:
    content = content.replace(search, replace)
    with open('core/export_3d.py', 'w') as f:
        f.write(content)
    print("Patched cutter generation!")
else:
    print("Could not find search block")

import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

# 1. Remove the sub_up / sub_down mess and restore just scaling in Y
pattern_mess = r"                            if t > 1e-5:.*?                            extended_subs\.extend\(\[sub_ext, sub_up, sub_down\]\)"
replace_clean = """                            if t > 1e-5:
                                scale = (t + 2.0) / t
                                t1 = np.eye(4)
                                t1[1, 3] = -y_center
                                s_mat = np.eye(4)
                                s_mat[1, 1] = scale # Y方向のみ拡大
                                t2 = np.eye(4)
                                t2[1, 3] = y_center
                                mat = t2 @ s_mat @ t1
                                sub_ext.apply_transform(mat)
                            extended_subs.append(sub_ext)"""

content = re.sub(pattern_mess, replace_clean, content, flags=re.DOTALL)

# 2. Add Ribs_Cutter generation logic if not present
search_extrude = """                        mesh.apply_transform(swap_yz)
                        mesh.apply_translation([0, y_global, 0])
                        meshes.append((mesh, mat_key))
                    except Exception as e: last_err = str(e); print("Extrude Error:", e)"""

replace_extrude = """                        mesh.apply_transform(swap_yz)
                        mesh.apply_translation([0, y_global, 0])
                        meshes.append((mesh, mat_key))

                        if mat_key in ['Ribs', 'CarbonRibs']:
                            try:
                                from shapely.geometry import box
                                inflated_p = p_simp.buffer(1.0)
                                minx, miny, maxx, maxy = p_simp.bounds
                                # 前縁側(minx)を2mm伸ばして後縁ブロックとCoplanarになるのを防ぐ。後縁側(maxx)はそのまま。
                                bbox = box(minx - 2.0, -9999, maxx, 9999)
                                inflated_p = inflated_p.intersection(bbox)
                                cutter_mesh = trimesh.creation.extrude_polygon(inflated_p, height=thickness)
                                cutter_mesh.apply_transform(swap_yz)
                                cutter_mesh.apply_translation([0, y_global, 0])
                                meshes.append((cutter_mesh, mat_key + "_Cutter"))
                            except Exception as e:
                                print("Cutter extrude error:", e)

                    except Exception as e: last_err = str(e); print("Extrude Error:", e)"""

if search_extrude in content:
    content = content.replace(search_extrude, replace_extrude)

# 3. Use Ribs_Cutter in rib_sub_meshes
search_rib_sub = """        rib_sub_meshes = ribs_m_list + carbon_m_list
        for name, m in other_meshes.items():"""

replace_rib_sub = """        cutter_m_list = [m for m, k in meshes if k in ['Ribs_Cutter', 'CarbonRibs_Cutter']]
        rib_sub_meshes = cutter_m_list if cutter_m_list else ribs_m_list + carbon_m_list
        for name, m in other_meshes.items():"""

if search_rib_sub in content:
    content = content.replace(search_rib_sub, replace_rib_sub)

with open('core/export_3d.py', 'w') as f:
    f.write(content)

print("Applied TRUE FIX to export_3d.py!")

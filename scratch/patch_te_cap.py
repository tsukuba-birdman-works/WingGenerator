import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

search = """                        except Exception as e:
                            print("Scaling sub error:", e)
                            extended_subs.append(sub)"""

replace = """                        except Exception as e:
                            print("Scaling sub error:", e)
                            extended_subs.append(sub)
                    
                    # 後縁キャップもブーリアンでくり抜く
                    for cap_name, cap_mesh in other_meshes.items():
                        if cap_name.startswith('TE_Cap') and cap_mesh is not None:
                            # 表面の完全一致によるブーリアンエラーを防ぐため、少しだけ法線方向（外側）に膨らませたカッターを使うと良いが
                            # まずはそのまま引き算に追加する
                            cap_cutter = cap_mesh.copy()
                            # 少し上下（Z）に大きくして表面を確実に突き抜けるようにする
                            # が、TE_Capは斜めなので単純Zスケールは危険。とりあえずそのまま追加。
                            extended_subs.append(cap_cutter)"""

if search in content:
    content = content.replace(search, replace)
    with open('core/export_3d.py', 'w') as f:
        f.write(content)
    print("Patched TE Cap subtraction!")
else:
    print("Could not find search block")

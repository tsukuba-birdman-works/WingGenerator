import sys

with open('/home/akihito-kasai/Desktop/tbw/Ribgenerator/core/export_3d.py', 'r') as f:
    content = f.read()

old_code = """                    min_dist_sum = float('inf')
                    best_roll = 0
                    for j in range(len(c_res)-1):
                        shifted = np.roll(c_res[:-1], -j, axis=0)
                        dist_sum = np.sum(np.linalg.norm(prev_c[:-1] - shifted, axis=1))
                        if dist_sum < min_dist_sum:
                            min_dist_sum, best_roll = dist_sum, j
                    shifted_core = np.roll(c_res[:-1], -best_roll, axis=0)
                    c_res = np.vstack([shifted_core, shifted_core[0]])"""

new_code = """                    min_dist_sum = float('inf')
                    best_roll = 0
                    best_rev = False
                    
                    # Check forward
                    for j in range(len(c_res)-1):
                        shifted = np.roll(c_res[:-1], -j, axis=0)
                        dist_sum = np.sum(np.linalg.norm(prev_c[:-1] - shifted, axis=1))
                        if dist_sum < min_dist_sum:
                            min_dist_sum, best_roll, best_rev = dist_sum, j, False
                            
                    # Check reversed
                    c_rev = c_res[::-1]
                    for j in range(len(c_rev)-1):
                        shifted = np.roll(c_rev[:-1], -j, axis=0)
                        dist_sum = np.sum(np.linalg.norm(prev_c[:-1] - shifted, axis=1))
                        if dist_sum < min_dist_sum:
                            min_dist_sum, best_roll, best_rev = dist_sum, j, True
                            
                    core_to_use = c_rev[:-1] if best_rev else c_res[:-1]
                    shifted_core = np.roll(core_to_use, -best_roll, axis=0)
                    c_res = np.vstack([shifted_core, shifted_core[0]])"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('/home/akihito-kasai/Desktop/tbw/Ribgenerator/core/export_3d.py', 'w') as f:
        f.write(content)
    print("Replaced alignment code successfully.")
else:
    print("Could not find old_code in export_3d.py")


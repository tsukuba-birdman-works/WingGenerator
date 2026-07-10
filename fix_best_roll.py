import sys

filepath = '/home/akihito-kasai/Desktop/tbw/Ribgenerator/core/export_3d.py'
with open(filepath, 'r') as f:
    content = f.read()

old_str = """                if i > 0:
                    prev_c = aligned_curves[-1]
                    min_dist_sum = float('inf')
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

new_str = """                if i > 0:
                    prev_c = aligned_curves[-1]
                    min_dist_sum = float('inf')
                    best_roll = 0
                    best_rev = False

                    # If topo_match is true, the corners are ALREADY perfectly aligned at indices 0, N, 2N...
                    # Shifting by any j != 0 would destroy this alignment!
                    roll_range = [0] if topo_match else range(len(c_res)-1)

                    # Check forward
                    for j in roll_range:
                        shifted = np.roll(c_res[:-1], -j, axis=0)
                        dist_sum = np.sum(np.linalg.norm(prev_c[:-1] - shifted, axis=1))
                        if dist_sum < min_dist_sum:
                            min_dist_sum, best_roll, best_rev = dist_sum, j, False

                    # Check reversed
                    # Reversing preserves the corner indices (e.g., 0 stays 0, corner at 10 moves to 5 which is the OTHER corner)
                    c_rev = c_res[::-1]
                    for j in roll_range:
                        shifted = np.roll(c_rev[:-1], -j, axis=0)
                        dist_sum = np.sum(np.linalg.norm(prev_c[:-1] - shifted, axis=1))
                        if dist_sum < min_dist_sum:
                            min_dist_sum, best_roll, best_rev = dist_sum, j, True

                    core_to_use = c_rev[:-1] if best_rev else c_res[:-1]
                    shifted_core = np.roll(core_to_use, -best_roll, axis=0)
                    c_res = np.vstack([shifted_core, shifted_core[0]])"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Fixed!")
else:
    print("Not found!")

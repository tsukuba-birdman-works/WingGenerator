import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

# 1. We need to respect native arrays
search_resample = """            for i, c in enumerate(valid_curves):
                if all_same_len and max_len <= 10:
                    c_res = c
                else:
                    c_res = resample_closed(c, max_len)

                if np.linalg.norm(c_res[0] - c_res[-1]) > 1e-5:
                    c_res = np.vstack([c_res, c_res[0]])

                if i > 0:
                    prev_c = aligned_curves[-1]
                    min_dist_sum = float('inf')
                    best_roll = 0
                    for j in range(len(c_res)-1):
                        shifted = np.roll(c_res[:-1], -j, axis=0)
                        dist_sum = np.sum(np.linalg.norm(prev_c[:-1] - shifted, axis=1))
                        if dist_sum < min_dist_sum:
                            min_dist_sum, best_roll = dist_sum, j
                    shifted_core = np.roll(c_res[:-1], -best_roll, axis=0)
                    c_res = np.vstack([shifted_core, shifted_core[0]])"""

replace_resample = """            for i, c in enumerate(valid_curves):
                if all_same_len:
                    c_res = c
                else:
                    c_res = resample_closed(c, max_len)

                if np.linalg.norm(c_res[0] - c_res[-1]) > 1e-5:
                    c_res = np.vstack([c_res, c_res[0]])

                if i > 0 and not all_same_len:
                    prev_c = aligned_curves[-1]
                    min_dist_sum = float('inf')
                    best_roll = 0
                    for j in range(len(c_res)-1):
                        shifted = np.roll(c_res[:-1], -j, axis=0)
                        dist_sum = np.sum(np.linalg.norm(prev_c[:-1] - shifted, axis=1))
                        if dist_sum < min_dist_sum:
                            min_dist_sum, best_roll = dist_sum, j
                    shifted_core = np.roll(c_res[:-1], -best_roll, axis=0)
                    c_res = np.vstack([shifted_core, shifted_core[0]])"""

if search_resample in content:
    content = content.replace(search_resample, replace_resample)
    with open('core/export_3d.py', 'w') as f:
        f.write(content)
    print("Patched export_3d.py (native arrays respected)")
else:
    print("Could not find resample block")

import numpy as np

def align_curves(c_curves):
    aligned_curves = []
    for i, c_res in enumerate(c_curves):
        if np.linalg.norm(c_res[0] - c_res[-1]) > 1e-5:
            c_res = np.vstack([c_res, c_res[0]])
            
        if i > 0:
            prev_c = aligned_curves[-1]
            prev_cent = np.mean(prev_c[:-1], axis=0)
            curr_cent = np.mean(c_res[:-1], axis=0)
            prev_local = prev_c[:-1] - prev_cent
            curr_local = c_res[:-1] - curr_cent
            
            min_dist_sum = float('inf')
            best_roll = 0
            for j in range(len(curr_local)):
                shifted = np.roll(curr_local, -j, axis=0)
                dist_sum = np.sum(np.linalg.norm(prev_local - shifted, axis=1))
                if dist_sum < min_dist_sum:
                    min_dist_sum, best_roll = dist_sum, j
            print(f"Curve {i} aligned with roll {best_roll}")
            shifted_core = np.roll(c_res[:-1], -best_roll, axis=0)
            c_res = np.vstack([shifted_core, shifted_core[0]])
            
        aligned_curves.append(c_res)
    return aligned_curves

r1 = np.array([[0, 0, 0], [30, 0, 0], [30, 0, 3], [0, 0, 3]])
r2 = np.array([[100, 10, 0], [110, 10, 0], [110, 10, 1], [100, 10, 1]]) # highly swept and shrunk
r3 = np.array([[200, 20, 0], [205, 20, 0], [205, 20, 0.5], [200, 20, 0.5]])

print("Test with 4 points:")
align_curves([r1, r2, r3])

# Resample to 50 points
from core.export_3d import Wing3DExporter
r1_res = Wing3DExporter.resample_closed(r1, 50)
r2_res = Wing3DExporter.resample_closed(r2, 50)
r3_res = Wing3DExporter.resample_closed(r3, 50)
print("\nTest with 50 points:")
align_curves([r1_res, r2_res, r3_res])


import sys
import numpy as np

# Let's test the idea
def get_te_corners_with_roles(c):
    idx_tip = np.argmax(c[:, 0])
    min_x = np.min(c[:, 0])
    front_indices = np.where(c[:, 0] < min_x + 2.0)[0]
    if len(front_indices) == 0: front_indices = np.where(c[:, 0] < min_x + 5.0)[0]
    idx_top = front_indices[np.argmax(c[front_indices, 2])]
    idx_bot = front_indices[np.argmin(c[front_indices, 2])]
    return idx_tip, idx_top, idx_bot

# We can modify get_corners to return the primary corner index as the first element!

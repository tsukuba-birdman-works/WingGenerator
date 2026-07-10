import numpy as np

def generate_te_native(u_x_mod, u_y_mod, l_x_mod, l_y_mod, te_cut, num_pts=25):
    # u_x_mod goes from LE to TE. We want TE to LE.
    u_pts_rev = np.column_stack((u_x_mod[::-1], u_y_mod[::-1]))
    l_pts_rev = np.column_stack((l_x_mod[::-1], l_y_mod[::-1]))
    
    # Calculate distance along curves
    dist_u = np.zeros(len(u_pts_rev))
    dist_u[1:] = np.cumsum(np.linalg.norm(np.diff(u_pts_rev, axis=0), axis=1))
    
    dist_l = np.zeros(len(l_pts_rev))
    dist_l[1:] = np.cumsum(np.linalg.norm(np.diff(l_pts_rev, axis=0), axis=1))
    
    # We want from dist=0 (TE) to dist=te_cut
    # Interpolate exactly num_pts
    targets_u = np.linspace(0, te_cut, num_pts)
    targets_l = np.linspace(te_cut, 0, num_pts)
    
    te_u_x = np.interp(targets_u, dist_u, u_pts_rev[:, 0])
    te_u_y = np.interp(targets_u, dist_u, u_pts_rev[:, 1])
    
    te_l_x = np.interp(targets_l, dist_l, l_pts_rev[:, 0])
    te_l_y = np.interp(targets_l, dist_l, l_pts_rev[:, 1])
    
    # Combine (TE -> cut -> TE)
    te_coords = np.column_stack((
        np.concatenate((te_u_x, te_l_x[1:])),
        np.concatenate((te_u_y, te_l_y[1:]))
    ))
    return te_coords
    
print("Native TE generation defined.")

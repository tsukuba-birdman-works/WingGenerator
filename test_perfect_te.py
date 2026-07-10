import numpy as np
from scipy.interpolate import interp1d

def generate_perfect_te(u_x, u_y, l_x, l_y, te_cut, chord, n_pts=20):
    # u_x, u_y go from LE (0) to TE (chord)
    # te_cut is measured from TE (e.g. 10mm). So start X is chord - te_cut.
    x_start = chord - te_cut
    x_end = chord
    
    # We want to interpolate exactly n_pts from x_start to x_end
    x_target = np.linspace(x_start, x_end, n_pts)
    
    # Interpolate upper surface
    f_u = interp1d(u_x, u_y, kind='linear', fill_value='extrapolate')
    u_y_target = f_u(x_target)
    
    # Interpolate lower surface
    f_l = interp1d(l_x, l_y, kind='linear', fill_value='extrapolate')
    l_y_target = f_l(x_target)
    
    # Assemble polygon: upper from start to end, lower from end to start
    te_x = np.concatenate((x_target, x_target[::-1]))
    te_y = np.concatenate((u_y_target, l_y_target[::-1]))
    
    return np.column_stack((te_x, te_y))

# Let's see if this matches what the user wants!

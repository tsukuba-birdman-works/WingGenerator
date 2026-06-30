import numpy as np

def test_preserve():
    # Square with perimeter 4
    pts = np.array([[0,0], [1,0], [1,1], [0,1], [0,0]])
    dist = np.array([0, 1, 2, 3, 4])
    
    n = 10
    target = np.linspace(0, 4, n)
    print("Original target:", target)
    
    # Corners are at dist 1, 2, 3
    corners = [1, 2, 3]
    for c_dist in corners:
        idx = np.argmin(np.abs(target - c_dist))
        target[idx] = c_dist
        
    print("Adjusted target:", target)
    print("Is monotonic?", np.all(np.diff(target) >= 0))

test_preserve()

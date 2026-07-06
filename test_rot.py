import numpy as np
import ezdxf

# Create a dummy DXF file
doc = ezdxf.new('R2010')
msp = doc.modelspace()
# A box of length 100, height 10, rotated by 15 degrees
points = [(-50, -5), (50, -5), (50, 5), (-50, 5)]
rad = np.radians(15)
R = np.array([[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]])
rotated_pts = np.dot(points, R.T)
for i in range(4):
    msp.add_line(rotated_pts[i], rotated_pts[(i+1)%4])
doc.saveas("dummy.dxf")

# Run find_optimal_rotation
from core.foam_engine import FoamCutterEngine
engine = FoamCutterEngine()
angle = engine.find_optimal_rotation("dummy.dxf", "dummy.dxf")
print(f"Optimal angle returned: {angle}")

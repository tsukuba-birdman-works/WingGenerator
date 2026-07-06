import numpy as np
from core.foam_engine import FoamCutterEngine
import ezdxf

doc = ezdxf.new('R2010')
msp = doc.modelspace()
# cambered airfoil approximation (shifted)
pts = []
for x in range(101):
    y = 5 * np.sin(x / 100.0 * np.pi) # camber
    pts.append((x, y + 2)) # top surface
for x in range(100, -1, -1):
    y = 5 * np.sin(x / 100.0 * np.pi)
    pts.append((x, y - 2)) # bottom surface
for i in range(len(pts)-1):
    msp.add_line(pts[i], pts[i+1])
doc.saveas('camber.dxf')

engine = FoamCutterEngine()
angle = engine.find_optimal_rotation('camber.dxf', 'camber.dxf')
print(f"Optimal angle: {angle}")

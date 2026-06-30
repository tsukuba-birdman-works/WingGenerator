import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core.engine import RibGeneratorEngine
import ezdxf

engine = RibGeneratorEngine()
engine.update_parameters(
    y_positions=[0.0, 100.0],
    chords=[200.0, 200.0],
    twists=[0.0, 0.0],
    te_cut=20.0,
    export_te=True
)
engine.generate_ribs()
res = engine.rib_results[0]
te_part = res.te_part_coords

doc = ezdxf.new('R2010')
msp = doc.modelspace()
msp.add_lwpolyline(te_part, close=True)
doc.saveas('test_te.dxf')
print("DXF saved to test_te.dxf")

# Print the points near the cut
print("Number of points:", len(te_part))
for pt in te_part:
    if pt[0] > 170: # near the TE cut
        print(pt)

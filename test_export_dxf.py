import ezdxf
from core.engine import RibGeneratorEngine
import numpy as np

engine = RibGeneratorEngine()
poly = np.array([[0,0], [10,0], [10,5], [0,5], [0,0]])
engine.export_single_poly_dxf("test_export_temp.dxf", poly, (0,0))
print("DXF Exported successfully")

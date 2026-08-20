import sys
sys.path.append('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
from core.fea_engine import RibFEAEngine
from shapely.geometry import Polygon

poly = Polygon([(0,0), (100,0), (50,50)])
eng = RibFEAEngine('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
try:
    eng.generate_fea_model(
        polygon=poly,
        spar_centers=[(20, 10), (80, 10)],
        chord=100.0,
        material_props={'E': 15.0, 'nu': 0.3},
        thickness=5.0,
        plank_poly=None,
        plank_params={'enabled': False}
    )
    print("FEA generation successful")
except Exception as e:
    import traceback
    traceback.print_exc()

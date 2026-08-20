import sys
sys.path.append('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
from core.fea_engine import RibFEAEngine
from core.rib_builder import RibBuilder

builder = RibBuilder()
res = builder.build(chord=1000.0)

eng = RibFEAEngine('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
eng.generate_fea_model(
    polygon=res.final_rib_mod,
    spar_centers=[res.c_m, res.c_r],
    chord=1000.0,
    material_props={'E': 15.0, 'nu': 0.3},
    thickness=5.0,
    plank_poly=None,
    plank_params={'enabled': False}
)

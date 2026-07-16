import json
from core.engine import RibGeneratorEngine

with open('preset/test.json', 'r') as f:
    p = json.load(f)

# Mock some UI calculated values
p['y_positions'] = [0, 50, 100]
p['export_te'] = True
p['wing_type'] = "Right"

engine = RibGeneratorEngine()
try:
    res = engine.export_3d_data(p)
    scene_rib_data, plank_curves, te_curves, stringer_curves, film_curves, te_cap_curves, main_spar_centers, rear_spar_centers, front_spar_centers = res
    print("TE Curves count:", len(te_curves) if te_curves else "None")
    
    from core.export_3d import Wing3DExporter
    te_skin = Wing3DExporter.generate_lofted_surface(te_curves)
    print("TE Skin faces:", len(te_skin.faces) if te_skin else "None")
except Exception as e:
    import traceback
    traceback.print_exc()


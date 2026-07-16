import json
import traceback
from core.export_3d import Wing3DBuilder
from core.engine import RibGeneratorEngine

def run():
    with open('preset/test.json', 'r') as f:
        data = json.load(f)
        
    engine = RibGeneratorEngine()
    
    # Mock y_positions
    data['y_positions'] = [0, 50, 100]
    data['export_te'] = True
    data['export_ribs'] = True
    data['export_carbon_ribs'] = True
    data['export_te_caps'] = True
    data['export_front_spar'] = True
    data['export_rear_spar'] = True
    data['export_plank'] = True
    data['export_film'] = True
    data['export_stringers'] = True
    data['export_connectors'] = True
    data['export_diag_spars'] = True
    data['wing_type'] = "Right"
    data['stringers'] = []
    
    builder = Wing3DBuilder(engine, data)
    
    try:
        scene, analytics = builder.build_geometry()
        print("Exported scene meshes:", list(scene.keys()))
        if "TE_Skin" in scene:
            print("TE_Skin faces:", len(scene["TE_Skin"].faces))
        else:
            print("TE_Skin NOT IN SCENE!")
            
    except Exception as e:
        print("Crash:", e)
        traceback.print_exc()

run()

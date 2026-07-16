import tkinter as tk
from ui.single_mode import RibGeneratorGUI_Single
from core.export_3d import Wing3DExporter

root = tk.Tk()
app = RibGeneratorGUI_Single(root)
root.update()

# Mock file loading
def load_mock(filepath):
    import json
    with open(filepath, 'r') as f:
        data = json.load(f)
    app.pm.obj.data = data
    app.pm.obj._update_ui_from_data()

app.pm.obj.load_preset = load_mock
app.pm.obj.load_preset('preset/test.json')

p = app.get_params()
p['export_te'] = True

scene_rib_data, plank_curves, te_curves, stringer_curves, film_curves, te_cap_curves, main_spar_centers, rear_spar_centers, front_spar_centers = app.engine.export_3d_data(p)

print("te_curves count:", len(te_curves))
for i, c in enumerate(te_curves):
    print(f"Curve {i} points:", len(c) if c is not None else 0)

import trimesh
other_meshes = {}
other_meshes["TE_Skin"] = Wing3DExporter.generate_lofted_surface(te_curves)
print("TE_Skin initially:", "OK" if other_meshes["TE_Skin"] else "None")

ribs_m_list = [] # dummy
carbon_m_list = [] # dummy
extended_subs = []
if other_meshes["TE_Skin"]:
    m = other_meshes["TE_Skin"]
    print("TE Skin mesh faces:", len(m.faces))

root.destroy()

import sys, json
from core.export_3d import Wing3DBuilder
from core.engine import RibGeneratorEngine

engine = RibGeneratorEngine()
with open("test.json", "r") as f:
    p = json.load(f)

p['connectors'] = [(200.0, "V-Shape"), (400.0, "Y-Shape")]
p['y_positions'] = [0.0, 200.0, 400.0, 600.0]
p['export_connectors'] = True

builder = Wing3DBuilder(engine, p)
builder._collect_geometry_data()
builder.build_geometry()

print("Connectors in meshes:")
for key, mesh in builder.meshes.items():
    if "Connector" in key:
        print(f"{key}: {len(mesh.faces)} faces")

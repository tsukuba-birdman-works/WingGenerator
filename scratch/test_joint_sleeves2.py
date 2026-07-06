from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DBuilder

engine = RibGeneratorEngine()
# mock y_positions and ribs
engine.y_positions = [0.0, 100.0, 200.0]
engine.wing_span = 200.0

def dummy_rib(p, y, idx, thick, is_carbon, te_cut):
    # res structure:
    # 0: outline, 2: main_hole, 4: front_hole, 6: rear_hole
    # 7: truss_holes, 8: jig_holes
    # 16: stringer_holes, 18: aux_holes
    # 19: te_cap_holes
    return ([ [0,0], [10,0], [10,10], [0,10] ], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []), [0, y, 0], [1.0]

engine.generate_rib_at_y = dummy_rib

params = {
    'y_positions': [0.0, 100.0, 200.0],
    'rib_thick': 2.0,
    'spar_hole_dia': 20.0,
    'joint_length': 0.0,
    'export_joint_sleeves': True,
    'joint_sleeves': [
        {'start': 5.0, 'end': 55.0, 'out_dia': 30.0, 't1': 2.0, 't2': 0.5}
    ],
    'mat_js_foam': 'Styrofoam (Blue)',
    'mat_js_cap': 'Carbon (Black)',
    'mat_js_skin': 'Carbon (Black)',
    'export_ribs': True,
    'mat_ribs': 'Styrofoam (Blue)',
    # defaults to prevent KeyError
    'export_main_spar': False, 'export_front_spar': False, 'export_rear_spar': False,
    'export_plank': False, 'export_te': False, 'export_connectors': False,
    'export_stringers': False, 'export_xbrace_wires': False, 'export_diag_spars': False,
    'export_carbon_ribs': False, 'export_te_caps': False, 'export_rib_caps': False,
    'export_film': False, 'tabs_active': False
}

builder = Wing3DBuilder(engine, params)
builder.build_and_export("scratch/test_joint_sleeves2.glb")
print("Exported scratch/test_joint_sleeves2.glb")

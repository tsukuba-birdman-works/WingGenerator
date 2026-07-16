import json
from core.engine import RibGeneratorEngine

with open('preset/test.json', 'r') as f:
    p = json.load(f)

p['y_positions'] = [0, 50, 100]
p['wing_type'] = "Right"

engine = RibGeneratorEngine()
u_x_mod, u_y_mod, l_x_mod, l_y_mod, _ = engine.apply_plank_offset(
    engine.get_airfoil_points(p['airfoil_name'])[0],
    engine.get_airfoil_points(p['airfoil_name'])[1],
    engine.get_airfoil_points(p['airfoil_name'])[2],
    engine.get_airfoil_points(p['airfoil_name'])[3],
    0, 0, 0, 0, 0, 200
)

te_x, te_y, te_nx, te_ny = engine.get_slice_curve(
    engine.get_loop_curve(u_x_mod, u_y_mod, l_x_mod, l_y_mod, 200)[0],
    engine.get_loop_curve(u_x_mod, u_y_mod, l_x_mod, l_y_mod, 200)[1],
    engine.get_loop_curve(u_x_mod, u_y_mod, l_x_mod, l_y_mod, 200)[2],
    engine.get_loop_curve(u_x_mod, u_y_mod, l_x_mod, l_y_mod, 200)[3],
    engine.get_loop_curve(u_x_mod, u_y_mod, l_x_mod, l_y_mod, 200)[4],
    p['te_start'] / 200.0, 1.0
)

print("TE Curve starts at:", te_x[0], te_y[0])
print("TE Curve ends at:", te_x[-1], te_y[-1])
print("Rib max X:", max(engine.get_loop_curve(u_x_mod, u_y_mod, l_x_mod, l_y_mod, 200)[0]))

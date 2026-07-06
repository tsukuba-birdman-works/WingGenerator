from core.engine import RibGeneratorEngine
import numpy as np

engine = RibGeneratorEngine()
p = {
    'file1': '/tmp/dummy.dat',
    'file2': '/tmp/dummy.dat',
    'wing_span': 100,
    'chord_root': 100,
    'chord_tip': 100,
    'jig_base_height': 100.0,
}
t = np.linspace(0, 2*np.pi, 20)
x = 0.5 + 0.5*np.cos(t)
y = 0.1*np.sin(t)
with open("/tmp/dummy.dat", "w") as f:
    f.write("MH43\n")
    for i in range(len(x)):
        f.write(f"{x[i]:.4f} {y[i]:.4f}\n")

pts = engine.generate_jig_at_y(p, 0.0)
print(f"generate_jig_at_y returned type: {type(pts)}, len: {len(pts) if pts else 0}")
if pts:
    print(f"First pt: {pts[0]}")

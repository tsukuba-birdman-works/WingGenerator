import sys
sys.path.append('.')
from core.engine import RibGeneratorEngine
engine = RibGeneratorEngine()
params = {
    'chord': 200, 'washout': 0, 'y_positions': [0], 'truss_angles_dict': {}, 'base_truss_angle': 0,
    'te_cut': 20, 'spar_pos': 30, 'front_spar_pos': 15, 'rear_spar_pos': 70,
    'spar_dia': 10, 'front_spar_dia': 6, 'rear_spar_dia': 8,
    'te_cap_uf_act': True, 'te_cap_uf_width': 5, 'te_cap_thick': 2,
    'te_cap_ur_act': False, 'te_cap_lf_act': False, 'te_cap_lr_act': False,
    'te_cut_overlap': 30
}
res = engine.generate_single_rib(params)
import matplotlib.pyplot as plt
plt.figure()
plt.plot(res[0][:, 0], res[0][:, 1], 'b-', label='Rib')
if len(res[14]) > 0:
    plt.plot(res[14][:, 0], res[14][:, 1], 'g-', label='TE Block')
for cap in res[22]:
    for c in cap:
        c_poly = np.vstack([c, c[0]])
        plt.plot(c_poly[:, 0], c_poly[:, 1], 'r-', label='TE Cap')
plt.xlim(160, 205)
plt.ylim(-10, 10)
plt.legend()
plt.savefig('scratch/plot_cap_fix.png')
print("Plot saved.")

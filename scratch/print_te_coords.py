from core.engine import RibGeneratorEngine
import json
import numpy as np

with open('preset/test.json', 'r') as f:
    p = json.load(f)

p['file1'] = 'preset/' + p.get('file1', 'AG35.dat')
p['file2'] = 'preset/' + p.get('file2', 'AG35.dat')
p['te_cut'] = 20
p['te_cap_uf_act'] = True
p['te_cap_uf_w'] = 5
if 'connectors' not in p: p['connectors'] = []
if 'xb_zones' not in p: p['xb_zones'] = []

engine = RibGeneratorEngine()
res = engine.generate_rib_at_y(p, 0, 0, 2)
te_block = res.te_part_coords
caps = res.te_cap_pts_list

if len(te_block) > 0:
    min_x_block = np.min(te_block[:, 0])
    max_x_block = np.max(te_block[:, 0])
    print(f"TE Block X range: {min_x_block:.2f} to {max_x_block:.2f}")

if len(caps[0]) > 0:
    cap0 = caps[0][0]
    min_x_cap = np.min(cap0[:, 0])
    max_x_cap = np.max(cap0[:, 0])
    print(f"TE Cap Upper X range: {min_x_cap:.2f} to {max_x_cap:.2f}")


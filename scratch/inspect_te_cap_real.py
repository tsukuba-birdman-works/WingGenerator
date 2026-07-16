import tkinter as tk
from ui.single_mode import RibGeneratorGUI_Single
import matplotlib.pyplot as plt
import unittest.mock as mock

root = tk.Tk()
app = RibGeneratorGUI_Single(root)

with mock.patch('tkinter.filedialog.askopenfilename', return_value='preset/test.json'):
    app.load_config()

engine = app.engine
p = app.get_params()
res = engine.generate_rib_at_y(p, 0, 0, 2)
rib_pts = res.final_rib_mod
te_block = res.te_part_coords
caps = res.te_cap_pts_list

plt.figure(figsize=(10, 5))
if len(rib_pts) > 0:
    plt.plot(rib_pts[:,0], rib_pts[:,1], 'k-', label='Rib')
if len(te_block) > 0:
    plt.plot(te_block[:,0], te_block[:,1], 'g-', label='TE Block')
if len(caps[0]) > 0:
    for cap in caps[0]:
        plt.plot(cap[:,0], cap[:,1], 'r-', label='Upper Cap')
if len(caps[1]) > 0:
    for cap in caps[1]:
        plt.plot(cap[:,0], cap[:,1], 'b-', label='Lower Cap')
plt.axis('equal')
plt.xlim(160, 210)
plt.legend()
plt.savefig('scratch/te_cap_inspect.png')
print("Saved to scratch/te_cap_inspect.png")

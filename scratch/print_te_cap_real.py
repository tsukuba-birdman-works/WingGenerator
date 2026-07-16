import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
import unittest.mock as mock

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

with mock.patch('tkinter.filedialog.askopenfilename', return_value='preset/test.json'):
    app.load_config()

engine = app.engine
p = app.get_params()
res = engine.generate_rib_at_y(p, 0, 0, 2)
rib_pts = res.final_rib_mod
te_block = res.te_part_coords
caps = res.te_cap_pts_list

import numpy as np
print("TE Block X min:", np.min(te_block[:, 0]))
print("TE Cap upper X max:", np.max(caps[0][0][:, 0]))
print("Rib X max:", np.max(rib_pts[:, 0]))

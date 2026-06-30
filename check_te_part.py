import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core.engine import RibGeneratorEngine

engine = RibGeneratorEngine()
y_positions = [0.0, 100.0]
chords = [200.0, 200.0]
twists = [0.0, 0.0]
engine.update_parameters(
    y_positions=y_positions,
    chords=chords,
    twists=twists,
    te_cut=20.0,
    export_te=True
)
engine.generate_ribs()
res = engine.rib_results[0]
te_part = res.te_part_coords
print("TE part vertices:", len(te_part))

import matplotlib.pyplot as plt
import numpy as np
te_arr = np.array(te_part)
plt.plot(te_arr[:,0], te_arr[:,1], marker='o')
plt.axis('equal')
plt.savefig('te_part.png')
print("Saved TE part image to te_part.png")

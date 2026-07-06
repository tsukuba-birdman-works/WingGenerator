import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

# Manually inject joint sleeve params
app.js1_act.set(True)
app.js1_start.set("5.0")
app.js1_end.set("55.0")
app.js1_out_dia.set("30.0")
app.js1_t1.set("2.0")
app.js1_t2.set("0.5")
app.spar_hole_dia.set("20.0")

# Mock other minimal stuff
app.wing_span.set("500")
app.interval.set("100")
app.joint_length.set("0")
app.chord_root.set("200")
app.chord_tip.set("200")
app.spar_pos_root.set("30")
app.spar_pos_tip.set("30")
app.generate_y_positions()

params = app._get_builder_params()
params['tabs_active'] = False

from core.export_3d import Wing3DBuilder
builder = Wing3DBuilder(app.engine, params)
builder.build_and_export("scratch/test_joint_sleeves.glb")
print("Exported successfully.")

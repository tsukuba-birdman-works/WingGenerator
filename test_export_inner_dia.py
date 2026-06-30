from ui.batch_mode import RibGeneratorGUI_Batch
import tkinter as tk

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)

app.file1_path.set("data/dae51.dat"); app.file2_path.set("data/dae51.dat")
# Set some bolt values
app.root_bolt1_dia.set("3.0")
app.root_bolt2_dia.set("3.0")
app.tip_bolt1_dia.set("3.0")
app.tip_bolt2_dia.set("3.0")
app.bolt_spacer_inner_dia.set("2.0")
app.bolt_spacer_length.set("10.0")

# Enable 3D export items
app.export_main_spar.set(True)
app.export_front_spar.set(True)
app.export_rear_spar.set(True)
app.export_diag_spars.set(True)
app.export_xbrace_wires.set(True)

import time
start = time.time()
try:
    from core.export_3d import Wing3DBuilder
    params = app._get_builder_params()
    params['tabs_active'] = False
    
    builder = Wing3DBuilder(app.engine, params)
    builder.build_and_export("test_inner_dia.glb")
    print(f"Success! Time: {time.time()-start:.2f}s")
except Exception as e:
    import traceback
    traceback.print_exc()


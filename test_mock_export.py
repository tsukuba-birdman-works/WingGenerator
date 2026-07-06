import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
ui = RibGeneratorGUI_Batch(root)

# Set some values to test
ui.dxf_all_in_one.set(True)
ui.dxf_part_outline.set(False)
ui.dxf_target_jigs.set(False)

params = ui._get_builder_params()
print("all_in_one:", params.get('dxf_all_in_one'))
print("part_outline:", params.get('dxf_part_outline'))
print("target_jigs:", params.get('dxf_target_jigs'))

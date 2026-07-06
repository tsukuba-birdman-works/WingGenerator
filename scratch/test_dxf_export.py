import tkinter as tk
import os
from unittest.mock import patch
from ui.batch_mode import RibGeneratorGUI_Batch

def run_test():
    root = tk.Tk()
    app = RibGeneratorGUI_Batch(root)
    root.update()
    
    app.pm.vars['file1_path'].set(os.path.abspath("airfoils/26_center_XGAG_1.23 _11.61_48.5.dat"))
    app.pm.vars['file2_path'].set(os.path.abspath("airfoils/26_5th-tip_DAE-41_AIRFOIL .dat"))
    app.pm.vars['wing_span'].set("1000")
    app.pm.vars['rib_interval'].set("100")
    app.pm.vars['joint_length'].set("0")
    app.pm.vars['jig_y_positions'].set("100, 500")
    app.calculate_y_positions()
    
    app.pm.vars['dxf_all_in_one'].set(True)
    app.pm.vars['dxf_layer_rib_outline'].set(True)
    app.pm.vars['dxf_layer_holes'].set(False)
    app.pm.vars['wing_name'].set("TestWing")
    
    app.update_dxf_selection_ui()
    if "rib___0" in app.dxf_selection_vars:
        app.dxf_selection_vars["rib___0"].set(False)

    def print_error(*args):
        print("ERROR:", args)

    with patch('tkinter.filedialog.askdirectory', return_value=os.path.abspath("scratch")), patch('tkinter.messagebox.showerror', print_error), patch('tkinter.messagebox.showinfo', lambda *args: print("SUCCESS:", args)):
        app.export_dxf()
    
    root.destroy()
    print("DXF export test completed.")

run_test()

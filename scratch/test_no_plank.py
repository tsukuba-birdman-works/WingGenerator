import sys
import traceback
import tkinter as tk
sys.path.append('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
from ui.app import RibGeneratorApp

root = tk.Tk()
app = RibGeneratorApp(root)
app.update()
app.chord_var.set(1000.0)
app.plank_enabled_var.set(False)
app._generate_rib()
app._open_fea_window()
fea = app.fea_window
fea.plank_enabled_var.set(False)
fea.str_enabled_var.set(False)
try:
    fea._run_analysis()
    print("Success")
except Exception as e:
    traceback.print_exc()

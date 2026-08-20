import sys, os
import tkinter as tk
sys.path.append('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
from ui.app import RibGeneratorApp
from core.engine import RibGeneratorEngine
from core.fea_engine import RibFEAEngine

root = tk.Tk()
app = RibGeneratorApp(root)
app.update()

# Set params
app.chord_var.set(1000.0)
app.plank_start_var.set(0.0)
app.plank_end_var.set(100.0)
app.plank_thick_var.set(2.0)

# Generate rib
app._generate_rib()
print("Rib generation successful.")

# Open FEA window
app._open_fea_window()
fea_win = app.fea_window
fea_win.plank_enabled_var.set(True)
fea_win.plank_E_var.set(3000.0)
fea_win.plank_width_var.set(100.0)
fea_win.e_var.set(15.0)
fea_win.csv_path_var.set(os.path.abspath('lift_distribution_sample.csv'))

# Run analysis
fea_win._run_analysis()
print("FEA analysis successful.")

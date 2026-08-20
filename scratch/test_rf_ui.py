import sys
import tkinter as tk
sys.path.append('/home/akihito-kasai/Desktop/tbw/Ribgenerator')
from ui.app import RibGeneratorApp

root = tk.Tk()
app = RibGeneratorApp(root)
app.update()
app.chord_var.set(1000.0)
app._generate_rib()
app._open_fea_window()

fea = app.fea_window
fea.plank_enabled_var.set(True)
fea.str_enabled_var.set(False)

# Mock the progress start and stop
fea.progress = type('mock', (), {'start': lambda: None, 'stop': lambda: None})()

try:
    # Run synchronously for test
    fea._run_analysis_thread(fea.csv_path_var.get())
    
    # Wait for after queues to process
    root.update()
    
    print("Main Spar Label Text:", fea.rf_main_label.cget("text"))
    print("Rear Spar Label Text:", fea.rf_rear_label.cget("text"))
    print("Test passed successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
    
root.destroy()

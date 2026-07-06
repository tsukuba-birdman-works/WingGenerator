import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch

root = tk.Tk()
app = RibGeneratorGUI_Batch(root)
app.conn1_y.set('200.0')
app.conn1_type.set('Y-Shape')
root.update()

import time
time.sleep(1)

# Take screenshot using Xvfb (assuming we are in a virtual display)
import os
os.system("import -window root scratch/ui_screenshot.png")

import sys
import os
import tkinter as tk
sys.path.append(os.getcwd())
from ui.batch_mode import BatchModeUI

class DummyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.vars = {}

    def start_batch_mode(self):
        self.batch_ui = BatchModeUI(self)
        self.batch_ui.wing_span.set("1000")
        self.batch_ui.chord_root.set("200")
        self.batch_ui.chord_tip.set("200")
        self.batch_ui.te_cut.set("10")
        self.batch_ui.rib_thick.set("2")
        self.batch_ui.export_te.set(True)
        self.batch_ui.export_ribs.set(True)
        
        # force generate
        self.batch_ui.generate_batch_ribs(output_dir=".", export_3d_flag=True, export_dxf_flag=False, show_preview=False)
        self.root.destroy()

app = DummyApp()
app.start_batch_mode()

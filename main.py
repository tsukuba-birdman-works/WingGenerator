#!/usr/bin/env python3

import tkinter as tk
from ui.batch_mode import RibGeneratorGUI_Batch
from ui.foam_mode import FoamCutterGUI
from ui.fin_mode import WingtipFinGUI

# ==========================================
# ランチャー (Mode Selection)
# ==========================================
def main():
    root = tk.Tk()
    root.title("WingGenerator - Ver.1.0.0 (Mode Select)")
    root.geometry("920x250")
    root.eval('tk::PlaceWindow . center')
    
        
    def start_batch():
        for w in root.winfo_children(): w.destroy()
        app = RibGeneratorGUI_Batch(root)
        
    def start_foam_cam():
        for w in root.winfo_children(): w.destroy()
        app = FoamCutterGUI(root)

    def start_fin_gen():
        for w in root.winfo_children(): w.destroy()
        app = WingtipFinGUI(root)
        
    tk.Label(root, text="Select Generation Mode", font=("Arial", 16, "bold")).pack(pady=(30, 20))
    btn_frame = tk.Frame(root); btn_frame.pack()
    tk.Button(btn_frame, text="Batch Wing Mode\n(翼全体のリブ設計)", font=("Arial", 11), width=18, height=3, bg="lightblue", command=start_batch).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="4-Axis Foam CAM\n(フォームコア加工)", font=("Arial", 11), width=18, height=3, bg="lightyellow", command=start_foam_cam).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Wingtip Fin Gen\n(翼端フィン設計)", font=("Arial", 11), width=18, height=3, bg="#e8d8f8", command=start_fin_gen).pack(side=tk.LEFT, padx=10)
    root.mainloop()

if __name__ == "__main__":
    main()
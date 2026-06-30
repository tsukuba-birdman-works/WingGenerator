import tkinter as tk
from tkinter import ttk

class WeightWindow:
    def __init__(self, parent, engine, params):
        self.top = tk.Toplevel(parent)
        self.top.title("Weight Estimate")
        self.top.geometry("400x300")
        
        self.engine = engine
        self.params = params
        
        ttk.Label(self.top, text="Weight Calculation Module (WIP)").pack(pady=20)
        ttk.Label(self.top, text="This feature is under development.").pack()

        # Dummy button to close
        ttk.Button(self.top, text="Close", command=self.top.destroy).pack(pady=20)


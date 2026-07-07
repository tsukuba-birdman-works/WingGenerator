import tkinter as tk
from tkinter import ttk, messagebox
from core.weight_engine import DEFAULT_MATERIAL_PROPS, WeightCalculator
from core.export_3d import Wing3DBuilder
import threading

class WeightWindow(tk.Toplevel):
    def __init__(self, parent, engine, params):
        super().__init__(parent)
        self.title("Weight Calculator")
        self.geometry("850x650")
        
        self.engine = engine
        self.params = params
        self.geoms = {}
        self.extra_analytics = {}
        self.mat_vars = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame: Inputs
        left_frame = ttk.LabelFrame(main_frame, text="Material Properties & Densities")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        canvas = tk.Canvas(left_frame, width=320)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        row = 0
        for key, val in DEFAULT_MATERIAL_PROPS.items():
            ttk.Label(scrollable_frame, text=key).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            if isinstance(val, bool):
                var = tk.BooleanVar(value=val)
                cb = ttk.Checkbutton(scrollable_frame, variable=var)
                cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            elif isinstance(val, float):
                var = tk.DoubleVar(value=val)
                ent = ttk.Entry(scrollable_frame, textvariable=var, width=10)
                ent.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            elif isinstance(val, str):
                var = tk.StringVar(value=val)
                ent = ttk.Entry(scrollable_frame, textvariable=var, width=15)
                ent.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            self.mat_vars[key] = var
            row += 1
            
        self.btn_calc = ttk.Button(scrollable_frame, text="Calculate Weight", command=self.start_calculation)
        self.btn_calc.grid(row=row, column=0, columnspan=2, pady=15)
        
        self.lbl_status = ttk.Label(scrollable_frame, text="", foreground="blue")
        self.lbl_status.grid(row=row+1, column=0, columnspan=2, pady=5)
        
        # Right frame: Results
        right_frame = ttk.LabelFrame(main_frame, text="Weight Report")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        columns = ("category", "name", "qty", "weight", "note")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        self.tree.heading("category", text="Category")
        self.tree.heading("name", text="Part Name")
        self.tree.heading("qty", text="Quantity / Formula")
        self.tree.heading("weight", text="Weight (g)")
        self.tree.heading("note", text="Note")
        
        self.tree.column("category", width=100)
        self.tree.column("name", width=150)
        self.tree.column("qty", width=180)
        self.tree.column("weight", width=80, anchor=tk.E)
        self.tree.column("note", width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.lbl_total = ttk.Label(right_frame, text="Total Weight: 0.00 g", font=("Arial", 14, "bold"))
        self.lbl_total.pack(pady=10)
        
    def start_calculation(self):
        self.btn_calc.config(state=tk.DISABLED)
        self.lbl_status.config(text="Generating geometry... Please wait.")
        self.update_idletasks()
        
        threading.Thread(target=self._run_calculation, daemon=True).start()
        
    def _run_calculation(self):
        try:
            # 1. Build geometry with all parts enabled for complete weight calculation
            calc_params = self.params.copy()
            for k in ['export_ribs', 'export_te', 'export_film', 'export_stringers', 
                      'export_te_caps', 'export_connectors', 'export_diag_spars', 
                      'export_xbrace_wires', 'export_joint_sleeves']:
                calc_params[k] = True
            builder = Wing3DBuilder(self.engine, calc_params)
            geoms, analytics = builder.build_geometry()
            self.geoms = geoms
            self.extra_analytics = analytics
            
            # 2. Compute weights
            mat_props = {k: v.get() for k, v in self.mat_vars.items()}
            calc = WeightCalculator()
            results = calc.calculate_weights(self.geoms, mat_props, self.extra_analytics, self.params)
            
            # 3. Update UI
            self.after(0, self._update_results, results)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.after(0, self._show_error, str(e))
            
    def _update_results(self, results):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        total_w = 0.0
        for r in results:
            w = r['weight_g']
            total_w += w
            self.tree.insert("", tk.END, values=(
                r['category'], r['display_name'], r['quantity_str'], f"{w:.2f}", r['note']
            ))
        
        self.lbl_total.config(text=f"Total Weight: {total_w:.2f} g")
        self.lbl_status.config(text="Done.")
        self.btn_calc.config(state=tk.NORMAL)
        
    def _show_error(self, err_msg):
        self.lbl_status.config(text="Error occurred.")
        self.btn_calc.config(state=tk.NORMAL)
        messagebox.showerror("Error", f"Calculation failed:\n{err_msg}", parent=self)


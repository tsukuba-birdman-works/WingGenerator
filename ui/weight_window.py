import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from core.weight_engine import DEFAULT_MATERIAL_PROPS, WeightCalculator
from core.export_3d import Wing3DBuilder
import threading

class WeightWindow(tk.Toplevel):
    def __init__(self, parent, engine, params):
        super().__init__(parent)
        self.title("Weight Calculator")
        self.geometry("1100x700")
        
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
        
        canvas = tk.Canvas(left_frame, width=420)
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
        
        self.MATERIAL_LABELS = {
            'foam_volume_density': 'フォーム材 体積密度 (g/cm³)',
            'foam_skin_area_density': 'フォーム材 表面スキン密度 (g/m²)',
            'main_spar_mode': '主桁計算モード (固定重量/計算)',
            'main_spar_weight_g': '主桁 固定重量 (g)',
            'main_spar_linear_density': '主桁 線密度 (g/m)',
            'carbon_tube_volume_density': 'C-パイプ 体積密度 (g/cm³)',
            'stringer_volume_density': 'ストリンガー 体積密度 (g/cm³)',
            'xbrace_linear_density': 'Xブレース 線密度 (g/m)',
            'carbon_rib_area_density': 'C-リブ 面密度 (g/m²)',
            'carbon_rib_adhesive_density': 'C-リブ 接着剤面密度 (g/m²)',
            'carbon_cap_area_density': 'C-キャップ 面密度 (g/m²)',
            'carbon_cap_adhesive_density': 'C-キャップ 接着剤面密度 (g/m²)',
            'film_area_density': 'フィルム 面密度 (g/m²)',
            'te_balsa_volume_density': '後縁バルサ 体積密度 (g/cm³)',
            'tape_linear_density': '両面テープ 線密度 (g/m)',
        }

        row = 0
        for key, val in DEFAULT_MATERIAL_PROPS.items():
            label_text = self.MATERIAL_LABELS.get(key, key)
            ttk.Label(scrollable_frame, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            if key == 'main_spar_mode':
                var = tk.StringVar(value=val)
                cb = ttk.Combobox(scrollable_frame, textvariable=var, values=['固定重量', '計算'], state='readonly', width=13)
                cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            elif isinstance(val, bool):
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

        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="Load Preset", command=self.load_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Preset", command=self.save_preset).pack(side=tk.LEFT, padx=5)

        self.btn_calc = ttk.Button(scrollable_frame, text="Calculate Weight", command=self.start_calculation)
        self.btn_calc.grid(row=row+1, column=0, columnspan=2, pady=(5, 15))

        self.lbl_status = ttk.Label(scrollable_frame, text="", foreground="blue")
        self.lbl_status.grid(row=row+2, column=0, columnspan=2, pady=5)
        
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

    def save_preset(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        if not os.path.splitext(path)[1]: path += '.json'
        try:
            data = {k: v.get() for k, v in self.mat_vars.items()}
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Saved", f"Preset saved to {path}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preset:\n{e}", parent=self)

    def load_preset(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for k, val in data.items():
                if k in self.mat_vars:
                    self.mat_vars[k].set(val)
            messagebox.showinfo("Loaded", f"Preset loaded from {path}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset:\n{e}", parent=self)

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
                      'export_xbrace_wires', 'export_joint_sleeves', 'export_te_balsa']:
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


import re

with open('ui/batch_mode.py', 'r') as f: code = f.read()

# 1. Add the comboboxes above the Export DXF button
dxf_btn_search = r"        if 'DXF' in self\.pm\.obj\.tabs_frames:\n            ttk\.Button\(self\.pm\.obj\.tabs_frames\['DXF'\], text=\"Export DXF\", command=self\.export_dxf\)\.pack\(fill=tk\.X, padx=10, pady=5\)"
dxf_combo_add = """        if 'DXF' in self.pm.obj.tabs_frames:
            lf_dxf = ttk.LabelFrame(self.pm.obj.tabs_frames['DXF'], text="Rib Range Filter")
            lf_dxf.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(lf_dxf, text="Start Rib:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
            self.combo_dxf_start = ttk.Combobox(lf_dxf, state='readonly', width=20)
            self.combo_dxf_start.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            ttk.Label(lf_dxf, text="End Rib:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
            self.combo_dxf_end = ttk.Combobox(lf_dxf, state='readonly', width=20)
            self.combo_dxf_end.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Button(self.pm.obj.tabs_frames['DXF'], text="Export DXF", command=self.export_dxf).pack(fill=tk.X, padx=10, pady=5)"""
code = re.sub(dxf_btn_search, dxf_combo_add, code, flags=re.DOTALL)

# 2. Update them in update_rib_combobox
update_search = r"            if hasattr\(self, 'combo_foam_start'\):\n                rib_only_values = \[item\['label'\] for item in items if item\['type'\] == 'rib'\]\n                self\.combo_foam_start\['values'\] = rib_only_values\n                self\.combo_foam_end\['values'\] = rib_only_values"
update_add = """            if hasattr(self, 'combo_foam_start'):
                rib_only_values = [item['label'] for item in items if item['type'] == 'rib']
                self.combo_foam_start['values'] = rib_only_values
                self.combo_foam_end['values'] = rib_only_values
                if hasattr(self, 'combo_dxf_start'):
                    self.combo_dxf_start['values'] = rib_only_values
                    self.combo_dxf_end['values'] = rib_only_values"""
code = re.sub(update_search, update_add, code, flags=re.DOTALL)

# 3. Set current index in update_rib_combobox
current_search = r"                if hasattr\(self, 'combo_foam_start'\):\n                    if self\.combo_foam_start\.current\(\) < 0: self\.combo_foam_start\.current\(0\)\n                    if self\.combo_foam_end\.current\(\) < 0: self\.combo_foam_end\.current\(len\(c_values\)-1\)"
current_add = """                if hasattr(self, 'combo_foam_start'):
                    if self.combo_foam_start.current() < 0: self.combo_foam_start.current(0)
                    if self.combo_foam_end.current() < 0: self.combo_foam_end.current(len(rib_only_values)-1)
                    if hasattr(self, 'combo_dxf_start'):
                        if self.combo_dxf_start.current() < 0: self.combo_dxf_start.current(0)
                        if self.combo_dxf_end.current() < 0: self.combo_dxf_end.current(len(rib_only_values)-1)"""
code = re.sub(current_search, current_add, code, flags=re.DOTALL)

with open('ui/batch_mode.py', 'w') as f: f.write(code)

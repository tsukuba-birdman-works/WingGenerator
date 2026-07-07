with open('ui/single_mode.py', 'r') as f:
    text = f.read()

# Fix get_rib_parameters
text = text.replace('file2=self.file1_path.get()', 'file2=self.file2_path.get()')
text = text.replace('file2=self.file1_path.get(), # Single mode uses same file? Wait, single mode file2_path was removed? No, I only kept file1_path.', 'file2=self.file2_path.get(),')

# Fix update_preview
text = text.replace('if not self.file1_path.get(): return', 'if not self.file1_path.get() or not self.file2_path.get(): return')

# Fix export_dxf and export_obj
text = text.replace('f1 = self.file1_path.get()\n        if not f1 or not os.path.exists(f1): return messagebox.showerror("Error", "Please select valid files.")', 
                    'f1, f2 = self.file1_path.get(), self.file2_path.get()\n        if not f1 or not f2 or not os.path.exists(f1) or not os.path.exists(f2): return messagebox.showerror("Error", "Please select valid files.")')

with open('ui/single_mode.py', 'w') as f:
    f.write(text)

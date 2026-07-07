import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

# Fix open_weight_window
old_win = """    def open_weight_window(self):
        \"\"\"重量計算ウインドウを開く\"\"\"
        try:
            params = self._get_builder_params()
        except Exception as e:
            params = {}
        from ui.weight_window import WeightWindow
        WeightWindow(self.root, self.engine, params)"""
new_win = """    def open_weight_window(self):
        \"\"\"重量計算ウインドウを開く\"\"\"
        try:
            params = self._get_builder_params()
        except Exception as e:
            params = {}
        from ui.weight_window import WeightWindow
        WeightWindow(self.root, self.engine, params)"""
if old_win in text:
    print("open_weight_window already correct")
else:
    print("Could not find open_weight_window")


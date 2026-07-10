import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

# Remove the bad binding
target1 = """        self.ui_builder.build_tabs(notebook, self.pm)
        notebook.bind("<<NotebookTabChanged>>", lambda e: [self.calculate_y_positions(), self.update_preview_full()])

        # Append custom panels"""

replacement1 = """        self.ui_builder.build_tabs(notebook, self.pm)

        # Append custom panels"""

if target1 in text:
    text = text.replace(target1, replacement1)
    print("Removed bad binding")
else:
    print("Target 1 not found")

# Add the binding at the end of create_widgets
target2 = """    def browse_file(self, var, is_dxf=False):"""

replacement2 = """        notebook.bind("<<NotebookTabChanged>>", lambda e: [self.calculate_y_positions(), self.update_preview_full()]) if hasattr(self, 'combo_rib') else None

    def browse_file(self, var, is_dxf=False):"""

if target2 in text:
    text = text.replace(target2, replacement2)
    print("Added safe binding")
else:
    print("Target 2 not found")

with open('ui/batch_mode.py', 'w') as f:
    f.write(text)


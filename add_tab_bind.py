import re

with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

target = """        self.ui_builder.build_tabs(notebook, self.pm)

        # Append custom panels"""

replacement = """        self.ui_builder.build_tabs(notebook, self.pm)
        notebook.bind("<<NotebookTabChanged>>", lambda e: [self.calculate_y_positions(), self.update_preview_full()])

        # Append custom panels"""

if target in text:
    text = text.replace(target, replacement)
    with open('ui/batch_mode.py', 'w') as f:
        f.write(text)
    print("Added NotebookTabChanged binding")
else:
    print("Target not found")


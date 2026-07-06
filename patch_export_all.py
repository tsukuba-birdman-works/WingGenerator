import re

with open("core/export_dxf.py", "r") as f:
    content = f.read()

# I will rewrite export_all_ribs completely.
import ast
# Let's just create a new WingDXFExporter class and replace it.

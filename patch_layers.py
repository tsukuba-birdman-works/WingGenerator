import re

with open('core/engine.py', 'r') as f:
    code = f.read()

def replace_layer(layer_name, color):
    return f"if '{layer_name}' not in doc.layers: doc.layers.add(name='{layer_name}', color={color})"

# Fix the layers block in export_dxf
old_block = """        try:
            doc.layers.add(name='RIB_OUTLINE', color=7)
            doc.layers.add(name='HOLES', color=1)
            doc.layers.add(name='TRUSS', color=2)
            doc.layers.add(name='PLANK', color=3)
            doc.layers.add(name='TE_PART', color=4)
        except AttributeError:
            doc.layers.new(name='RIB_OUTLINE', dxfattribs={'color': 7})
            doc.layers.new(name='HOLES', dxfattribs={'color': 1})
            doc.layers.new(name='TRUSS', dxfattribs={'color': 2})
            doc.layers.new(name='PLANK', dxfattribs={'color': 3})
            doc.layers.new(name='TE_PART', dxfattribs={'color': 4})"""

new_block = """        try:
            if 'RIB_OUTLINE' not in doc.layers: doc.layers.add(name='RIB_OUTLINE', color=7)
            if 'HOLES' not in doc.layers: doc.layers.add(name='HOLES', color=1)
            if 'TRUSS' not in doc.layers: doc.layers.add(name='TRUSS', color=2)
            if 'PLANK' not in doc.layers: doc.layers.add(name='PLANK', color=3)
            if 'TE_PART' not in doc.layers: doc.layers.add(name='TE_PART', color=4)
        except AttributeError:
            pass"""

code = code.replace(old_block, new_block)

# Fix TE_CAPS and RIB_CAPS blocks
code = code.replace(
    "try: doc.layers.add(name='TE_CAPS', color=6)",
    "try:\n                if 'TE_CAPS' not in doc.layers: doc.layers.add(name='TE_CAPS', color=6)"
)
code = code.replace(
    "try: doc.layers.add(name='RIB_CAPS', color=5)",
    "try:\n                if 'RIB_CAPS' not in doc.layers: doc.layers.add(name='RIB_CAPS', color=5)"
)

# Fix export_single_poly_dxf
code = code.replace(
    "try: doc.layers.add(name='JIG', color=7)",
    "try:\n            if 'JIG' not in doc.layers: doc.layers.add(name='JIG', color=7)"
)


with open('core/engine.py', 'w') as f:
    f.write(code)


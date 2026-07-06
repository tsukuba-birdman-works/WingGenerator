import re
with open('core/engine.py', 'r') as f: code = f.read()

code = code.replace(
    "def export_single_poly_dxf(self, filepath, poly_pts, origin, doc=None, msp=None):",
    "def export_single_poly_dxf(self, filepath, poly_pts, origin, doc=None, msp=None, layer='PART'):"
)

code = code.replace(
    "if not doc.layers.has_entry('PART'):\n            doc.layers.add(name='PART', color=7)",
    "if not doc.layers.has_entry(layer):\n            doc.layers.add(name=layer, color=7)"
)

code = code.replace(
    "msp.add_lwpolyline(moved_pts, dxfattribs={'layer': 'PART'}, close=True)",
    "msp.add_lwpolyline(moved_pts, dxfattribs={'layer': layer}, close=True)"
)

with open('core/engine.py', 'w') as f: f.write(code)

with open('core/export_dxf.py', 'r') as f: code_dxf = f.read()

code_dxf = code_dxf.replace(
    'self.engine.export_single_poly_dxf("", jig_pts, origin_offset, doc=doc, msp=msp)',
    'self.engine.export_single_poly_dxf("", jig_pts, origin_offset, doc=doc, msp=msp, layer="JIG")'
)

code_dxf = code_dxf.replace(
    'self.engine.export_single_poly_dxf(filepath, jig_pts, origin_offset)',
    'self.engine.export_single_poly_dxf(filepath, jig_pts, origin_offset, layer="JIG")'
)

with open('core/export_dxf.py', 'w') as f: f.write(code_dxf)


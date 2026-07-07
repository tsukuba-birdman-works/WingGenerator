import re

with open('core/cam_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Modify def generate_gcode signature
old_sig = "def generate_gcode(self, rib_res, params: Dict[str, Any]) -> Tuple[str, List[str]]:"
new_sig = "def generate_gcode(self, rib_res, params: Dict[str, Any], is_jig: bool = False) -> Tuple[str, List[str]]:"
content = content.replace(old_sig, new_sig)

# Where does it extract shapes?
# Let's find out how it handles holes, caps etc.
# Actually, if is_jig is True, there are no holes, no caps, just the outer outline (poly_rot).
# Let's see how poly_rot is handled.
# poly_rot is handled as outer_pts.

with open('core/cam_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched core/cam_engine.py signature")

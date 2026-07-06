import re
with open('core/engine.py', 'r') as f: code = f.read()

replacement = """        if slot_boxes:
            try:
                from shapely.validation import make_valid
                slots_union = make_valid(unary_union(slot_boxes))
                poly = poly.difference(slots_union)
            except Exception as e:
                print(f"Jig Exception in difference: {e}")
                print(f"poly valid: {poly.is_valid}")
                slots_union = unary_union(slot_boxes).buffer(0)
                print(f"slots_union valid: {slots_union.is_valid}")
                try:
                    poly = poly.difference(slots_union)
                except Exception as e2:
                    print(f"Second diff failed: {e2}")
                    print("poly pts:")
                    for pt in pts: print(pt)"""

code = code.replace(
    """        if slot_boxes:
            try:
                from shapely.validation import make_valid
                slots_union = make_valid(unary_union(slot_boxes))
                poly = poly.difference(slots_union)
            except:
                slots_union = unary_union(slot_boxes).buffer(0)
                poly = poly.difference(slots_union)""",
    replacement
)

with open('core/engine.py', 'w') as f: f.write(code)

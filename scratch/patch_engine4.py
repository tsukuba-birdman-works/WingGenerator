import re

with open('core/engine.py', 'r') as f:
    content = f.read()

search = """                    # Ensure winding order is identical to Shapely's standard (CCW)
                    if SHAPELY_AVAILABLE:
                        try:
                            poly = Polygon(te_unrot)
                            if poly.is_valid and not poly.is_empty:
                                te_unrot = np.array(poly.exterior.coords)
                        except: pass"""

replace = """"""

if search in content:
    content = content.replace(search, replace)
    with open('core/engine.py', 'w') as f:
        f.write(content)
    print("Removed Shapely wrapper to preserve topology")
else:
    print("Could not find search block")

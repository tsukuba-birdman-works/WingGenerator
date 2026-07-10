import re

with open('core/engine.py', 'r') as f:
    text = f.read()

target1 = """    def get_local_params(self, params: Dict[str, Any], y_local: float) -> LocalParams:
        wing_span = params.get('wing_span', 1000.0)
        chord_root = params.get('chord_root', 200.0)
        chord_tip = params.get('chord_tip', 200.0)"""

replacement1 = """    def get_local_params(self, params: Dict[str, Any], y_local: float) -> LocalParams:
        wing_span = max(params.get('wing_span', 1000.0), 1.0)
        chord_root = max(params.get('chord_root', 200.0), 1.0)
        chord_tip = max(params.get('chord_tip', 200.0), 1.0)"""

target2 = """    def _scale_airfoil(self, upper_pts, lower_pts, chord, aoa_deg):
        if len(upper_pts) == 0 or len(lower_pts) == 0:
            return np.array([]), np.array([])"""

replacement2 = """    def _scale_airfoil(self, upper_pts, lower_pts, chord, aoa_deg):
        if chord < 1.0: chord = 1.0  # Prevent degenerate geometry and gradient errors
        if len(upper_pts) == 0 or len(lower_pts) == 0:
            return np.array([]), np.array([])"""

if target1 in text:
    text = text.replace(target1, replacement1)
    print("Patched get_local_params")
if target2 in text:
    text = text.replace(target2, replacement2)
    print("Patched _scale_airfoil")

with open('core/engine.py', 'w') as f:
    f.write(text)


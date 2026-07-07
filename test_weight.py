from core.weight_engine import WeightCalculator
import numpy as np

calc = WeightCalculator()
geoms = {} # No geometries
mat_props = {
    'foam_volume_density': 0.03,
    'carbon_tube_volume_density': 1.6,
    'stringer_volume_density': 0.5,
}
extra_analytics = {
    'main_spar_span_mm': 1000.0,
    'te_span_mm': 1000.0,
    'rib_perimeters_mm': [500.0, 500.0]
}
wing_params = {
    'main_spar_dia': 10.0,
    'main_spar_thickness': 1.0,
    'rear_spar_dia': 8.0,
    'rear_spar_thickness': 1.0,
    'stringers_data': [{'width': 5.0, 'depth': 5.0}]
}

# Mock category data will be generated inside calculate_weights. 
# But wait, category_data uses mesh_props which comes from geoms!
# If geoms is empty, category_data will be empty, so parts won't be calculated!
# Let's run it and see.
results = calc.calculate_weights(geoms, mat_props, extra_analytics, wing_params)
for r in results:
    print(r['name'], r['weight_g'])


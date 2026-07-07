with open('ui/weight_window.py', 'r') as f:
    text = f.read()

text = text.replace(
    "results = calc.calculate_weights(self.geoms, mat_props, self.extra_analytics)",
    "results = calc.calculate_weights(self.geoms, mat_props, self.extra_analytics, self.params)"
)

with open('ui/weight_window.py', 'w') as f:
    f.write(text)

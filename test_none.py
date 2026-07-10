import re

with open('ui/base_mode.py', 'r') as f:
    text = f.read()

target = """    def safe_float(self, var, default=0.0):
        try:
            val = var.get()
            if isinstance(val, str):
                val = val.strip()
                return float(val) if val else default
            return float(val)
        except:
            return default"""

replacement = """    def safe_float(self, var, default=0.0):
        try:
            val = var.get()
            if isinstance(val, str):
                val = val.strip()
                return float(val) if val else default
            return float(val)
        except:
            return default

    def safe_float_or_none(self, var):
        try:
            val = var.get()
            if isinstance(val, str):
                val = val.strip()
                return float(val) if val else None
            return float(val)
        except:
            return None"""

if target in text:
    text = text.replace(target, replacement)
    with open('ui/base_mode.py', 'w') as f:
        f.write(text)
    print("Added safe_float_or_none")
else:
    print("Target not found")

import os
import sys
sys.path.append(os.path.abspath('.'))
from core.engine import RibGeneratorEngine, RibParameters

# Try to initialize the engine to check for syntax errors
engine = RibGeneratorEngine()
print("Engine initialized successfully.")

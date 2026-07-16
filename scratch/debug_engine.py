import sys, os
sys.path.append(os.path.abspath('.'))
from core.engine import RibGeneratorEngine

# We will read a file and simulate it.
import tkinter as tk
from ui.param_manager import ParamManager
from ui.param_spec import BATCH_PARAMS

root = tk.Tk()
pm = ParamManager(None, BATCH_PARAMS)

p = pm.get_all_vars()
p['truss_scale_front'] = "0.5, 0.5"
p['truss_scale_rear'] = "0.5"

engine = RibGeneratorEngine()
# let's see what RibParameters gets

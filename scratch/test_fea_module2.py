import sys, os
sys.path.append(os.path.abspath('.'))
from core.fea_engine import RibFEAEngine

engine = RibFEAEngine(work_dir="scratch")
disp, stress = engine.parse_dat_results("scratch/rib_fea.dat")
print(f"Disp nodes parsed: {len(disp)}")
print(f"Stress elements parsed: {len(stress)}")
if stress:
    print(f"Max Von Mises stress: {max(stress.values()):.3f}")

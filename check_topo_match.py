import sys
import os
sys.path.append(os.getcwd())
import json

with open('/home/akihito-kasai/Desktop/tbw/Ribgenerator/core/export_3d.py', 'r') as f:
    content = f.read()

# Add a print statement in resample_closed
new_content = content.replace(
    "topo_match = len(all_corners) > 0 and all(len(cn) == len(all_corners[0]) and len(cn) > 0 for cn in all_corners)",
    "topo_match = len(all_corners) > 0 and all(len(cn) == len(all_corners[0]) and len(cn) > 0 for cn in all_corners)\n            print(f'topo_match: {topo_match}, all_corners lens: {[len(cn) for cn in all_corners]}', flush=True)"
)

with open('/home/akihito-kasai/Desktop/tbw/Ribgenerator/core/export_3d.py', 'w') as f:
    f.write(new_content)

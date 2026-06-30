import json
import os

target_ts = 1781770654 * 1000  # ms

history_dir = "/home/akihito-kasai/.config/Code/User/History/50b3bc30/"
entries_file = os.path.join(history_dir, "entries.json")
with open(entries_file, "r") as f:
    data = json.load(f)

entries = data.get("entries", [])
# find the one closest to target_ts
closest = None
min_diff = float("inf")
for e in entries:
    diff = abs(e["timestamp"] - target_ts)
    if diff < min_diff:
        min_diff = diff
        closest = e

if closest:
    print(f"Closest entry for batch_mode.py: {closest['id']} at {closest['timestamp']}")
    os.system(f"ls -l {history_dir}/{closest['id']}")

import json
import os

target_ts = 1781774038 * 1000  # ms

history_dir_base = "/home/akihito-kasai/.config/Code/User/History/"

for dirname in os.listdir(history_dir_base):
    entries_file = os.path.join(history_dir_base, dirname, "entries.json")
    if not os.path.exists(entries_file): continue
    with open(entries_file, "r") as f:
        data = json.load(f)
    res_path = data.get("resource", "")
    if "ui/single_mode.py" in res_path or "core/export_3d.py" in res_path:
        entries = data.get("entries", [])
        closest = None
        min_diff = float("inf")
        for e in entries:
            diff = abs(e["timestamp"] - target_ts)
            if diff < min_diff:
                min_diff = diff
                closest = e
        if closest:
            print(f"File: {res_path}")
            print(f"Closest entry: {closest['id']} at {closest['timestamp']}")
            print(f"Path: {history_dir_base}{dirname}/{closest['id']}\n")


import json
import datetime
import os

history_dir = "/home/akihito-kasai/.config/Code/User/History/50b3bc30/"
entries_file = os.path.join(history_dir, "entries.json")
with open(entries_file, "r") as f:
    data = json.load(f)

for e in data.get("entries", [])[-10:]:
    ts = e["timestamp"] / 1000
    dt = datetime.datetime.fromtimestamp(ts)
    print(f"{dt}: {e['id']}")


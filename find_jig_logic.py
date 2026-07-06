import json

transcript_path = "/home/akihito-kasai/.gemini/antigravity/brain/44a6c132-cd64-40bc-8e11-0505fb90f8d0/.system_generated/logs/transcript_full.jsonl"
matches = []

with open(transcript_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        if "content" in data and isinstance(data["content"], str):
            if "def generate_jig_at_y(" in data["content"] and "jig_angle" in data["content"]:
                matches.append(data["content"])
        
        # also check tool_calls
        if "tool_calls" in data:
            for tc in data["tool_calls"]:
                if "args" in tc:
                    for arg, val in tc["args"].items():
                        if isinstance(val, str) and "def generate_jig_at_y(" in val and "jig_angle" in val:
                            matches.append(val)

print(f"Found {len(matches)} matches.")
for i, m in enumerate(matches[-5:]): # look at the last 5
    print(f"\n--- MATCH {len(matches) - 5 + i} ---")
    lines = m.split('\n')
    start_idx = -1
    for j, l in enumerate(lines):
        if "def generate_jig_at_y(" in l:
            start_idx = j
            break
    
    if start_idx != -1:
        print("\n".join(lines[start_idx:start_idx+150]))

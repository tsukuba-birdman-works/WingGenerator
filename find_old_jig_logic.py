import json

transcript_path = "/home/akihito-kasai/.gemini/antigravity/brain/44a6c132-cd64-40bc-8e11-0505fb90f8d0/.system_generated/logs/transcript_full.jsonl"
matches = []

with open(transcript_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        content = ""
        if "content" in data and isinstance(data["content"], str):
            content += data["content"]
        if "tool_calls" in data:
            for tc in data["tool_calls"]:
                if "args" in tc:
                    for arg, val in tc["args"].items():
                        if isinstance(val, str):
                            content += val
        
        if "def generate_jig_at_y(" in content:
            matches.append(content)

print(f"Found {len(matches)} matches.")
# Print the first few matches which would be the oldest
for i in range(min(5, len(matches))):
    print(f"\n--- OLD MATCH {i} ---")
    lines = matches[i].split('\n')
    start_idx = -1
    for j, l in enumerate(lines):
        if "def generate_jig_at_y(" in l:
            start_idx = j
            break
    if start_idx != -1:
        print("\n".join(lines[start_idx:start_idx+100]))


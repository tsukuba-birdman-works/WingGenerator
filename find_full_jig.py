import json

transcript_path = "/home/akihito-kasai/.gemini/antigravity/brain/44a6c132-cd64-40bc-8e11-0505fb90f8d0/.system_generated/logs/transcript_full.jsonl"
with open(transcript_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        if "tool_calls" in data:
            for tc in data["tool_calls"]:
                if tc.get("name") in ["replace_file_content", "multi_replace_file_content", "run_command"]:
                    args = tc.get("args", {})
                    # If this is replace_file_content or multi_replace_file_content
                    # and the target is core/engine.py
                    content = str(args)
                    if "def generate_jig_at_y" in content and "LineString" in content and "frame_width" in content:
                        print(f"--- MATCH IN {tc['name']} ---")
                        print(content)

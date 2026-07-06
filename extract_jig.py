import json

transcript_path = "/home/akihito-kasai/.gemini/antigravity/brain/44a6c132-cd64-40bc-8e11-0505fb90f8d0/.system_generated/logs/transcript_full.jsonl"
with open(transcript_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        if "tool_calls" in data:
            for tc in data["tool_calls"]:
                if tc.get("name") == "replace_file_content":
                    args = tc.get("args", {})
                    if "Instruction" in args and "Update generate_jig_at_y with Shapely skeleton" in args.get("Instruction", ""):
                        with open("recovered_jig.py", "w") as out:
                            out.write(args["ReplacementContent"])
                        print("Saved to recovered_jig.py")

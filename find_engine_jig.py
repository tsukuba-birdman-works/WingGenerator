import json

transcript_path = "/home/akihito-kasai/.gemini/antigravity/brain/44a6c132-cd64-40bc-8e11-0505fb90f8d0/.system_generated/logs/transcript_full.jsonl"
with open(transcript_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        if "tool_calls" in data:
            for tc in data["tool_calls"]:
                if tc.get("name") in ["replace_file_content", "multi_replace_file_content", "write_to_file"]:
                    args = tc.get("args", {})
                    if "core/engine.py" in str(args) and "def generate_jig_at_y" in str(args):
                        print(f"\n======================\nFOUND IN {tc['name']}")
                        print(str(args)[:1000] + "...\n(TRUNCATED)")
                        
                        # Find the actual code that was replaced
                        if 'ReplacementContent' in args:
                            content = args['ReplacementContent']
                        elif 'ReplacementChunks' in args:
                            content = "\n".join([chunk.get('ReplacementContent', '') for chunk in args['ReplacementChunks']])
                        elif 'CodeContent' in args:
                            content = args['CodeContent']
                        else:
                            content = ""
                            
                        # Extract the function
                        lines = content.split('\n')
                        in_func = False
                        func_lines = []
                        for l in lines:
                            if "def generate_jig_at_y" in l:
                                in_func = True
                            if in_func:
                                func_lines.append(l)
                                if l.strip().startswith("return ") and "return_full" not in l:
                                    break
                        print("\n".join(func_lines))


import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

def dedup_list(match):
    content = match.group(1)
    # Extract all dicts
    dicts = re.findall(r"    \{.*?\},", content, re.DOTALL)
    
    seen = {}
    for d in dicts:
        # extract id
        id_match = re.search(r"'id':\s*'([^']+)'", d)
        if id_match:
            seen[id_match.group(1)] = d
            
    # Reconstruct
    res = "\n".join(seen.values())
    return "[\n" + res + "\n]"

code = re.sub(r"BATCH_PARAMS = \[\n(.*?)\n\]", lambda m: "BATCH_PARAMS = " + dedup_list(m), code, flags=re.DOTALL)
code = re.sub(r"SINGLE_PARAMS = \[\n(.*?)\n\]", lambda m: "SINGLE_PARAMS = " + dedup_list(m), code, flags=re.DOTALL)

with open("ui/param_spec.py", "w") as f:
    f.write(code)

print("Deduplicated param_spec.py")

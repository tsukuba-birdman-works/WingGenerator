import re

files = ["ui/single_mode.py", "ui/batch_mode.py"]
for fpath in files:
    with open(fpath, "r") as f:
        code = f.read()

    # for single_mode
    if "single_mode" in fpath:
        idxs = [m.start() for m in re.finditer(r"    def get_rib_parameters\(self", code)]
        if len(idxs) > 1:
            start_skip = idxs[1]
            end_skip = code.find("    def update_preview", start_skip)
            code = code[:start_skip] + code[end_skip:]

    # for batch_mode
    if "batch_mode" in fpath:
        idxs = [m.start() for m in re.finditer(r"    def _get_builder_params\(self", code)]
        if len(idxs) > 1:
            start_skip = idxs[1]
            end_skip = code.find("    def export_gcode_all", start_skip)
            code = code[:start_skip] + code[end_skip:]

    with open(fpath, "w") as f:
        f.write(code)

print("Deduplicated parameter methods")

with open("ui/batch_mode.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.startswith("    def _get_builder_params"):
        # count occurrences. we want to keep the FIRST one (our new one), and skip the SECOND one
        pass

# Actually simpler: find the first _get_builder_params and the second _get_builder_params
idxs = [i for i, l in enumerate(lines) if l.startswith("    def _get_builder_params(self):")]
if len(idxs) == 2:
    start_skip = idxs[1]
    # find next def
    end_skip = len(lines)
    for i in range(start_skip+1, len(lines)):
        if lines[i].startswith("    def "):
            end_skip = i
            break
    
    del lines[start_skip:end_skip]

with open("ui/batch_mode.py", "w") as f:
    f.writelines(lines)

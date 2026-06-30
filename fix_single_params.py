import re

with open("backup_single_mode.py", "r") as f:
    single_old = f.read()

# Extract get_rib_parameters from backup
match_single = re.search(r'(    def get_rib_parameters\(self, fast_mode=False\) -> RibParameters:.*?)(?=\n    def update_preview)', single_old, re.DOTALL)
if match_single:
    single_original_method = match_single.group(1)
    
    with open("ui/single_mode.py", "r") as f:
        single_new = f.read()
    
    # In my rewrite of single_mode, I put a generic _get_builder_params. I should replace it with get_rib_parameters.
    start_idx = single_new.find("    def _get_builder_params(self):")
    if start_idx != -1:
        end_idx = single_new.find("    def create_widgets(self):", start_idx)
        if end_idx != -1:
            single_new = single_new[:start_idx] + single_original_method + "\n" + single_new[end_idx:]
            
            with open("ui/single_mode.py", "w") as f:
                f.write(single_new)
            print("Successfully restored get_rib_parameters in single_mode.py")
else:
    print("Failed to find get_rib_parameters in backup_single_mode.py")

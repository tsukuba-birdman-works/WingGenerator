import re

# 1. Fix batch_mode.py
with open("backup_batch_mode.py", "r") as f:
    batch_old = f.read()

# Extract _get_builder_params from backup
match_batch = re.search(r'(    def _get_builder_params\(self\):.*?)(?=\n    def export_gcode_all)', batch_old, re.DOTALL)
if match_batch:
    batch_original_method = match_batch.group(1)
    
    with open("ui/batch_mode.py", "r") as f:
        batch_new = f.read()
    
    # Replace the current _get_builder_params with the original one
    # First find where it starts and ends in the new file
    start_idx = batch_new.find("    def _get_builder_params(self):")
    if start_idx != -1:
        end_idx = batch_new.find("    def create_widgets(self):", start_idx)
        if end_idx != -1:
            batch_new = batch_new[:start_idx] + batch_original_method + "\n" + batch_new[end_idx:]
            
            with open("ui/batch_mode.py", "w") as f:
                f.write(batch_new)
            print("Successfully restored _get_builder_params in batch_mode.py")
else:
    print("Failed to find _get_builder_params in backup_batch_mode.py")

# 2. Fix single_mode.py
with open("backup_single_mode.py", "r") as f:
    single_old = f.read()

# Extract get_rib_parameters from backup
match_single = re.search(r'(    def get_rib_parameters\(self, fast_mode=False\):.*?)(?=\n    def update_preview)', single_old, re.DOTALL)
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


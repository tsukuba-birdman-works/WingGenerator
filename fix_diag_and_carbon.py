import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

# Remove unused carbon variables and outer TE cuts
code = re.sub(r"    \{'id': '(carbon_le_cut|carbon_offset|carbon_te_cut|cr_root_out_te|cr_tip_out_te)',.*?\},\n", "", code)

# We will just write a python script to process BATCH_PARAMS and SINGLE_PARAMS

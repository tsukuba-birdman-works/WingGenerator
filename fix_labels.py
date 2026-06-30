import re

with open("ui/param_spec.py", "r") as f:
    code = f.read()

label_map = {
    'plank_start': 'Actual Start (%)',
    'plank_end': 'Actual End (%)',
    'plank_part_start': 'Cut Start (%)',
    'plank_part_end': 'Cut End (%)',
    'plank_thick': 'Thickness (mm)',
    'te_cut': 'Cut from TE Edge (mm)',
    'te_cap_thick': 'Carbon Cap Thick (mm)',
    'te_cap_uf_act': 'Upper Front (Active)',
    'te_cap_uf_w': 'Upper Front Width',
    'te_cap_uf_d': 'Upper Front Depth (Double)',
    'te_cap_lf_act': 'Lower Front (Active)',
    'te_cap_lf_w': 'Lower Front Width',
    'te_cap_lf_d': 'Lower Front Depth (Double)',
    'te_cap_ur_act': 'Upper Rear (Active)',
    'te_cap_ur_w': 'Upper Rear Width',
    'te_cap_lr_act': 'Lower Rear (Active)',
    'te_cap_lr_w': 'Lower Rear Width',
}

for k, v in label_map.items():
    code = re.sub(rf"('id': '{k}'.*?'label': )'[^']+'", rf"\g<1>'{v}'", code)

with open("ui/param_spec.py", "w") as f:
    f.write(code)

print("Updated Plank and TE labels!")

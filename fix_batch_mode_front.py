with open('ui/batch_mode.py', 'r') as f:
    text = f.read()

old_params = " 'front_spar_dx', 'front_spar_dy',"
new_params = " 'front_spar_dx', 'front_spar_dy', 'front_spar_dx_root', 'front_spar_dy_root', 'front_spar_dx_tip', 'front_spar_dy_tip',"
if old_params in text:
    text = text.replace(old_params, new_params)
    with open('ui/batch_mode.py', 'w') as f:
        f.write(text)
        print("Replaced successfully")
else:
    print("Already updated or not found")

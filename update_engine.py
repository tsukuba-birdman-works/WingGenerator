import re

with open('core/engine.py', 'r') as f:
    text = f.read()

target_spars = """        # Calculate interpolated positions for spars
        front_dx_root = p.get('front_spar_dx_root', p.get('front_spar_dx', 0.0))
        front_dx_tip = p.get('front_spar_dx_tip', p.get('front_spar_dx', 0.0))
        front_dy_root = p.get('front_spar_dy_root', p.get('front_spar_dy', 0.0))
        front_dy_tip = p.get('front_spar_dy_tip', p.get('front_spar_dy', 0.0))
        front_dx = front_dx_root * (1 - blend) + front_dx_tip * blend
        front_dy = front_dy_root * (1 - blend) + front_dy_tip * blend

        rear_dx_root = p.get('rear_spar_dx_root', p.get('rear_spar_dx', 0.0))
        rear_dx_tip = p.get('rear_spar_dx_tip', p.get('rear_spar_dx', 0.0))
        rear_dy_root = p.get('rear_spar_dy_root', p.get('rear_spar_dy', 0.0))
        rear_dy_tip = p.get('rear_spar_dy_tip', p.get('rear_spar_dy', 0.0))
        rear_dx = rear_dx_root * (1 - blend) + rear_dx_tip * blend
        rear_dy = rear_dy_root * (1 - blend) + rear_dy_tip * blend"""

replacement_spars = """        # Calculate interpolated positions for spars
        front_dx_root = p.get('front_spar_dx_root')
        if front_dx_root is None: front_dx_root = p.get('front_spar_dx')
        front_dx_tip = p.get('front_spar_dx_tip')
        if front_dx_tip is None: front_dx_tip = p.get('front_spar_dx')
        front_dy_root = p.get('front_spar_dy_root')
        if front_dy_root is None: front_dy_root = p.get('front_spar_dy')
        front_dy_tip = p.get('front_spar_dy_tip')
        if front_dy_tip is None: front_dy_tip = p.get('front_spar_dy')
        
        if None in (front_dx_root, front_dx_tip, front_dy_root, front_dy_tip):
            p['front_spar_dia'] = -1.0
            front_dx_root = front_dx_tip = front_dy_root = front_dy_tip = 0.0

        front_dx = front_dx_root * (1 - blend) + front_dx_tip * blend
        front_dy = front_dy_root * (1 - blend) + front_dy_tip * blend

        rear_dx_root = p.get('rear_spar_dx_root')
        if rear_dx_root is None: rear_dx_root = p.get('rear_spar_dx')
        rear_dx_tip = p.get('rear_spar_dx_tip')
        if rear_dx_tip is None: rear_dx_tip = p.get('rear_spar_dx')
        rear_dy_root = p.get('rear_spar_dy_root')
        if rear_dy_root is None: rear_dy_root = p.get('rear_spar_dy')
        rear_dy_tip = p.get('rear_spar_dy_tip')
        if rear_dy_tip is None: rear_dy_tip = p.get('rear_spar_dy')

        if None in (rear_dx_root, rear_dx_tip, rear_dy_root, rear_dy_tip):
            p['rear_spar_dia'] = -1.0
            rear_dx_root = rear_dx_tip = rear_dy_root = rear_dy_tip = 0.0

        rear_dx = rear_dx_root * (1 - blend) + rear_dx_tip * blend
        rear_dy = rear_dy_root * (1 - blend) + rear_dy_tip * blend"""

if target_spars in text:
    text = text.replace(target_spars, replacement_spars)
    print("Spars replaced.")
else:
    print("Spars not found!")

target_bolts = """        root_bolt1, root_bolt2 = p.get('root_bolt1', (0,0,0)), p.get('root_bolt2', (0,0,0))
        tip_bolt1, tip_bolt2 = p.get('tip_bolt1', (0,0,0)), p.get('tip_bolt2', (0,0,0))
        b1_dx = root_bolt1[0] * (1 - blend) + tip_bolt1[0] * blend
        b1_dy = root_bolt1[1] * (1 - blend) + tip_bolt1[1] * blend
        bolt1_dia = root_bolt1[2] * (1 - blend) + tip_bolt1[2] * blend
        b2_dx = root_bolt2[0] * (1 - blend) + tip_bolt2[0] * blend
        b2_dy = root_bolt2[1] * (1 - blend) + tip_bolt2[1] * blend
        bolt2_dia = root_bolt2[2] * (1 - blend) + tip_bolt2[2] * blend"""

replacement_bolts = """        root_bolt1, root_bolt2 = p.get('root_bolt1', (None,None,-1.0)), p.get('root_bolt2', (None,None,-1.0))
        tip_bolt1, tip_bolt2 = p.get('tip_bolt1', (None,None,-1.0)), p.get('tip_bolt2', (None,None,-1.0))
        
        if None in (root_bolt1[0], root_bolt1[1], tip_bolt1[0], tip_bolt1[1]):
            bolt1_dia = -1.0
            b1_dx, b1_dy = 0.0, 0.0
        else:
            b1_dx = root_bolt1[0] * (1 - blend) + tip_bolt1[0] * blend
            b1_dy = root_bolt1[1] * (1 - blend) + tip_bolt1[1] * blend
            bolt1_dia = root_bolt1[2] * (1 - blend) + tip_bolt1[2] * blend

        if None in (root_bolt2[0], root_bolt2[1], tip_bolt2[0], tip_bolt2[1]):
            bolt2_dia = -1.0
            b2_dx, b2_dy = 0.0, 0.0
        else:
            b2_dx = root_bolt2[0] * (1 - blend) + tip_bolt2[0] * blend
            b2_dy = root_bolt2[1] * (1 - blend) + tip_bolt2[1] * blend
            bolt2_dia = root_bolt2[2] * (1 - blend) + tip_bolt2[2] * blend"""

if target_bolts in text:
    text = text.replace(target_bolts, replacement_bolts)
    print("Bolts replaced.")
else:
    print("Bolts not found!")

with open('core/engine.py', 'w') as f:
    f.write(text)


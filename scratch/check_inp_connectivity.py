def check_connectivity(inp_file):
    with open(inp_file, 'r') as f:
        lines = f.readlines()
        
    elem_to_nodes = {}
    reading_els = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('*ELEMENT, TYPE=CPS3, ELSET=EALL'):
            reading_els = True
            continue
        elif line.startswith('*'):
            reading_els = False
            
        if reading_els and line:
            parts = line.split(',')
            elem_to_nodes[int(parts[0])] = [int(p) for p in parts[1:]]
            
    rib_els = []
    plank_els = []
    current_set = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('*ELSET, ELSET=EALL_RIB'):
            current_set = 'rib'
            continue
        elif line.startswith('*ELSET, ELSET=EALL_PLANK'):
            current_set = 'plank'
            continue
        elif line.startswith('*'):
            current_set = None
            
        if current_set == 'rib' and line:
            parts = line.split(',')
            rib_els.extend([int(p) for p in parts if p.strip()])
        elif current_set == 'plank' and line:
            parts = line.split(',')
            plank_els.extend([int(p) for p in parts if p.strip()])
            
    rib_nodes = set()
    for e in rib_els:
        rib_nodes.update(elem_to_nodes[e])
        
    plank_nodes = set()
    for e in plank_els:
        plank_nodes.update(elem_to_nodes[e])
        
    shared = rib_nodes.intersection(plank_nodes)
    print(f"Rib nodes: {len(rib_nodes)}")
    print(f"Plank nodes: {len(plank_nodes)}")
    print(f"Shared nodes: {len(shared)}")

check_connectivity('rib_fea.inp')

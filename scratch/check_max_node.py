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
            
    all_nodes = set()
    for n_list in elem_to_nodes.values():
        all_nodes.update(n_list)
        
    print(f"Max node ID: {max(all_nodes)}")

check_connectivity('rib_fea.inp')

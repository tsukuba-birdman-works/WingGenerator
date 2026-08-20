def check_unused(inp_file):
    with open(inp_file, 'r') as f:
        lines = f.readlines()
        
    elem_to_nodes = {}
    reading_els = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('*ELEMENT'):
            reading_els = True
            continue
        elif line.startswith('*'):
            reading_els = False
            
        if reading_els and line:
            parts = line.split(',')
            elem_to_nodes[int(parts[0])] = [int(p) for p in parts[1:]]
            
    used_nodes = set()
    for n_list in elem_to_nodes.values():
        used_nodes.update(n_list)
        
    all_nodes = set()
    reading_nodes = False
    for line in lines:
        line = line.strip()
        if line.startswith('*NODE'):
            reading_nodes = True
            continue
        elif line.startswith('*'):
            reading_nodes = False
            
        if reading_nodes and line:
            parts = line.split(',')
            all_nodes.add(int(parts[0]))
            
    unused = all_nodes - used_nodes
    print(f"Total nodes: {len(all_nodes)}")
    print(f"Used nodes: {len(used_nodes)}")
    print(f"Unused nodes: {len(unused)}")

check_unused('rib_fea.inp')

import json

with open("scratch/test_pbr.glb", "rb") as f:
    magic = f.read(4)
    version = int.from_bytes(f.read(4), 'little')
    length = int.from_bytes(f.read(4), 'little')
    json_chunk_length = int.from_bytes(f.read(4), 'little')
    json_chunk_type = f.read(4)
    json_data = f.read(json_chunk_length)
    gltf = json.loads(json_data.decode('utf-8'))
    
print(json.dumps(gltf.get('materials', []), indent=2))

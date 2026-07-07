with open('ui/single_mode.py', 'r') as f:
    text = f.read()

text = text.replace('trimesh library is required for 3D export.\nPlease run', 'trimesh library is required for 3D export.\\nPlease run')

with open('ui/single_mode.py', 'w') as f:
    f.write(text)

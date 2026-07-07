with open('ui/single_mode.py', 'r') as f:
    text = f.read()

text = text.replace('f"Saved to:\n{path}"', 'f"Saved to:\\n{path}"')
text = text.replace('f"Saved 3D Model to:\n{filepath}"', 'f"Saved 3D Model to:\\n{filepath}"')

with open('ui/single_mode.py', 'w') as f:
    f.write(text)

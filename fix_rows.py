with open('ui/foam_mode.py', 'r') as f:
    content = f.read()

# Change Smooth curves from row=8 to row=9
content = content.replace('.grid(row=8, column=1, sticky="w", pady=2)', '.grid(row=9, column=1, sticky="w", pady=2)')

with open('ui/foam_mode.py', 'w') as f:
    f.write(content)

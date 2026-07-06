with open('core/foam_engine.py', 'r') as f:
    content = f.read()

if 'import numpy as np' not in content:
    content = "import numpy as np\n" + content

with open('core/foam_engine.py', 'w') as f:
    f.write(content)

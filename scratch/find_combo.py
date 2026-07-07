import re
with open('/home/akihito-kasai/Desktop/tbw/Ribgenerator/ui/batch_mode.py', 'r') as f:
    text = f.read()
print("combo_foam_start in batch_mode.py:")
for m in re.finditer(r'.*combo_foam_start.*', text):
    print(m.group(0))

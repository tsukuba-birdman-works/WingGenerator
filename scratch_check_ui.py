import re

def get_entry_vars(filepath):
    vars = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match tk.Entry or ttk.Entry with textvariable=self.some_var
    matches = re.findall(r'Entry\([^)]*textvariable=self\.([a-zA-Z0-9_]+)[^)]*\)', content)
    vars.update(matches)
    
    # Match Checkbutton with variable=self.some_var
    matches_cb = re.findall(r'Checkbutton\([^)]*variable=self\.([a-zA-Z0-9_]+)[^)]*\)', content)
    vars.update(matches_cb)
    
    return vars

old_vars = get_entry_vars('/home/akihito-kasai/.config/Code/User/History/50b3bc30/EYfi.py')
new_vars = get_entry_vars('ui/batch_mode.py')
base_vars = get_entry_vars('ui/base_mode.py')
new_vars.update(base_vars)

missing = old_vars - new_vars
added = new_vars - old_vars

print("Variables with input fields missing in new UI:")
for m in sorted(missing):
    print(" -", m)

print("\nVariables with input fields added in new UI:")
for a in sorted(added):
    print(" -", a)

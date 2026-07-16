import re
with open('core/engine.py', 'r') as f:
    content = f.read()

# I will change the cap position back to what it might be, or exactly te_start
# Let's look at the actual current code
print(re.search(r'te_start = te_cut \+ 10\.0.*?\n.*?zones = \[\]\n.*?if f_act', content, re.DOTALL).group(0))

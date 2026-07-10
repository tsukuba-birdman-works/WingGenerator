with open('core/engine.py', 'r') as f:
    text = f.read()

if "te_cut_overlap = te_cut + 10.0" in text:
    print("Overlap is present")
else:
    print("Overlap is missing!")

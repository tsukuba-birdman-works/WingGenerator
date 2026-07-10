with open('core/engine.py', 'r') as f:
    text = f.read()

if "te_unrot = te_unrot[::-1]" in text:
    print("Winding reversal is present")
else:
    print("Winding reversal is missing!")

if "te_cut_overlap = te_cut + 10.0" in text:
    print("Overlap is present")
else:
    print("Overlap is missing!")

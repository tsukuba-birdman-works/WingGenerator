import ezdxf

doc = ezdxf.readfile("/tmp/All_In_One.dxf")
layers = {}
for e in doc.modelspace():
    l = e.dxf.layer
    layers[l] = layers.get(l, 0) + 1

for l, count in layers.items():
    print(f"Layer {l}: {count} entities")

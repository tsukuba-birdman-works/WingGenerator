import ezdxf

doc = ezdxf.readfile("/tmp/All_In_One.dxf")
jig_entities = [e for e in doc.modelspace() if e.dxf.layer == "JIG"]
print(f"Number of JIG entities: {len(jig_entities)}")

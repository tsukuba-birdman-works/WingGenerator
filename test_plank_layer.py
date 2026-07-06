import ezdxf

doc = ezdxf.readfile("/tmp/All_In_One.dxf")
plank_entities = [e for e in doc.modelspace() if e.dxf.layer == "PLANK"]
holes_entities = [e for e in doc.modelspace() if e.dxf.layer == "HOLES"]
outline_entities = [e for e in doc.modelspace() if e.dxf.layer == "RIB_OUTLINE"]
print(f"Number of PLANK entities: {len(plank_entities)}")
print(f"Number of HOLES entities: {len(holes_entities)}")
print(f"Number of RIB_OUTLINE entities: {len(outline_entities)}")

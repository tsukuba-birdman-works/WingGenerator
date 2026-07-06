import ezdxf

doc = ezdxf.new('R2010')
try:
    doc.layers.add(name='RIB_OUTLINE', color=7)
    doc.layers.add(name='RIB_OUTLINE', color=7)
except Exception as e:
    print(f"Exception: {type(e).__name__} - {e}")

try:
    doc.layers.new(name='RIB_OUTLINE2', dxfattribs={'color': 7})
    doc.layers.new(name='RIB_OUTLINE2', dxfattribs={'color': 7})
except Exception as e:
    print(f"Exception2: {type(e).__name__} - {e}")


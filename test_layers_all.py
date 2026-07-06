import ezdxf

doc = ezdxf.new('R2010')
print("RIB_OUTLINE in doc.layers:", 'RIB_OUTLINE' in doc.layers)
doc.layers.add('RIB_OUTLINE', color=7)
print("RIB_OUTLINE in doc.layers (after add):", 'RIB_OUTLINE' in doc.layers)

try:
    if 'RIB_OUTLINE' not in doc.layers: doc.layers.add(name='RIB_OUTLINE', color=7)
    print("Second add with 'not in' check OK")
except Exception as e:
    print("Error:", type(e), e)

try:
    doc.layers.add(name='RIB_OUTLINE', color=7)
except Exception as e:
    print("Error on direct add:", type(e), e)

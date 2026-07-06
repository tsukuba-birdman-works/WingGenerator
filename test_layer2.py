import ezdxf

doc = ezdxf.new('R2010')
doc.layers.add(name='RIB_OUTLINE', color=7)
print("RIB_OUTLINE in layers:", 'RIB_OUTLINE' in doc.layers)

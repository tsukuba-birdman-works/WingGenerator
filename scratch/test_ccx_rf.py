with open('/home/akihito-kasai/Desktop/tbw/Ribgenerator/rib_fea.inp', 'r') as f:
    inp = f.read()
inp = inp.replace("*NODE PRINT, NSET=NALL\nU", "*NODE PRINT, NSET=FIXED\nRF\n*NODE PRINT, NSET=NALL\nU")
with open('rib_fea.inp', 'w') as f:
    f.write(inp)

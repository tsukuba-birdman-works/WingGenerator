from core.engine import RibGeneratorEngine
eng = RibGeneratorEngine()
p = {
    'file1': 'dummy.dat', 'file2': 'dummy.dat',
    'chord_root': 200, 'chord_tip': 200,
    'wing_span': 1000, 'te_cut': 10,
    'front_spar_dia': 8, 'spar_hole_dia': 12, 'rear_spar_dia': 10,
    'spar_pos': 30, 'front_spar_dx': -50, 'front_spar_dy': 5,
    'rear_spar_dx': 50, 'rear_spar_dy': 2,
    'jig_base_height': 100, 'jig_slot_interval': 100,
    'jig_slot_width': 3, 'jig_slot_depth': 10
}
import urllib.request
import os
if not os.path.exists('dummy.dat'):
    urllib.request.urlretrieve('http://airfoiltools.com/airfoil/seligdatfile?airfoil=naca0012-il', 'dummy.dat')
res = eng.generate_jig_at_y(p, 50, return_full=True)
if res:
    print("Jig generation OK!")
    print(len(res['jig_pts']), "points in jig")
else:
    print("Jig generation failed!")

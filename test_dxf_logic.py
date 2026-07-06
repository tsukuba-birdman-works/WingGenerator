import sys
import ezdxf
import numpy as np

# Mocking the engine export_dxf function
def export_dxf(filepath, origin, rib_pts, c_m, d_m, c_f, d_f, c_r, d_r, truss_holes, xb_centers, d_xb, plank_poly, te_part, c_b1, d_b1, hole_b1, c_b2, d_b2, hole_b2, diag_poly_pts_list, te_cap_pts_list=None, rc_cap_pts_list=None, jig_pts=None):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    try:
        doc.layers.add(name='RIB_OUTLINE', color=7)
        doc.layers.add(name='HOLES', color=1)
        doc.layers.add(name='TRUSS', color=2)
        doc.layers.add(name='PLANK', color=3)
        doc.layers.add(name='TE_PART', color=4)
        doc.layers.add(name='JIG_OUTLINE', color=5)
    except AttributeError:
        doc.layers.new(name='RIB_OUTLINE', dxfattribs={'color': 7})
        doc.layers.new(name='HOLES', dxfattribs={'color': 1})
        doc.layers.new(name='TRUSS', dxfattribs={'color': 2})
        doc.layers.new(name='PLANK', dxfattribs={'color': 3})
        doc.layers.new(name='TE_PART', dxfattribs={'color': 4})
        doc.layers.new(name='JIG_OUTLINE', dxfattribs={'color': 5})

    origin_pt = np.array(origin)
    def shift_poly(poly): return [(float(pt[0] - origin_pt[0]), float(pt[1] - origin_pt[1])) for pt in poly]
    
    if jig_pts is not None and len(jig_pts) > 0: 
        msp.add_lwpolyline(shift_poly(jig_pts), close=True, dxfattribs={'layer': 'JIG_OUTLINE'})

export_dxf("dummy.dxf", (0,0), [], (0,0), 0, (0,0), 0, (0,0), 0, [], [], 0, [], [], (0,0), 0, False, (0,0), 0, False, [], None, None, [(0,0), (1,1), (2,0)])
print("Test passed")

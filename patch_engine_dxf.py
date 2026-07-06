with open('core/engine.py', 'r') as f:
    content = f.read()

import re

old_export_dxf_sig = r"""    def export_dxf\(self, filepath, origin, rib_pts, c_m, d_m, c_f, d_f, c_r, d_r, truss_holes, xb_centers, d_xb, plank_poly, te_part, c_b1, d_b1, hole_b1, c_b2, d_b2, hole_b2, diag_poly_pts_list, te_cap_pts_list=None, rc_cap_pts_list=None\):
        if ezdxf is None: raise ImportError\("ezdxf is required."\)
        doc = ezdxf.new\('R2010'\)
        msp = doc.modelspace\(\)"""

new_export_dxf_sig = """    def export_dxf(self, filepath, origin, rib_pts, c_m, d_m, c_f, d_f, c_r, d_r, truss_holes, xb_centers, d_xb, plank_poly, te_part, c_b1, d_b1, hole_b1, c_b2, d_b2, hole_b2, diag_poly_pts_list, te_cap_pts_list=None, rc_cap_pts_list=None, doc=None, msp=None, export_flags=None):
        if ezdxf is None: raise ImportError("ezdxf is required.")
        if export_flags is None: export_flags = {}
        is_new_doc = (doc is None)
        if doc is None:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()"""
content = re.sub(old_export_dxf_sig, new_export_dxf_sig, content, flags=re.MULTILINE)

# Now we need to wrap the layers with export_flags
old_layers = r"""        if len\(rib_pts\) > 0: msp.add_lwpolyline\(shift_poly\(rib_pts\), close=True, dxfattribs=\{'layer': 'RIB_OUTLINE'\}\)
        if d_m > 0: msp.add_circle\(center=shift\(c_m\), radius=d_m/2.0, dxfattribs=\{'layer': 'HOLES'\}\)
        if d_f > 0: msp.add_circle\(center=shift\(c_f\), radius=d_f/2.0, dxfattribs=\{'layer': 'HOLES'\}\)
        if d_r > 0: msp.add_circle\(center=shift\(c_r\), radius=d_r/2.0, dxfattribs=\{'layer': 'HOLES'\}\)
        if d_b1 > 0: msp.add_circle\(center=shift\(c_b1\), radius=d_b1/2.0, dxfattribs=\{'layer': 'HOLES'\}\)
        if d_b2 > 0: msp.add_circle\(center=shift\(c_b2\), radius=d_b2/2.0, dxfattribs=\{'layer': 'HOLES'\}\)
        for c in xb_centers: msp.add_circle\(center=shift\(c\), radius=d_xb/2.0, dxfattribs=\{'layer': 'TRUSS'\}\)
        for h in truss_holes: msp.add_lwpolyline\(shift_poly\(h\), close=True, dxfattribs=\{'layer': 'TRUSS'\}\)
        if len\(plank_poly\) > 0: msp.add_lwpolyline\(shift_poly\(plank_poly\), close=True, dxfattribs=\{'layer': 'PLANK'\}\)
        if len\(te_part\) > 0: msp.add_lwpolyline\(shift_poly\(te_part\), close=True, dxfattribs=\{'layer': 'TE_PART'\}\)
        for diag_poly_pts in diag_poly_pts_list:
            if len\(diag_poly_pts\) > 0: msp.add_lwpolyline\(shift_poly\(diag_poly_pts\), close=True, dxfattribs=\{'layer': 'HOLES'\}\)

        if te_cap_pts_list is not None:
            try: doc.layers.add\(name='TE_CAPS', color=6\)
            except AttributeError: doc.layers.new\(name='TE_CAPS', dxfattribs=\{'color': 6\}\)
            for cap_pts in te_cap_pts_list:
                if len\(cap_pts\) > 0: msp.add_lwpolyline\(shift_poly\(cap_pts\), close=True, dxfattribs=\{'layer': 'TE_CAPS'\}\)

        if rc_cap_pts_list is not None:
            try: doc.layers.add\(name='RIB_CAPS', color=5\)
            except AttributeError: doc.layers.new\(name='RIB_CAPS', dxfattribs=\{'color': 5\}\)
            for cap_pts in rc_cap_pts_list\[0\] \+ rc_cap_pts_list\[1\]:
                if len\(cap_pts\) > 0: msp.add_lwpolyline\(shift_poly\(cap_pts\), close=True, dxfattribs=\{'layer': 'RIB_CAPS'\}\)

        doc.saveas\(filepath\)"""

new_layers = """        if export_flags.get('dxf_part_outline', True):
            if len(rib_pts) > 0: msp.add_lwpolyline(shift_poly(rib_pts), close=True, dxfattribs={'layer': 'RIB_OUTLINE'})
        if export_flags.get('dxf_part_holes', True):
            if d_m > 0: msp.add_circle(center=shift(c_m), radius=d_m/2.0, dxfattribs={'layer': 'HOLES'})
            if d_f > 0: msp.add_circle(center=shift(c_f), radius=d_f/2.0, dxfattribs={'layer': 'HOLES'})
            if d_r > 0: msp.add_circle(center=shift(c_r), radius=d_r/2.0, dxfattribs={'layer': 'HOLES'})
            if d_b1 > 0: msp.add_circle(center=shift(c_b1), radius=d_b1/2.0, dxfattribs={'layer': 'HOLES'})
            if d_b2 > 0: msp.add_circle(center=shift(c_b2), radius=d_b2/2.0, dxfattribs={'layer': 'HOLES'})
            for diag_poly_pts in diag_poly_pts_list:
                if len(diag_poly_pts) > 0: msp.add_lwpolyline(shift_poly(diag_poly_pts), close=True, dxfattribs={'layer': 'HOLES'})
        if export_flags.get('dxf_part_truss', True):
            for c in xb_centers: msp.add_circle(center=shift(c), radius=d_xb/2.0, dxfattribs={'layer': 'TRUSS'})
            for h in truss_holes: msp.add_lwpolyline(shift_poly(h), close=True, dxfattribs={'layer': 'TRUSS'})
        if export_flags.get('dxf_part_plank', True):
            if len(plank_poly) > 0: msp.add_lwpolyline(shift_poly(plank_poly), close=True, dxfattribs={'layer': 'PLANK'})
        if export_flags.get('dxf_part_te', True):
            if len(te_part) > 0: msp.add_lwpolyline(shift_poly(te_part), close=True, dxfattribs={'layer': 'TE_PART'})
        if export_flags.get('dxf_part_caps', True):
            if te_cap_pts_list is not None:
                try: doc.layers.add(name='TE_CAPS', color=6)
                except AttributeError: doc.layers.new(name='TE_CAPS', dxfattribs={'color': 6})
                for cap_pts in te_cap_pts_list:
                    if len(cap_pts) > 0: msp.add_lwpolyline(shift_poly(cap_pts), close=True, dxfattribs={'layer': 'TE_CAPS'})
            if rc_cap_pts_list is not None:
                try: doc.layers.add(name='RIB_CAPS', color=5)
                except AttributeError: doc.layers.new(name='RIB_CAPS', dxfattribs={'color': 5})
                for cap_pts in rc_cap_pts_list[0] + rc_cap_pts_list[1]:
                    if len(cap_pts) > 0: msp.add_lwpolyline(shift_poly(cap_pts), close=True, dxfattribs={'layer': 'RIB_CAPS'})

        if is_new_doc:
            doc.saveas(filepath)"""
content = re.sub(old_layers, new_layers, content, flags=re.MULTILINE)

# Also update export_single_poly_dxf
old_single_poly = r"""    def export_single_poly_dxf\(self, filepath, poly_pts, origin\):
        if ezdxf is None: raise ImportError\("ezdxf is required."\)
        doc = ezdxf.new\('R2010'\)
        msp = doc.modelspace\(\)
        try: doc.layers.add\(name='JIG', color=7\)
        except AttributeError: doc.layers.new\(name='JIG', dxfattribs=\{'color': 7\}\)
        origin_pt = np.array\(origin\)
        def shift_poly\(poly\): return \[\(float\(pt\[0\] - origin_pt\[0\]\), float\(pt\[1\] - origin_pt\[1\]\)\) for pt in poly\]
        if len\(poly_pts\) > 0:
            msp.add_lwpolyline\(shift_poly\(poly_pts\), close=True, dxfattribs=\{'layer': 'JIG'\}\)
        doc.saveas\(filepath\)"""

new_single_poly = """    def export_single_poly_dxf(self, filepath, poly_pts, origin, doc=None, msp=None):
        if ezdxf is None: raise ImportError("ezdxf is required.")
        is_new_doc = (doc is None)
        if doc is None:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
        try: doc.layers.add(name='JIG', color=7)
        except AttributeError: doc.layers.new(name='JIG', dxfattribs={'color': 7})
        origin_pt = np.array(origin)
        def shift_poly(poly): return [(float(pt[0] - origin_pt[0]), float(pt[1] - origin_pt[1])) for pt in poly]
        if len(poly_pts) > 0:
            msp.add_lwpolyline(shift_poly(poly_pts), close=True, dxfattribs={'layer': 'JIG'})
        if is_new_doc:
            doc.saveas(filepath)"""
content = re.sub(old_single_poly, new_single_poly, content, flags=re.MULTILINE)

with open('core/engine.py', 'w') as f:
    f.write(content)


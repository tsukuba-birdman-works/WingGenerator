import re

with open('patch_jig_temp.py', 'r') as f:
    orig = f.read()

old_spar_cut = """        # Cut spar holes (U shaped)
        if d_f > 0:
            f_hole = Point(c_f).buffer(d_f/2.0)
            f_cut = box(c_f[0] - d_f, c_f[1], c_f[0] + d_f, c_f[1] + d_f)
            frame = frame.difference(f_hole.union(f_cut))

        if d_m > 0:
            m_hole = Point(c_m).buffer(d_m/2.0)
            m_cut = box(c_m[0] - d_m, c_m[1], c_m[0] + d_m, c_m[1] + d_m)
            frame = frame.difference(m_hole.union(m_cut))

        if d_r > 0:
            r_hole = Point(c_r).buffer(d_r/2.0)
            r_cut = box(c_r[0] - d_r, c_r[1], c_r[0] + d_r, c_r[1] + d_r)
            frame = frame.difference(r_hole.union(r_cut))"""

new_spar_cut = """        # Cut spar holes (60% box shaped)
        if d_f > 0:
            bw = 0.6 * d_f
            f_cut = box(c_f[0] - bw/2.0, c_f[1] - d_f/2.0, c_f[0] + bw/2.0, c_f[1] + d_f)
            frame = frame.difference(f_cut)

        if d_m > 0:
            bw = 0.6 * d_m
            m_cut = box(c_m[0] - bw/2.0, c_m[1] - d_m/2.0, c_m[0] + bw/2.0, c_m[1] + d_m)
            frame = frame.difference(m_cut)

        if d_r > 0:
            bw = 0.6 * d_r
            r_cut = box(c_r[0] - bw/2.0, c_r[1] - d_r/2.0, c_r[0] + bw/2.0, c_r[1] + d_r)
            frame = frame.difference(r_cut)"""

if old_spar_cut in orig:
    orig = orig.replace(old_spar_cut, new_spar_cut)
else:
    print("WARNING: old_spar_cut not found!")

with open('patch_jig_temp.py', 'w') as f:
    f.write(orig)

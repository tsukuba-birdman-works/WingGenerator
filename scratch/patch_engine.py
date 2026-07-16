with open("core/engine.py", "r") as f:
    code = f.read()

# Replace process_blocks_sharp inner loop
old_code = """
        def process_side(blocks, is_rear):
            for b in blocks:
                for idx, b_item in enumerate(b):
                    if not b_item: continue
                    rb = [( (np.array(l[0])-[spar_x, spar_y]).dot(R_mat.T)+[spar_x, spar_y],
                            (np.array(l[1])-[spar_x, spar_y]).dot(R_mat.T)+[spar_x, spar_y] ) for l in b_item]

                    c1, c2 = ('right', 'left') if is_rear else ('left', 'right')
                    canvas = self.cut_polygon_by_line(inner_poly, rb[0][0], rb[0][1], c1)
                    canvas = self.cut_polygon_by_line(canvas, rb[-1][0], rb[-1][1], c2)

                    webs = []
                    for l in rb[1:-1]:
                        p1, p2 = np.array(l[0]), np.array(l[1])
                        vec = p2 - p1
                        if np.linalg.norm(vec) > 0:
                            vec = vec / np.linalg.norm(vec)
                            w_line = LineString([p1 - vec * 10000, p2 + vec * 10000])
                            try: webs.append(w_line.buffer(beam_width / 2.0).buffer(0))
                            except Exception: pass

                    if webs:
                        try:
                            safe_webs = unary_union(webs).buffer(0)
                            canvas = canvas.buffer(0).difference(safe_webs).buffer(0)
                        except Exception: pass

                    for p in ([canvas] if getattr(canvas, 'geom_type', '') == 'Polygon' else list(getattr(canvas, 'geoms', []))):
                        if getattr(p, 'geom_type', '') == 'Polygon' and p.area > 5.0:
                            sharp_polys.append(p)
"""

new_code = """
        def process_side(blocks, is_rear):
            for b in blocks:
                for idx, b_item in enumerate(b):
                    if not b_item: continue
                    rb = [( (np.array(l[0])-[spar_x, spar_y]).dot(R_mat.T)+[spar_x, spar_y],
                            (np.array(l[1])-[spar_x, spar_y]).dot(R_mat.T)+[spar_x, spar_y] ) for l in b_item]

                    c1, c2 = ('right', 'left') if is_rear else ('left', 'right')
                    canvas = self.cut_polygon_by_line(inner_poly, rb[0][0], rb[0][1], c1)
                    canvas = self.cut_polygon_by_line(canvas, rb[-1][0], rb[-1][1], c2)

                    webs = []
                    for l in rb[1:-1]:
                        p1, p2 = np.array(l[0]), np.array(l[1])
                        vec = p2 - p1
                        if np.linalg.norm(vec) > 0:
                            vec = vec / np.linalg.norm(vec)
                            w_line = LineString([p1 - vec * 10000, p2 + vec * 10000])
                            try: webs.append(w_line.buffer(beam_width / 2.0).buffer(0))
                            except Exception: pass

                    if webs:
                        try:
                            safe_webs = unary_union(webs).buffer(0)
                            canvas = canvas.buffer(0).difference(safe_webs).buffer(0)
                        except Exception: pass

                    for p in ([canvas] if getattr(canvas, 'geom_type', '') == 'Polygon' else list(getattr(canvas, 'geoms', []))):
                        if getattr(p, 'geom_type', '') == 'Polygon' and p.area > 5.0:
                            sharp_polys.append((p, is_rear, idx))
"""
if old_code in code:
    code = code.replace(old_code, new_code)
    with open("core/engine.py", "w") as f:
        f.write(code)
    print("Replaced process_side")
else:
    print("process_side not found")


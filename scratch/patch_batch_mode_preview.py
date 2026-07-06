import re

with open('ui/batch_mode.py', 'r') as f:
    content = f.read()

update_code_find = """        try:
            p = self._get_builder_params()
            p['fast_mode'] = fast_mode
            res = self.engine.generate_rib_at_y(p, y_local, idx, t_rib, is_carbon=is_carbon, te_cut_override=te_cut_val)
            self.last_warnings = res.warnings_list
            chord, spar_pct, washout, blend, local_xb_pct, x_dia = self.get_local_params(y_local)
            angle = p['truss_angles_dict'].get(idx, p['base_truss_angle'])
            title = f"{item['label']} - Chord: {chord:.1f}mm, Washout: {washout:.2f}°, Truss: {angle:.1f}°" + (" [FAST PREVIEW]" if fast_mode else "")
            self.draw_plot(*res[:12], self.last_warnings, res.plank_poly_rot, res.te_part_coords, res.c_b1, res.hole_b1, res.c_b2, res.hole_b2, res.diag_poly_pts_list, res.final_rib_orig, title, res.te_cap_pts_list, res.rc_cap_pts_list)
        except Exception as e: print("Preview Error:", e)"""

update_code_replace = """        try:
            p = self._get_builder_params()
            p['fast_mode'] = fast_mode
            
            if item.get('type') == 'jig':
                res_jig = self.engine.generate_jig_at_y(p, y_local, return_full=True)
                self.last_warnings = []
                chord, spar_pct, washout, blend, local_xb_pct, x_dia = self.get_local_params(y_local)
                title = f"{item['label']} - Chord: {chord:.1f}mm, Washout: {washout:.2f}°" + (" [FAST PREVIEW]" if fast_mode else "")
                
                # Mock dummy parameters for draw_plot
                import numpy as np
                dummy_pts = np.array([])
                c_m = np.array(res_jig['c_m']) if 'c_m' in res_jig else dummy_pts
                c_f = np.array(res_jig['c_f']) if 'c_f' in res_jig else dummy_pts
                c_r = np.array(res_jig['c_r']) if 'c_r' in res_jig else dummy_pts
                
                # Create circle logic just to show the spar position
                def make_circle(c, d):
                    if d <= 0 or len(c) < 2: return dummy_pts
                    ang = np.linspace(0, 2*np.pi, 30)
                    return np.column_stack((c[0] + d/2*np.cos(ang), c[1] + d/2*np.sin(ang)))
                
                h_m = make_circle(c_m, res_jig.get('d_m', 0))
                h_f = make_circle(c_f, res_jig.get('d_f', 0))
                h_r = make_circle(c_r, res_jig.get('d_r', 0))
                
                jig_pts = np.array(res_jig.get('jig_pts', []))
                wing_pts = np.array(res_jig.get('wing_pts', []))
                
                self.draw_plot(wing_pts, c_m, h_m, c_r, h_r, c_f, h_f, [], [], [], [], [], [], dummy_pts, dummy_pts, dummy_pts, dummy_pts, dummy_pts, dummy_pts, [], None, title, jig_pts=jig_pts)
            else:
                res = self.engine.generate_rib_at_y(p, y_local, idx, t_rib, is_carbon=is_carbon, te_cut_override=te_cut_val)
                self.last_warnings = res.warnings_list
                chord, spar_pct, washout, blend, local_xb_pct, x_dia = self.get_local_params(y_local)
                angle = p['truss_angles_dict'].get(idx, p['base_truss_angle'])
                title = f"{item['label']} - Chord: {chord:.1f}mm, Washout: {washout:.2f}°, Truss: {angle:.1f}°" + (" [FAST PREVIEW]" if fast_mode else "")
                self.draw_plot(*res[:12], self.last_warnings, res.plank_poly_rot, res.te_part_coords, res.c_b1, res.hole_b1, res.c_b2, res.hole_b2, res.diag_poly_pts_list, res.final_rib_orig, title, res.te_cap_pts_list, res.rc_cap_pts_list)
        except Exception as e: print("Preview Error:", e)"""

content = content.replace(update_code_find, update_code_replace)

draw_plot_find = """    def draw_plot(self, rib_pts, c_m, h_m, c_r, h_r, c_f, h_f, t_holes, xb_act, xb_c_act, xb_skip, xb_c_skip, warnings_list, plank_poly, te_part, c_b1, hole_b1, c_b2, hole_b2, diag_poly_pts_list, final_rib_orig, title, te_cap_pts_list=None, rc_cap_pts_list=None):"""

draw_plot_replace = """    def draw_plot(self, rib_pts, c_m, h_m, c_r, h_r, c_f, h_f, t_holes, xb_act, xb_c_act, xb_skip, xb_c_skip, warnings_list, plank_poly, te_part, c_b1, hole_b1, c_b2, hole_b2, diag_poly_pts_list, final_rib_orig, title, te_cap_pts_list=None, rc_cap_pts_list=None, jig_pts=None):"""

content = content.replace(draw_plot_find, draw_plot_replace)

jig_draw_code = """        if rc_cap_pts_list is not None:
            drawn_rc_cap = False
            for cap_pts in rc_cap_pts_list[0] + rc_cap_pts_list[1]:
                if len(cap_pts) > 0:
                    self.ax.plot(cap_pts[:, 0], cap_pts[:, 1], color='black', linestyle='-', linewidth=2, label="Rib Cap" if not drawn_rc_cap else "")
                    drawn_rc_cap = True"""

jig_draw_code_replace = jig_draw_code + """
        if jig_pts is not None and len(jig_pts) > 0:
            self.ax.plot(jig_pts[:, 0], jig_pts[:, 1], color='red', linestyle='-', linewidth=2, label="Jig Outline")"""

content = content.replace(jig_draw_code, jig_draw_code_replace)

with open('ui/batch_mode.py', 'w') as f:
    f.write(content)


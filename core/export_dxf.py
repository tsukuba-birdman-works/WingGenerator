import os

class WingDXFExporter:
    """
    UIから受け取ったパラメータを元に、翼全体のDXFファイルを一括で生成・保存するクラス。
    """
    def __init__(self, engine, params):
        self.engine = engine
        self.p = params

    def export_all_ribs(self, dir_path):
        """すべての通常リブとカーボンリブのDXFファイルを指定されたディレクトリに保存する。"""
        import ezdxf
        exported_count = 0
        wing_name = self.p.get('wing_name', '').strip().replace('/', '_').replace('\\', '_')
        prefix = f"{wing_name}_" if wing_name else ""
        
        all_in_one = self.p.get('dxf_all_in_one', False)
        layer_flags = {
            'dxf_layer_rib_outline': self.p.get('dxf_layer_rib_outline', True),
            'dxf_layer_holes': self.p.get('dxf_layer_holes', True),
            'dxf_layer_truss': self.p.get('dxf_layer_truss', True),
            'dxf_layer_plank': self.p.get('dxf_layer_plank', True),
            'dxf_layer_te_part': self.p.get('dxf_layer_te_part', True),
            'dxf_layer_te_balsa': self.p.get('dxf_layer_te_balsa', True),
            'dxf_layer_jig_outline': self.p.get('dxf_layer_jig_outline', True)
        }
        selections = self.p.get('dxf_selections', {})
        
        doc = None
        msp = None
        current_y = 0.0
        gap_y = 20.0
        is_first = True
        
        if all_in_one:
            try:
                doc = ezdxf.new('R2010')
                msp = doc.modelspace()
            except Exception as e:
                print(f"ezdxf is required: {e}")
                return 0

        # 1. 通常リブのエクスポート
        for i, y_local in enumerate(self.p['y_positions']):
            key = f"rib___{i}"
            if selections and not selections.get(key, True):
                continue
                
            res = self._generate_rib_at_y(y_local, i, self.p['rib_thick'])
            y_global = y_local + self.p['joint_length']
            filename = f"{prefix}No.{i}_Y{y_global:.1f}mm.dxf"
            filepath = os.path.join(dir_path, filename)
            
            if all_in_one:
                pts = res[0] # rib_pts
                origin_pt = res[1]
                if len(pts) > 0:
                    local_min_y = min(p[1] for p in pts)
                    local_max_y = max(p[1] for p in pts)
                    if is_first:
                        offset_y = 0.0
                        is_first = False
                    else:
                        offset_y = current_y - gap_y - local_max_y + origin_pt[1]
                    offset = (0, offset_y)
                    current_y = local_min_y - origin_pt[1] + offset_y
                else:
                    offset = (0, 0)
            else:
                offset = (0, 0)

            self._export_single_dxf(filepath, res, jig_pts=None, doc=doc, msp=msp, offset=offset, layer_flags=layer_flags)
            exported_count += 1

        # 2. カーボンリブのエクスポート
        for cconf in self.p['carbon_rib_configs']:
            if not cconf['act']: continue
            idx, y_local = cconf['idx'], self.p['y_positions'][cconf['idx']]
            key = f"carbon_{cconf['loc']}_{cconf['pos']}_{idx}"
            if selections and not selections.get(key, True):
                continue
                
            te_cut_override = self.p['te_cut'] if cconf['te'] else 0.0
            res = self._generate_rib_at_y(y_local, idx, self.p['cr_thick'], is_carbon=True, te_cut_override=te_cut_override)
            
            y_global = y_local + self.p['joint_length']
            filename = f"{prefix}CarbonRib_{cconf['loc'].capitalize()}_{cconf['pos'].capitalize()}_Y{y_global:.1f}mm.dxf"
            filepath = os.path.join(dir_path, filename)
            
            if all_in_one:
                pts = res[0]
                origin_pt = res[1]
                if len(pts) > 0:
                    local_min_y = min(p[1] for p in pts)
                    local_max_y = max(p[1] for p in pts)
                    if is_first:
                        offset_y = 0.0
                        is_first = False
                    else:
                        offset_y = current_y - gap_y - local_max_y + origin_pt[1]
                    offset = (0, offset_y)
                    current_y = local_min_y - origin_pt[1] + offset_y
                else:
                    offset = (0, 0)
            else:
                offset = (0, 0)

            self._export_single_dxf(filepath, res, jig_pts=None, doc=doc, msp=msp, offset=offset, layer_flags=layer_flags)
            exported_count += 1

        # 3. ジグのエクスポート
        jig_str = self.p.get('jig_y_positions', '')
        if jig_str:
            try:
                joint = float(self.p.get('joint_length', 0.0))
                jigs = [float(v.strip()) for v in jig_str.split(',') if v.strip()]
                for j_idx, jy in enumerate(jigs):
                    key = f"jig_{j_idx}"
                    if selections and not selections.get(key, True):
                        continue
                        
                    jig_pts = self.engine.generate_jig_at_y(self.p, jy - joint)
                    if jig_pts:
                        filename = f"{prefix}Jig_No.{j_idx}_Y{jy:.1f}mm.dxf"
                        filepath = os.path.join(dir_path, filename)
                        
                        if all_in_one:
                            if jig_pts and len(jig_pts) > 0:
                                local_min_y = min(p[1] for p in jig_pts)
                                local_max_y = max(p[1] for p in jig_pts)
                                origin_y = 0.0
                                if is_first:
                                    offset_y = 0.0
                                    is_first = False
                                else:
                                    offset_y = current_y - gap_y - local_max_y + origin_y
                                offset = (0, offset_y)
                                current_y = local_min_y - origin_y + offset_y
                            else:
                                offset = (0, 0)
                        else:
                            offset = (0, 0)

                        self.engine.export_single_poly_dxf(filepath, jig_pts, (0, 0), doc=doc, msp=msp, offset=offset)
                        exported_count += 1
            except Exception as e:
                print(f"Error exporting jigs: {e}")

        if all_in_one and exported_count > 0:
            all_filepath = os.path.join(dir_path, f"{prefix}All_in_One.dxf")
            doc.saveas(all_filepath)
            
        return exported_count

    def _generate_rib_at_y(self, y_local, rib_index, thickness, is_carbon=False, te_cut_override=None):
        p_copy = self.p.copy()
        p_copy['tabs_active'] = False
        return self.engine.generate_rib_at_y(p_copy, y_local, rib_index, thickness, is_carbon, te_cut_override)

    def _export_single_dxf(self, filepath, res, jig_pts=None, doc=None, msp=None, offset=(0,0), layer_flags=None):
        te_balsa_pts = getattr(res, 'te_balsa_pts', None)
        te_balsa_holes = getattr(res, 'te_balsa_holes', None)
        self.engine.export_dxf(filepath, res[1], res[0], res[1], self.p['spar_hole_dia'], 
                               res[5], self.p['front_spar_dia'], res[3], self.p['rear_spar_dia'], 
                               res[7], res[9], self.p['xbrace_dia'], res[13], res[14], 
                               res[15], self.p['root_bolt1'][2], res[16], 
                               res[17], self.p['root_bolt2'][2], res[18], res[19], res[22], res[23], 
                               jig_pts=jig_pts, doc=doc, msp=msp, offset=offset, layer_flags=layer_flags,
                               te_balsa_pts=te_balsa_pts, te_balsa_holes=te_balsa_holes)
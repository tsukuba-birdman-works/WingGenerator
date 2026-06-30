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
        exported_count = 0

        # 1. 通常リブのエクスポート
        for i, y_local in enumerate(self.p['y_positions']):
            res = self._generate_rib_at_y(y_local, i, self.p['rib_thick'])
            y_global = y_local + self.p['joint_length']
            filename = f"Rib_{i:02d}_Y{y_global:.1f}.dxf"
            filepath = os.path.join(dir_path, filename)
            self._export_single_dxf(filepath, res)
            exported_count += 1

        # 2. カーボンリブのエクスポート
        for cconf in self.p['carbon_rib_configs']:
            if not cconf['act']: continue
            idx, y_local = cconf['idx'], self.p['y_positions'][cconf['idx']]
            
            te_cut_override = self.p['te_cut'] if cconf['te'] else 0.0
            res = self._generate_rib_at_y(y_local, idx, self.p['cr_thick'], is_carbon=True, te_cut_override=te_cut_override)
            
            y_global = y_local + self.p['joint_length']
            filename = f"CarbonRib_{cconf['loc'].capitalize()}_{cconf['pos'].capitalize()}_Y{y_global:.1f}.dxf"
            filepath = os.path.join(dir_path, filename)
            self._export_single_dxf(filepath, res)
            exported_count += 1
            
        return exported_count

    def _generate_rib_at_y(self, y_local, rib_index, thickness, is_carbon=False, te_cut_override=None):
        p_copy = self.p.copy()
        p_copy['tabs_active'] = False
        return self.engine.generate_rib_at_y(p_copy, y_local, rib_index, thickness, is_carbon, te_cut_override)

    def _export_single_dxf(self, filepath, res):
        self.engine.export_dxf(filepath, res[1], res[0], res[1], self.p['spar_hole_dia'], 
                               res[5], self.p['front_spar_dia'], res[3], self.p['rear_spar_dia'], 
                               res[7], res[9], self.p['xbrace_dia'], res[13], res[14], 
                               res[15], self.p['root_bolt1'][2], res[16], 
                               res[17], self.p['root_bolt2'][2], res[18], res[19], res[22], res[23])
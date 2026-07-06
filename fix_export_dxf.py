with open("core/export_dxf.py", "r") as f:
    content = f.read()

new_export_all_ribs = """
    def export_all_ribs(self, dir_path):
        exported_count = 0
        wing_name = self.p.get('wing_name', '').strip()
        prefix = f"{wing_name}_" if wing_name else ""

        target_ribs = self.p.get('dxf_target_ribs', True)
        target_carbon = self.p.get('dxf_target_carbon', True)
        target_jigs = self.p.get('dxf_target_jigs', True)
        all_in_one = self.p.get('dxf_all_in_one', False)
        merge_margin = float(self.p.get('dxf_merge_margin', 50.0))

        export_flags = {
            'dxf_part_outline': self.p.get('dxf_part_outline', True),
            'dxf_part_holes': self.p.get('dxf_part_holes', True),
            'dxf_part_truss': self.p.get('dxf_part_truss', True),
            'dxf_part_plank': self.p.get('dxf_part_plank', True),
            'dxf_part_te': self.p.get('dxf_part_te', True),
            'dxf_part_caps': self.p.get('dxf_part_caps', True),
        }

        doc = None
        msp = None
        current_y_offset = 0.0

        if all_in_one:
            try:
                import ezdxf
                doc = ezdxf.new('R2010')
                msp = doc.modelspace()
            except ImportError:
                print("ezdxf is not installed.")
                return 0

        def get_max_y(pts):
            if len(pts) == 0: return 0.0
            return max([p[1] for p in pts])
        
        def get_min_y(pts):
            if len(pts) == 0: return 0.0
            return min([p[1] for p in pts])

        dxf_start_idx = self.p.get('dxf_start_idx', 0)
        dxf_end_idx = self.p.get('dxf_end_idx', len(self.p['y_positions']) - 1)
        joint = float(self.p.get('joint_length', 0.0))
        
        jig_str = self.p.get('jig_y_positions', '')
        jigs = [float(v.strip()) for v in jig_str.split(',') if v.strip()] if jig_str else []

        carbon_configs = self.p.get('carbon_rib_configs', [])

        for i, y_local in enumerate(self.p['y_positions']):
            if i < dxf_start_idx or i > dxf_end_idx: continue
            y_global = y_local + joint
            
            max_y_group = -9999
            min_y_group = 9999
            any_exported = False

            # 1. Rib
            if target_ribs:
                res = self._generate_rib_at_y(y_local, i, self.p['rib_thick'])
                origin_offset = (res[1][0], res[1][1] - current_y_offset) if all_in_one else res[1]
                if not all_in_one:
                    filename = f"{prefix}No.{i}_Y{y_global:.1f}mm.dxf"
                    filepath = os.path.join(dir_path, filename)
                    self._export_single_dxf(filepath, res, origin=origin_offset, export_flags=export_flags)
                else:
                    self._export_single_dxf("", res, origin=origin_offset, doc=doc, msp=msp, export_flags=export_flags)
                    max_y_group = max(max_y_group, get_max_y(res[0]) - res[1][1] + current_y_offset if len(res[0])>0 else -9999)
                    min_y_group = min(min_y_group, get_min_y(res[0]) - res[1][1] + current_y_offset if len(res[0])>0 else 9999)
                    any_exported = True
                exported_count += 1

            # 2. Carbon
            if target_carbon:
                for cconf in carbon_configs:
                    if cconf['act'] and cconf['idx'] == i:
                        te_cut_override = self.p['te_cut'] if cconf['te'] else 0.0
                        res = self._generate_rib_at_y(y_local, i, self.p['cr_thick'], is_carbon=True, te_cut_override=te_cut_override)
                        origin_offset = (res[1][0], res[1][1] - current_y_offset) if all_in_one else res[1]
                        if not all_in_one:
                            filename = f"{prefix}CarbonRib_{cconf['loc'].capitalize()}_{cconf['pos'].capitalize()}_Y{y_global:.1f}mm.dxf"
                            filepath = os.path.join(dir_path, filename)
                            self._export_single_dxf(filepath, res, origin=origin_offset, export_flags=export_flags)
                        else:
                            self._export_single_dxf("", res, origin=origin_offset, doc=doc, msp=msp, export_flags=export_flags)
                            max_y_group = max(max_y_group, get_max_y(res[0]) - res[1][1] + current_y_offset if len(res[0])>0 else -9999)
                            min_y_group = min(min_y_group, get_min_y(res[0]) - res[1][1] + current_y_offset if len(res[0])>0 else 9999)
                            any_exported = True
                        exported_count += 1

            # 3. Jig
            if target_jigs:
                if any(abs(jy - (y_local)) < 1.0 for jy in jigs):
                    j_idx = next(idx for idx, jy in enumerate(jigs) if abs(jy - (y_local)) < 1.0)
                    jig_data = self.engine.generate_jig_at_y(self.p, y_local, return_full=True)
                    if jig_data and 'jig_pts' in jig_data and len(jig_data['jig_pts']) > 0:
                        jig_pts = jig_data['jig_pts']
                        c_m = jig_data['c_m']
                        origin_offset = (c_m[0], c_m[1] - current_y_offset) if all_in_one else c_m
                        if not all_in_one:
                            filename = f"{prefix}Jig_No.{j_idx}_Y{y_global:.1f}mm.dxf"
                            filepath = os.path.join(dir_path, filename)
                            self.engine.export_single_poly_dxf(filepath, jig_pts, origin_offset)
                        else:
                            self.engine.export_single_poly_dxf("", jig_pts, origin_offset, doc=doc, msp=msp)
                            max_y_group = max(max_y_group, get_max_y(jig_pts) - c_m[1] + current_y_offset)
                            min_y_group = min(min_y_group, get_min_y(jig_pts) - c_m[1] + current_y_offset)
                            any_exported = True
                        exported_count += 1

            if all_in_one and any_exported:
                current_y_offset -= (max_y_group - min_y_group) + merge_margin

        if all_in_one and exported_count > 0:
            filename = f"{prefix}All_In_One.dxf"
            filepath = os.path.join(dir_path, filename)
            doc.saveas(filepath)

        return exported_count
"""

# Extract the part to replace
import re
new_code = re.sub(r'    def export_all_ribs\(self, dir_path\):.*?(?=    def _generate_rib_at_y)', new_export_all_ribs + '\n', content, flags=re.DOTALL)

with open("core/export_dxf.py", "w") as f:
    f.write(new_code)

print("export_dxf.py patched successfully")

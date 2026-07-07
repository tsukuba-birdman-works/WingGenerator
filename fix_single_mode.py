import sys

with open('ui/single_mode.py', 'r') as f:
    content = f.read()

# Replace get_rib_parameters
new_get_rib = """    def get_rib_parameters(self, fast_mode=False) -> RibParameters:
        t_rib = 3.0 # Hardcoded as requested to delete from UI
        
        return RibParameters(
            file1=self.file1_path.get(),
            file2=self.file1_path.get(), # Single mode uses same file? Wait, single mode file2_path was removed? No, I only kept file1_path.
            blend_ratio=self.safe_float(self.blend_ratio_pct)/100.0,
            chord=self.safe_float(self.chord_length),
            spar_pct=self.safe_float(self.spar_pos_pct),
            washout_deg=self.safe_float(self.washout_deg),
            spar_hole_dia=self.safe_float(self.spar_hole_dia),
            rear_dx=0.0,
            rear_dy=0.0,
            rear_dia=0.0,
            front_dx=0.0,
            front_dy=0.0,
            front_dia=0.0,
            truss_angle=self.safe_float(self.base_truss_angle),
            truss_front_n=self.safe_int(self.truss_front_n),
            truss_rear_n=self.safe_int(self.truss_rear_n),
            beam_width=self.safe_float(self.beam_width),
            margin_spar=self.safe_float(self.margin_spar),
            margin_bolt=self.safe_float(self.margin_bolt),
            margin_outer=self.safe_float(self.margin_outer),
            truss_fillet=self.safe_float(self.truss_fillet),
            min_hole_dia=self.safe_float(self.min_hole_dia),
            xb_t_list=[],
            x_dia=0.0,
            plank_start=self.safe_float(self.plank_start),
            plank_end=self.safe_float(self.plank_end),
            plank_part_start=self.safe_float(self.plank_start),
            plank_part_end=self.safe_float(self.plank_end),
            plank_thick=self.safe_float(self.plank_thick),
            stringers_data=self.get_stringers_data(),
            te_cut=self.safe_float(self.te_cut),
            apply_safe_margin=self.safe_margin_var.get(),
            te_cap_uf_act=False,
            te_cap_uf_w=0.0,
            te_cap_ur_act=False,
            te_cap_ur_w=0.0,
            te_cap_lf_act=False,
            te_cap_lf_w=0.0,
            te_cap_lr_act=False,
            te_cap_lr_w=0.0,
            te_cap_thick=0.0,
            rc1_act=False,
            rc1_start=0.0,
            rc1_end=0.0,
            rc1_thick=0.0,
            rc2_act=False,
            rc2_start=0.0,
            rc2_end=0.0,
            rc2_thick=0.0,
            bolt1_dx=self.safe_float(self.bolt1_dx),
            bolt1_dy=self.safe_float(self.bolt1_dy),
            bolt1_dia=self.safe_float(self.bolt1_dia),
            bolt2_dx=self.safe_float(self.bolt2_dx),
            bolt2_dy=self.safe_float(self.bolt2_dy),
            bolt2_dia=self.safe_float(self.bolt2_dia),
            diag_params_list=[],
            fast_mode=fast_mode,
            tabs_active=self.tabs_active.get() if hasattr(self, 'tabs_active') else True,
            truss_tab_width=4.0,
            le_interp_active=self.le_interp_active.get(),
            le_interp_range=self.safe_float(self.le_interp_range, 10.0),
            le_interp_divisions=self.safe_int(self.le_interp_divisions, 50)
        )"""

# I will replace the function in content
import re
content = re.sub(r'    def get_rib_parameters.*?        \)', new_get_rib, content, flags=re.DOTALL)

with open('ui/single_mode.py', 'w') as f:
    f.write(content)

# UI Restoration Plan

## 1. Fix 3D Export Variables
Initialize `self.export_... = tk.BooleanVar(value=True)` for all 3D export parts so they are properly saved and function.

## 2. Restore Tab 1 (Wing)
Add:
- `rib_interval`
- `cr_root_in_act`, `cr_thick` etc. for Carbon Ribs

## 3. Restore Tab 2 (Spar)
Add:
- `root_bolt1_dia`, `root_bolt1_dx`, `root_bolt1_dy`
- `root_bolt2_dia`, `root_bolt2_dx`, `root_bolt2_dy`
- `tip_bolt1_dia`, `tip_bolt1_dx`, `tip_bolt1_dy`
- `tip_bolt2_dia`, `tip_bolt2_dx`, `tip_bolt2_dy`
- `spar_pos_tip`

## 4. Restore Tab 3 (Rib / Truss)
Add:
- `margin_outer_edge`
- `local_truss_angle`

## 5. Restore Tab 4 (Plank / TE)
Add:
- `plank_part_start`, `plank_part_end`
- `te_cap_ur_act`, `te_cap_lr_act`, `te_cap_thick`, `te_cap_ur_w`, `te_cap_lr_w`
- `rc1_...` and `rc2_...`

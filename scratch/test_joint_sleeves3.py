import trimesh
import numpy as np

joint_sleeves = [{'start': 5.0, 'end': 55.0, 'out_dia': 30.0, 't1': 2.0, 't2': 0.5}]
R_in = 10.0 # 20.0 / 2.0
meshes = {}

for i, js in enumerate(joint_sleeves):
    y_start = js['start']
    y_end = js['end']
    if y_start >= y_end:
        y_start, y_end = y_end, y_start
    
    L = y_end - y_start
    if L <= 0: continue

    R_out = js['out_dia'] / 2.0
    t1 = js['t1']
    t2 = js['t2']

    if R_out <= R_in: continue

    def place_annulus(r_min, r_max, height, z_center):
        if r_max <= r_min or height <= 0: return None
        try:
            mesh = trimesh.creation.annulus(r_min=r_min, r_max=r_max, height=height)
            rot = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
            mesh.apply_transform(rot)
            trans = trimesh.transformations.translation_matrix([0, z_center, 0])
            mesh.apply_transform(trans)
            return mesh
        except Exception as e:
            print("Error creating joint sleeve part:", e)
            return None

    skin_mesh = place_annulus(R_out - t2, R_out, L, (y_start + y_end) / 2.0)
    if skin_mesh: meshes[f"JointSleeve_Skin_{i}"] = skin_mesh

    if t1 > 0:
        cap_s = place_annulus(R_in, R_out, t1, y_start + t1 / 2.0)
        if cap_s: meshes[f"JointSleeve_CapS_{i}"] = cap_s
        
        cap_e = place_annulus(R_in, R_out, t1, y_end - t1 / 2.0)
        if cap_e: meshes[f"JointSleeve_CapE_{i}"] = cap_e

    foam_L = L - 2 * t1
    if foam_L > 0 and R_out - t2 > R_in:
        foam_mesh = place_annulus(R_in, R_out - t2, foam_L, (y_start + y_end) / 2.0)
        if foam_mesh: meshes[f"JointSleeve_Foam_{i}"] = foam_mesh

scene = trimesh.Scene()
for name, m in meshes.items():
    if "Skin" in name:
        m.visual.face_colors = [20, 20, 20, 255]
    elif "Cap" in name:
        m.visual.face_colors = [30, 30, 30, 255]
    elif "Foam" in name:
        m.visual.face_colors = [100, 100, 255, 255]
    scene.add_geometry(m)

scene.export("scratch/test_joint_sleeves3.glb")
print("Exported scratch/test_joint_sleeves3.glb with keys:", list(meshes.keys()))

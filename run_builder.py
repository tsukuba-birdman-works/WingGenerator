import sys
import json
from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DExporter

if __name__ == '__main__':
    with open('Ribgenerator.json', 'r') as f:
        j = json.load(f)
    params = {}
    for k, v in j.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, dict):
                    params.update(vv)
                else:
                    params[kk] = vv
        else:
            params[k] = v
            
    # Fix paths
    import glob
    dats = glob.glob('Airfoils/*.dat')
    if dats:
        params['file1_path'] = dats[0]
        params['file2_path'] = dats[0]
        
    engine = RibGeneratorEngine()
    te_curves = []
    for i, y_local in enumerate(params.get('y_positions', [])):
        res = engine.generate_rib_at_y(params, y_local, i, params.get('rib_thick', 2.0), False, None)
        c_m = np.array([res.spar_x, res.spar_y])
        if len(res[14]) > 0:
            c = res[14] - c_m
            c_3d = np.insert(c, 1, y_local, axis=1)
            te_curves.append(c_3d)

    mesh = Wing3DExporter.generate_lofted_surface(te_curves, topo_type='TE_Skin')
    if mesh:
        mesh.export('test_te_mesh.glb')
        print(f"Mesh exported, vertices: {len(mesh.vertices)}")

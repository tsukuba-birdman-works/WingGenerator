from core.engine import RibGeneratorEngine
from core.export_3d import Wing3DExporter
import xml.etree.ElementTree as ET

def convert_xml_to_json(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    p = {}
    for elem in root:
        try:
            val = float(elem.text)
            if val.is_integer(): val = int(val)
        except:
            val = elem.text
        p[elem.tag] = val

    p['y_positions'] = [0, 100, 200]
    p['chord_lengths'] = [200, 200, 200]
    p['washouts'] = [0, 0, 0]
    p['dihedrals'] = [0, 0, 0]
    p['connectors'] = []
    p['carbon_rib_configs'] = []
    p['jig_hole_diameter'] = 5.0
    p['te_cut'] = 20.0
    
    p['spar_x'] = 50.0
    p['spar_y'] = 5.0
    p['spar_dia'] = 8.0
    p['spar_hole_dia'] = 8.0
    p['joint_length'] = 0.0
    p['rib_thick'] = 2.0
    p['cr_thick'] = 1.0
    p['cr_act'] = False

    return p

p = convert_xml_to_json('settings.xml')
exporter = Wing3DExporter(p)
scene_geoms = exporter.build_geometry()[0]
print("Geoms:", scene_geoms.keys())
exporter.export_glb("scratch/test_bool_out.glb")
print("Exported GLB")

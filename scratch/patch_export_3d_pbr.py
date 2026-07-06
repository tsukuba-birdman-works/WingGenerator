import re

with open('core/export_3d.py', 'r') as f:
    content = f.read()

# Replace the materials import
import_find = "from .materials import AVAILABLE_MATERIALS"
import_replace = "from .materials import AVAILABLE_MATERIALS, MATERIAL_PBR_PROPERTIES"
content = content.replace(import_find, import_replace)

# Modify _collect_geometry_data part_colors
# Instead of `AVAILABLE_MATERIALS.get(self.p['mat_ribs'], [200, 200, 200, 255])`
# We want a helper function or dictionary comprehension that gets the color and PBR properties
color_map_code = """        def get_mat_props(mat_key, default_rgba=[200, 200, 200, 255]):
            mat_name = self.p.get(mat_key, '')
            rgba = AVAILABLE_MATERIALS.get(mat_name, default_rgba)
            pbr = MATERIAL_PBR_PROPERTIES.get(mat_name, (0.1, 0.5)) # default metallic, roughness
            return (rgba, pbr[0], pbr[1])

        part_colors = {
            'Ribs': get_mat_props('mat_ribs'),
            'Main_Spar': get_mat_props('mat_main_spar', [30,30,30,255]),
            'Front_Spar': get_mat_props('mat_front_spar', [30,30,30,255]),
            'Rear_Spar': get_mat_props('mat_rear_spar', [30,30,30,255]),
            'Plank_Skin': get_mat_props('mat_plank'),
            'TE_Skin': get_mat_props('mat_te'),
            'Connector': get_mat_props('mat_connectors', [30,30,30,255]),
            'Stringer': get_mat_props('mat_stringers'),
            'XBraceWire': get_mat_props('mat_xbrace_wires'),
            'Diag_Spar': get_mat_props('mat_diag_spars', [30,30,30,255]),
            'CarbonRibs': get_mat_props('mat_carbon_ribs', [30,30,30,255]),
            'TE_Cap': get_mat_props('mat_te_caps', [30,30,30,255]),
            'Rib_Cap': get_mat_props('mat_rib_caps', [30,30,30,255]),
            'JointSleeve_Cap': get_mat_props('mat_js_cap', [30, 30, 30, 255]),
            'JointSleeve_Foam': get_mat_props('mat_js_foam', [100, 100, 255, 255]),
            'JointSleeve_Skin': get_mat_props('mat_js_skin', [30, 30, 30, 255]),
            'Film_Skin': get_mat_props('mat_film', [250, 250, 255, 80])
        }"""

# Using regex to replace the part_colors block
content = re.sub(r"part_colors = \{.*?\}", color_map_code, content, flags=re.DOTALL)

# Modify apply_color to unpack (rgba, metallic, roughness)
apply_color_find = """        def apply_color(mesh_obj, color_rgba):
            mesh_obj.visual.face_colors = color_rgba
            if PBRMaterial:
                a_mode = 'BLEND' if color_rgba[3] < 255 else 'OPAQUE'
                mesh_obj.visual.material = PBRMaterial(baseColorFactor=color_rgba, doubleSided=True, alphaMode=a_mode)"""

apply_color_replace = """        def apply_color(mesh_obj, color_props):
            if isinstance(color_props, tuple) and len(color_props) == 3:
                color_rgba, metallic, roughness = color_props
            else:
                color_rgba, metallic, roughness = color_props, 0.1, 0.5

            mesh_obj.visual.face_colors = color_rgba
            if PBRMaterial:
                a_mode = 'BLEND' if color_rgba[3] < 255 else 'OPAQUE'
                mesh_obj.visual.material = PBRMaterial(baseColorFactor=color_rgba, metallicFactor=metallic, roughnessFactor=roughness, doubleSided=True, alphaMode=a_mode)"""

content = content.replace(apply_color_find, apply_color_replace)

# Modify the default part_colors get calls in export_3d_scene to supply tuple defaults
content = re.sub(r"c = part_colors\.get\('Ribs',\s*\[200,\s*200,\s*200,\s*255\]\)", r"c = part_colors.get('Ribs', ([200, 200, 200, 255], 0.1, 0.5))", content)
content = re.sub(r"c = part_colors\.get\('CarbonRibs',\s*\[30,\s*30,\s*30,\s*255\]\)", r"c = part_colors.get('CarbonRibs', ([30, 30, 30, 255], 0.2, 0.1))", content)
content = re.sub(r"c = part_colors\.get\('Rib_Cap',\s*\[30,\s*30,\s*30,\s*255\]\)", r"c = part_colors.get('Rib_Cap', ([30, 30, 30, 255], 0.2, 0.1))", content)
content = re.sub(r"c = part_colors\.get\(name,\s*\[200,\s*200,\s*200,\s*255\]\)", r"c = part_colors.get(name, ([200, 200, 200, 255], 0.1, 0.5))", content)


with open('core/export_3d.py', 'w') as f:
    f.write(content)


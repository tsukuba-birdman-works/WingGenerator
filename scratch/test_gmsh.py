import gmsh
import numpy as np
from shapely.geometry import Polygon

# Define a Shapely polygon with a hole
outer = [(0, 0), (10, 0), (10, 5), (0, 5)]
hole = [(2, 1), (8, 1), (8, 4), (2, 4)]
poly = Polygon(outer, [hole])

def shapely_to_gmsh(polygon, mesh_size=0.5):
    gmsh.initialize()
    gmsh.model.add("rib_test")
    
    # We use the OpenCASCADE kernel for robust 2D operations
    
    def add_ring(ring, z=0):
        coords = list(ring.coords)
        if coords[0] == coords[-1]:
            coords = coords[:-1]
        
        pt_tags = []
        for x, y in coords:
            pt_tags.append(gmsh.model.occ.addPoint(x, y, z, mesh_size))
            
        line_tags = []
        for i in range(len(pt_tags)):
            p1 = pt_tags[i]
            p2 = pt_tags[(i+1)%len(pt_tags)]
            line_tags.append(gmsh.model.occ.addLine(p1, p2))
            
        curve_loop = gmsh.model.occ.addCurveLoop(line_tags)
        return curve_loop

    cl_outer = add_ring(polygon.exterior)
    cl_holes = [add_ring(interior) for interior in polygon.interiors]
    
    surface = gmsh.model.occ.addPlaneSurface([cl_outer] + cl_holes)
    
    gmsh.model.occ.synchronize()
    
    # Generate 2D mesh
    gmsh.model.mesh.generate(2)
    
    nodeTags, nodeCoords, _ = gmsh.model.mesh.getNodes()
    elementTypes, elementTags, nodeTagsPerElement = gmsh.model.mesh.getElements(dim=2)
    
    print(f"Generated {len(nodeTags)} nodes and {len(elementTags[0]) if elementTags else 0} elements.")
    
    # gmsh.write("test_mesh.msh")
    gmsh.finalize()

try:
    shapely_to_gmsh(poly)
except Exception as e:
    print(f"Error: {e}")

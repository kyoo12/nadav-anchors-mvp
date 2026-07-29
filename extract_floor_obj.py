import rhino3dm

print("Loading 3DM file...")
model = rhino3dm.File3dm.Read("modelForNadav.3dm")

ff_idx = -1
for layer in model.Layers:
    if layer.Name == 'floting_floor':
        ff_idx = layer.Index
        break

if ff_idx == -1:
    print("Could not find floting_floor layer")
    exit()

print(f"Found floting_floor layer index: {ff_idx}")

obj_lines = []
vertex_offset = 1

for obj in model.Objects:
    if obj.Attributes.LayerIndex == ff_idx and obj.Geometry.ObjectType == rhino3dm.ObjectType.Mesh:
        mesh = obj.Geometry
        # Convert Rhino Z-up to Three.js Y-up
        for i in range(len(mesh.Vertices)):
            v = mesh.Vertices[i]
            # three_x = x/1000, three_y = z/1000, three_z = -y/1000
            obj_lines.append(f"v {v.X/1000.0} {v.Z/1000.0} {-v.Y/1000.0}")
            
        for i in range(len(mesh.Faces)):
            f = mesh.Faces[i]
            if f[2] == f[3]: # Triangle
                obj_lines.append(f"f {f[0]+vertex_offset} {f[1]+vertex_offset} {f[2]+vertex_offset}")
            else: # Quad
                obj_lines.append(f"f {f[0]+vertex_offset} {f[1]+vertex_offset} {f[2]+vertex_offset} {f[3]+vertex_offset}")
                
        vertex_offset += len(mesh.Vertices)

with open("web/public/floating_floor.obj", "w") as f:
    f.write("\n".join(obj_lines))
    
print(f"Exported {vertex_offset - 1} vertices to web/public/floating_floor.obj")

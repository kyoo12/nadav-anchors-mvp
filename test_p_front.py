import rhino3dm
import numpy as np
from scipy.spatial import cKDTree

model = rhino3dm.File3dm.Read("modelForNadav.3dm")
col_idx = -1
for layer in model.Layers:
    if layer.Name == "vertical colums":
        col_idx = layer.Index
        break

def extract_pts(mesh):
    return np.array([[v.X, v.Y] for v in mesh.Vertices])

# Get pillar P4 (for F4_40 left path)
p4_pts = None
for obj in model.Objects:
    if obj.Attributes.LayerIndex == col_idx and obj.Attributes.Name == "P4" and obj.Geometry.ObjectType == rhino3dm.ObjectType.Mesh:
        p4_pts = extract_pts(obj.Geometry)
        break

tree = cKDTree(p4_pts)

M_web = [-4.39, 105.23] # F4_40
M_rhino = [M_web[0] * 1000.0, -M_web[1] * 1000.0]

# P_front from M
_, idx = tree.query(M_rhino)
P_front = p4_pts[idx]
print(f"P_front (Rhino): {P_front[0]:.1f}, {P_front[1]:.1f}")
print(f"P_front (Web): {P_front[0]/1000.0:.2f}, {-P_front[1]/1000.0:.2f}")

# A4
A4_web = [-9.21, 104.23]
print(f"A4 (Web): {A4_web[0]:.2f}, {A4_web[1]:.2f}")

# Dot product check
MP = [P_front[0]/1000.0 - M_web[0], -P_front[1]/1000.0 - M_web[1]]
PA = [A4_web[0] - P_front[0]/1000.0, A4_web[1] - (-P_front[1]/1000.0)]
dot = MP[0]*PA[0] + MP[1]*PA[1]
print(f"Dot product (M -> P_front) . (P_front -> A4) = {dot:.2f}")
if dot > 0:
    print("A4 is PAST the front face and will be trimmed!")
else:
    print("A4 is in front of the front face and will be kept.")

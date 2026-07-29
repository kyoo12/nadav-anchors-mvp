import rhino3dm
from scipy.spatial import KDTree
import json

model = rhino3dm.File3dm.Read("modelForNadav.3dm")

col_idx = -1
for layer in model.Layers:
    if layer.Name == "vertical colums":
        col_idx = layer.Index
        break

pillars_data = []
for obj in model.Objects:
    if obj.Attributes.LayerIndex == col_idx and obj.Geometry.ObjectType == rhino3dm.ObjectType.Mesh:
        pts_2d = []
        for v in obj.Geometry.Vertices:
            pts_2d.append((v.X, v.Y))
        if pts_2d:
            pillars_data.append(KDTree(pts_2d))

with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["floor"] == 2 and 49 <= int(a["id"].split("_")[1]) <= 65:
        rhino_x = a["x"] * 1000.0
        rhino_y = -a["z"] * 1000.0
        
        min_d = float("inf")
        for tree in pillars_data:
            d, _ = tree.query([rhino_x, rhino_y])
            if d < min_d: min_d = d
            
        print(f"Anchor {a['id'].split('_')[1]}: dist={min_d:.1f} mm")

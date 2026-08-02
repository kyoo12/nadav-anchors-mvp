import json

with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)
    
for a in anchors:
    if a['id'] == 'F0_6':
        print("Final JSON data:")
        print(f"X: {a['x']}, Z: {a['z']}")
        
import rhino3dm
model = rhino3dm.File3dm.Read("modelForNadav.3dm")
layer_indices = {layer.Index for layer in model.Layers if layer.Name in ['Layer 01', 'Layer 02', 'vertical colums', 'GYPS 2', 'concret part']}

blocks = []
for obj in model.Objects:
    geom = obj.Geometry
    if obj.Attributes.LayerIndex in layer_indices and geom.ObjectType == rhino3dm.ObjectType.InstanceReference:
        idef = model.InstanceDefinitions.FindId(geom.ParentIdefId)
        if idef:
            blocks.append({
                'x': geom.Xform.M03, 'y': geom.Xform.M13, 'z': geom.Xform.M23,
                'name': idef.Name
            })

# Search for the block close to F0_6 coordinates
import math
for b in blocks:
    if abs((b['x']/1000.0) - a['x']) < 1.0 and abs((-b['y']/1000.0) - a['z']) < 1.0:
        print("Found matching raw block:")
        print(f"Name: {b['name']}, X: {b['x']}, Y: {b['y']}, Z: {b['z']}")
        
        # Now find its neighbors
        for n in blocks:
            if n != b:
                dist = math.hypot(n['x']-b['x'], n['y']-b['y'])
                if dist < 150:
                    print(f"Neighbor: {n['name']} at dist {dist:.1f}")


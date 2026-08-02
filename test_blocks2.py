import rhino3dm
import math
import numpy as np

model = rhino3dm.File3dm.Read("modelForNadav.3dm")
layer_indices = {layer.Index for layer in model.Layers if layer.Name in ['Layer 01', 'Layer 02', 'vertical colums', 'GYPS 2', 'concret part']}

raw_blocks = []
for obj in model.Objects:
    geom = obj.Geometry
    if obj.Attributes.LayerIndex in layer_indices and geom.ObjectType == rhino3dm.ObjectType.InstanceReference:
        idef = model.InstanceDefinitions.FindId(geom.ParentIdefId)
        name = idef.Name if idef else "Unknown"
        raw_blocks.append({
            'x': geom.Xform.M03, 'y': geom.Xform.M13, 'z': geom.Xform.M23,
            'name': name
        })

print("Found", len(raw_blocks), "blocks.")

# Let's find a cluster that has AN70 and PL70
for b in raw_blocks:
    if "AN70" in b['name'].upper():
        print(f"AN70 block found at {b['x']:.1f}, {b['y']:.1f}, {b['z']:.1f}")
        # Find PL blocks nearby
        for p in raw_blocks:
            if "PL70" in p['name'].upper():
                dist = math.hypot(p['x']-b['x'], p['y']-b['y'])
                if dist < 150:
                    print(f"  -> Matched PL70 at {p['x']:.1f}, {p['y']:.1f}, {p['z']:.1f}. Dist: {dist:.1f}")
                    break
        break

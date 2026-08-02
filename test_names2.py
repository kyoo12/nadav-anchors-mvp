import rhino3dm
model = rhino3dm.File3dm.Read("modelForNadav.3dm")
layer_indices = {layer.Index for layer in model.Layers if layer.Name in ['Layer 01', 'Layer 02', 'vertical colums', 'GYPS 2', 'concret part']}

names = set()
for obj in model.Objects:
    geom = obj.Geometry
    if obj.Attributes.LayerIndex in layer_indices and geom.ObjectType == rhino3dm.ObjectType.InstanceReference:
        idef = model.InstanceDefinitions.FindId(geom.ParentIdefId)
        if idef:
            names.add(idef.Name)

for n in names:
    print(n)

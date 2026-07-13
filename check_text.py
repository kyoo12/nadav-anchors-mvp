import rhino3dm

model = rhino3dm.File3dm.Read("modelForNadav.3dm")
mapping = {}
for idef in model.InstanceDefinitions:
    for obj in idef.GetObjects():
        if obj.Geometry.ObjectType == rhino3dm.ObjectType.Annotation:
            try:
                mapping[idef.Name] = obj.Geometry.PlainText
            except:
                pass
for k, v in mapping.items():
    print(k.encode('utf-8', 'replace').decode('utf-8'), '->', v)

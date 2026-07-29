with open("web/src/components/FloatingFloorMesh.tsx", "r", encoding="utf-8") as f:
    app = f.read()

# Make it clean
app = app.replace("color: '#00F0FF',", "color: '#94a3b8',")
app = app.replace("opacity: 0.15,", "opacity: 0.5,\n          depthWrite: false,")
app = app.replace("wireframe: true,", "wireframe: false,")

with open("web/src/components/FloatingFloorMesh.tsx", "w", encoding="utf-8") as f:
    f.write(app)

with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    app2 = f.read()

# Fix undefined TS errors
app2 = app2.replace("a.offsetX.toFixed(1)", "(a.offsetX || 0).toFixed(1)")
app2 = app2.replace("a.offsetY.toFixed(1)", "(a.offsetY || 0).toFixed(1)")
app2 = app2.replace("a.distanceToConcrete.toFixed(1)", "(a.distanceToConcrete || 0).toFixed(1)")
app2 = app2.replace("a.nearestGridX,", "a.nearestGridX || 'N/A',")
app2 = app2.replace("a.nearestGridY,", "a.nearestGridY || 'N/A',")

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(app2)

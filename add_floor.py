with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    app = f.read()

app = app.replace(
    "import BuildingMesh from './components/BuildingMesh'",
    "import BuildingMesh from './components/BuildingMesh'\nimport FloatingFloorMesh from './components/FloatingFloorMesh'"
)

app = app.replace(
    "<BuildingMesh />",
    "<BuildingMesh />\n          <FloatingFloorMesh />"
)

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(app)

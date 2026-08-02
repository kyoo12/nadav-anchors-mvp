with open("web/src/components/AnchorVisualizer.tsx", "r", encoding="utf-8") as f:
    av = f.read()

av = av.replace("placementError: boolean;", "placementError: boolean;\n  placementErrorAmount: number;")
with open("web/src/components/AnchorVisualizer.tsx", "w", encoding="utf-8") as f:
    f.write(av)


with open("web/src/components/RightSidebar.tsx", "r", encoding="utf-8") as f:
    rs = f.read()

rs = rs.replace("""            <div className="detail-item">
              <span className="detail-label">Distance to Concrete</span>
              <span className={`detail-value ${selectedAnchor.placementError ? 'pending' : ''}`}>
                {selectedAnchor.distanceToConcrete > 0 ? selectedAnchor.distanceToConcrete.toFixed(1) : 'N/A'} mm
              </span>
            </div>""",
"""            <div className="detail-item">
              <span className="detail-label">Actual Dist. to Concrete</span>
              <span className={`detail-value ${selectedAnchor.placementError ? 'pending' : ''}`}>
                {selectedAnchor.distanceToConcrete !== 0 ? selectedAnchor.distanceToConcrete.toFixed(1) : 'N/A'} mm
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Placement Error (CAD)</span>
              <span className={`detail-value ${selectedAnchor.placementErrorAmount !== 0 ? 'pending' : ''}`}>
                {selectedAnchor.placementErrorAmount > 0 ? '+' : ''}{selectedAnchor.placementErrorAmount.toFixed(1)} mm
              </span>
            </div>""")
with open("web/src/components/RightSidebar.tsx", "w", encoding="utf-8") as f:
    f.write(rs)


with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    app = f.read()

app = app.replace("const header = \"PointID,X,Y,Z,Floor,Type,NearestGridX,OffsetX,NearestGridY,OffsetY,WallGap\\n\";",
                  "const header = \"PointID,X,Y,Z,Floor,Type,NearestGridX,OffsetX,NearestGridY,OffsetY,TrueWallGap,CADError\\n\";")

app = app.replace("`${a.id},${a.x.toFixed(3)},${a.y.toFixed(3)},${a.z.toFixed(3)},${a.floor},${a.metadata},${a.nearestGridX},${(a.offsetX || 0).toFixed(1)},${a.nearestGridY},${(a.offsetY || 0).toFixed(1)},${(a.distanceToConcrete || 0).toFixed(1)}`",
                  "`${a.id},${a.x.toFixed(3)},${a.y.toFixed(3)},${a.z.toFixed(3)},${a.floor},${a.metadata},${a.nearestGridX},${(a.offsetX || 0).toFixed(1)},${a.nearestGridY},${(a.offsetY || 0).toFixed(1)},${(a.distanceToConcrete || 0).toFixed(1)},${(a.placementErrorAmount || 0).toFixed(1)}`")
with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(app)


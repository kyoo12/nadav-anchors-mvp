with open("extract_segmented.py", "r", encoding="utf-8") as f:
    script = f.read()

import re

# Update extraction logic
replacement = """            shim_thickness = 0.0
            if best_dist < 999999:
                # 1. Calculate True Required Shim Thickness (Ideal gap for PL block is 0.0)
                shim_thickness = best_dist
                dist_to_concrete = best_dist
                
                # 2. Sanity Audit
                # If it penetrates wall severely (< -20) or hovers impossibly far (> 300)
                if best_dist < -20.0 or best_dist > 300.0:
                    placement_error = True
                
                # NOTE: We have REMOVED the auto-snapping logic completely!
                # The anchors will export at their true CAD coordinates to preserve the perfectly straight facade alignment.
"""

script = re.sub(r"            placement_error_amount = 0\.0\n.*?pl_block\['y'\] \+= placement_error_amount \* vy_y", 
                replacement, 
                script, flags=re.DOTALL)

script = script.replace("placement_error_amount = 0.0", "shim_thickness = 0.0")
script = script.replace("'placementErrorAmount': placement_error_amount,", "'shimThickness': shim_thickness,")
script = script.replace("'placementErrorAmount': float(a.get('placementErrorAmount', 0.0)),", "'shimThickness': float(a.get('shimThickness', 0.0)),")

with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(script)


with open("web/src/components/AnchorVisualizer.tsx", "r", encoding="utf-8") as f:
    av = f.read()

av = av.replace("placementErrorAmount?: number;", "shimThickness?: number;")
with open("web/src/components/AnchorVisualizer.tsx", "w", encoding="utf-8") as f:
    f.write(av)


with open("web/src/components/RightSidebar.tsx", "r", encoding="utf-8") as f:
    rs = f.read()

rs = rs.replace("""            <div className="detail-item">
              <span className="detail-label">Placement Error (CAD)</span>
              <span className={`detail-value ${selectedAnchor.placementErrorAmount !== 0 ? 'pending' : ''}`}>
                {selectedAnchor.placementErrorAmount > 0 ? '+' : ''}{selectedAnchor.placementErrorAmount.toFixed(1)} mm
              </span>
            </div>""",
"""            <div className="detail-item">
              <span className="detail-label">Required Shim Thickness</span>
              <span className={`detail-value ${selectedAnchor.shimThickness !== 0 ? 'pending' : ''}`}>
                {selectedAnchor.shimThickness > 0 ? '+' : ''}{selectedAnchor.shimThickness.toFixed(1)} mm
              </span>
            </div>""")

with open("web/src/components/RightSidebar.tsx", "w", encoding="utf-8") as f:
    f.write(rs)


with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    app = f.read()

app = app.replace("const header = \"PointID,X,Y,Z,Floor,Type,NearestGridX,OffsetX,NearestGridY,OffsetY,TrueWallGap,CADError\\n\";",
                  "const header = \"PointID,X,Y,Z,Floor,Type,NearestGridX,OffsetX,NearestGridY,OffsetY,TrueWallGap,ShimThickness\\n\";")

app = app.replace("`${a.id},${a.x.toFixed(3)},${a.y.toFixed(3)},${a.z.toFixed(3)},${a.floor},${a.metadata},${a.nearestGridX},${(a.offsetX || 0).toFixed(1)},${a.nearestGridY},${(a.offsetY || 0).toFixed(1)},${(a.distanceToConcrete || 0).toFixed(1)},${(a.placementErrorAmount || 0).toFixed(1)}`",
                  "`${a.id},${a.x.toFixed(3)},${a.y.toFixed(3)},${a.z.toFixed(3)},${a.floor},${a.metadata},${a.nearestGridX},${(a.offsetX || 0).toFixed(1)},${a.nearestGridY},${(a.offsetY || 0).toFixed(1)},${(a.distanceToConcrete || 0).toFixed(1)},${(a.shimThickness || 0).toFixed(1)}`")

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(app)


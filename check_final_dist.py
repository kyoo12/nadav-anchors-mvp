import json
with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["isMiddleAnchor"] and a["floor"] == 2:
        print(f"Anchor {a['id']}: Pillar A ({a.get('pillarALabel')}): {a['pillarADistance']:.1f} mm, Pillar B ({a.get('pillarBLabel')}): {a['pillarBDistance']:.1f} mm")

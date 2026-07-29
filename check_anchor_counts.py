import json
with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["isMiddleAnchor"] and a["floor"] == 2:
        left_path = len(a["pillarAPath"]) - 1
        right_path = len(a["pillarBPath"]) - 1
        print(f"Anchor {a['id']}: {left_path} hops to {a.get('pillarALabel')}, {right_path} hops to {a.get('pillarBLabel')}")

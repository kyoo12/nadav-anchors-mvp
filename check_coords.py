import json
with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["floor"] == 2 and 49 <= int(a["id"].split("_")[1]) <= 55:
        print(f"Anchor {a['id'].split('_')[1]}: x={a['x']:.2f}, y={a['y']:.2f}, z={a['z']:.2f}")

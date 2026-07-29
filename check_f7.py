import json
with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["isMiddleAnchor"] and a["floor"] == 7:
        d_left = a['pillarADistance']
        d_right = a['pillarBDistance']
        total = d_left + d_right
        print(f"Anchor F7_{a['id'].split('_')[1]}: {a.get('pillarALabel')} to {a.get('pillarBLabel')}, Left={d_left:.1f}, Right={d_right:.1f}, Total={total:.1f}")

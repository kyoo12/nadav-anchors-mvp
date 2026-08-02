import json
with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a['id'] == 'F0_6':
        print(f"Anchor F0_6 metadata: {a['metadata']}")
        print(f"Placement Error: {a['placementErrorAmount']}")
        print(f"True Distance: {a['distanceToConcrete']}")

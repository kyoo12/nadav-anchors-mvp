import json
import math

with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["id"] == "F2_13":
        print("Left path (Pillar A):")
        for p in a["pillarAPath"]:
            print(f"  {p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}")
        
        print("\nRight path (Pillar B):")
        for p in a["pillarBPath"]:
            print(f"  {p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}")

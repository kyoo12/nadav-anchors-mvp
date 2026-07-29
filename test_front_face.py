import json
import math
import numpy as np

with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["id"] in ["F4_40", "F3_61", "F2_13"]:
        print(f"\n--- Anchor {a['id']} ---")
        for side, path in [("Left", a["pillarAPath"]), ("Right", a["pillarBPath"])]:
            M = path[0]
            # In the current JSON, path[-1] is the pillar point P calculated from min_idx
            # So P is potentially on the back face.
            P_bad = path[-1]
            
            # Let's see all anchors in the path
            print(f"{side} Path:")
            for i, pt in enumerate(path[:-1]):
                print(f"  A{i}: {pt[0]:.2f}, {pt[2]:.2f}")
            print(f"  P_bad: {P_bad[0]:.2f}, {P_bad[2]:.2f}")

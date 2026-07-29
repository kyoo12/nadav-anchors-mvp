import json
import math

with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["id"] == "F2_13":
        path = a["pillarAPath"]
        A_5 = path[-2] # The min_idx anchor
        A_4 = path[-3] # The one before it
        
        # Calculate distances
        M = path[0]
        
        print(f"M: {M[0]:.2f}, {M[2]:.2f}")
        print(f"A_4: {A_4[0]:.2f}, {A_4[2]:.2f}")
        print(f"A_5: {A_5[0]:.2f}, {A_5[2]:.2f}")
        
        dist_M_A4 = math.hypot(A_4[0]-M[0], A_4[2]-M[2])
        dist_M_A5 = math.hypot(A_5[0]-M[0], A_5[2]-M[2])
        print(f"Dist M to A4: {dist_M_A4:.2f}")
        print(f"Dist M to A5: {dist_M_A5:.2f}")

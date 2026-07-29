import json
import math

with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["id"] == "F2_13":
        # The path has points in Web GL coords: x, y, z.
        # Web GL x = rhino x / 1000
        # Web GL z = -rhino y / 1000
        # So Web GL x is proportional to Rhino X, Web GL z is proportional to -Rhino Y.
        
        # Left path
        left_path = a["pillarAPath"]
        M = left_path[0]
        P = left_path[-1] # The last point is the pillar point
        
        print("Trimming Left Path:")
        trimmed_left = [M]
        for pt in left_path[1:-1]:
            MP = [P[0] - M[0], P[2] - M[2]]
            PA = [pt[0] - P[0], pt[2] - P[2]]
            dot = MP[0]*PA[0] + MP[1]*PA[1]
            if dot > 0:
                print(f"Discarding {pt[0]:.2f}, {pt[2]:.2f} (dot={dot:.2f})")
                break
            print(f"Keeping {pt[0]:.2f}, {pt[2]:.2f} (dot={dot:.2f})")
            trimmed_left.append(pt)
        trimmed_left.append(P)
        print(f"Original hops: {len(left_path)-1}, Trimmed hops: {len(trimmed_left)-1}")
        
        # Right path
        right_path = a["pillarBPath"]
        M = right_path[0]
        P = right_path[-1]
        
        print("\nTrimming Right Path:")
        trimmed_right = [M]
        for pt in right_path[1:-1]:
            MP = [P[0] - M[0], P[2] - M[2]]
            PA = [pt[0] - P[0], pt[2] - P[2]]
            dot = MP[0]*PA[0] + MP[1]*PA[1]
            if dot > 0:
                print(f"Discarding {pt[0]:.2f}, {pt[2]:.2f} (dot={dot:.2f})")
                break
            print(f"Keeping {pt[0]:.2f}, {pt[2]:.2f} (dot={dot:.2f})")
            trimmed_right.append(pt)
        trimmed_right.append(P)
        print(f"Original hops: {len(right_path)-1}, Trimmed hops: {len(trimmed_right)-1}")

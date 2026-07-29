import json

with open("web/public/true_anchors.json", "r") as f:
    anchors = json.load(f)

for a in anchors:
    if a["isMiddleAnchor"]:
        left_path = a["pillarAPath"]
        M = left_path[0]
        P = left_path[-1]
        
        A_last = left_path[-2] if len(left_path) > 1 else None
        
        if A_last:
            MP = [P[0] - M[0], P[2] - M[2]]
            PA = [A_last[0] - P[0], A_last[2] - P[2]]
            dot = MP[0]*PA[0] + MP[1]*PA[1]
            if dot <= 0:
                print(f"FAILED TRIM? Anchor {a['id']} Left: A_last={A_last[0]:.1f},{A_last[2]:.1f}, P={P[0]:.1f},{P[2]:.1f}, dot={dot:.2f}")

        right_path = a["pillarBPath"]
        M = right_path[0]
        P = right_path[-1]
        
        A_last = right_path[-2] if len(right_path) > 1 else None
        
        if A_last:
            MP = [P[0] - M[0], P[2] - M[2]]
            PA = [A_last[0] - P[0], A_last[2] - P[2]]
            dot = MP[0]*PA[0] + MP[1]*PA[1]
            if dot <= 0:
                print(f"FAILED TRIM? Anchor {a['id']} Right: A_last={A_last[0]:.1f},{A_last[2]:.1f}, P={P[0]:.1f},{P[2]:.1f}, dot={dot:.2f}")


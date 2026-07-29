import re

with open('extract_segmented.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the export logic
pattern = r'    export_anchors = \[\]\n    for f_idx in range\(len\(floors\)\):.*?    print\(f"Exported \{len\(export_anchors\)\} anchors'
new_code = """    export_anchors = []
    for f_idx in range(len(floors)):
        floor_group = [col[f_idx] for col in columns]
        
        # Precompute nearest pillar distances and points for all anchors on this floor
        dists_to_pillar = []
        closest_pillar_points = []
        for a in floor_group:
            anchor_2d = [a['rhino_x'], a['rhino_y']]
            min_d = float('inf')
            min_p_pt = None
            for p_data in pillars_data:
                d, idx = p_data['tree'].query(anchor_2d)
                if d < min_d:
                    min_d = d
                    min_p_pt = p_data['pts_3d'][idx]
            dists_to_pillar.append(min_d)
            closest_pillar_points.append(min_p_pt)
            
        for i, a in enumerate(floor_group):
            three_x = a['rhino_x'] / 1000.0
            three_y = a['rhino_z'] / 1000.0
            three_z = -a['rhino_y'] / 1000.0
            yaw = -a['rhino_yaw']
            
            is_roof = (f_idx == len(floors) - 1)
            floor_prefix = "Roof" if is_roof else f"F{f_idx}"
            
            middle_indices = [4, 13, 22, 31, 40, 58, 73, 70, 61, 49]
            is_middle = (i in middle_indices)
            
            pillar_a_dist, pillar_b_dist = None, None
            pillar_a_path, pillar_b_path = None, None
            
            if is_middle and len(pillars_data) >= 2:
                # Find left pillar (step -1)
                min_val_left = float('inf')
                min_idx_left = -1
                for step in range(1, 15):
                    idx = (i - step) % len(floor_group)
                    if dists_to_pillar[idx] < min_val_left:
                        min_val_left = dists_to_pillar[idx]
                        min_idx_left = idx
                        
                path_left = []
                dist_left = 0.0
                curr = i
                while curr != min_idx_left:
                    a_curr = floor_group[curr]
                    path_left.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    nxt = (curr - 1) % len(floor_group)
                    a_nxt = floor_group[nxt]
                    dx = a_nxt['rhino_x'] - a_curr['rhino_x']
                    dy = a_nxt['rhino_y'] - a_curr['rhino_y']
                    dist_left += (dx**2 + dy**2)**0.5
                    curr = nxt
                
                a_curr = floor_group[min_idx_left]
                path_left.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                p_pt = closest_pillar_points[min_idx_left]
                path_left.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                dist_left += dists_to_pillar[min_idx_left]
                
                # Find right pillar (step +1)
                min_val_right = float('inf')
                min_idx_right = -1
                for step in range(1, 15):
                    idx = (i + step) % len(floor_group)
                    if dists_to_pillar[idx] < min_val_right:
                        min_val_right = dists_to_pillar[idx]
                        min_idx_right = idx
                        
                path_right = []
                dist_right = 0.0
                curr = i
                while curr != min_idx_right:
                    a_curr = floor_group[curr]
                    path_right.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    nxt = (curr + 1) % len(floor_group)
                    a_nxt = floor_group[nxt]
                    dx = a_nxt['rhino_x'] - a_curr['rhino_x']
                    dy = a_nxt['rhino_y'] - a_curr['rhino_y']
                    dist_right += (dx**2 + dy**2)**0.5
                    curr = nxt
                    
                a_curr = floor_group[min_idx_right]
                path_right.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                p_pt = closest_pillar_points[min_idx_right]
                path_right.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                dist_right += dists_to_pillar[min_idx_right]
                
                pillar_a_dist = float(dist_left)
                pillar_b_dist = float(dist_right)
                pillar_a_path = path_left
                pillar_b_path = path_right

            export_anchors.append({
                'id': f"{floor_prefix}_{i}",
                'floor': f_idx,
                'x': three_x,
                'y': three_y,
                'z': three_z,
                'pitch': float(a['pitch']),
                'yaw': float(yaw),
                'distanceToConcrete': float(a.get('distanceToConcrete', 0.0)),
                'metadata': a['metadata'],
                'nearestGridX': a.get('nearestGridX', 'N/A'),
                'offsetX': float(a.get('offsetX', 0.0)),
                'nearestGridY': a.get('nearestGridY', 'N/A'),
                'offsetY': float(a.get('offsetY', 0.0)),
                'distanceToFloatingFloor': float(a.get('distanceToFloatingFloor', 0.0)),
                'isMiddleAnchor': is_middle,
                'pillarADistance': pillar_a_dist,
                'pillarBDistance': pillar_b_dist,
                'pillarAPath': pillar_a_path,
                'pillarBPath': pillar_b_path
            })
            
    with open('web/public/true_anchors.json', 'w', encoding='utf-8') as f:
        json.dump(export_anchors, f, indent=2)
        
    print(f"Exported {len(export_anchors)} anchors"""

code = re.sub(pattern, new_code, code, flags=re.DOTALL)

with open('extract_segmented.py', 'w', encoding='utf-8') as f:
    f.write(code)

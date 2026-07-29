import re

with open("extract_segmented.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace pillars_data building logic to map by name
old_pillars = """    print("Building Pillar KDTrees...")
    pillars_data = []
    for obj in model.Objects:
        if obj.Attributes.LayerIndex == col_idx and obj.Geometry.ObjectType == rhino3dm.ObjectType.Mesh:
            pts_2d = []
            for v in obj.Geometry.Vertices:
                pts_2d.append((v.X, v.Y))
            if pts_2d:
                pillars_data.append({
                    'tree': KDTree(pts_2d),
                    'pts_3d': [(v.X, v.Y, v.Z) for v in obj.Geometry.Vertices]
                })"""

new_pillars = """    print("Building Pillar KDTrees...")
    pillars_data = {}
    for obj in model.Objects:
        if obj.Attributes.LayerIndex == col_idx and obj.Geometry.ObjectType == rhino3dm.ObjectType.Mesh:
            pts_2d = []
            for v in obj.Geometry.Vertices:
                pts_2d.append((v.X, v.Y))
            if pts_2d:
                name = obj.Attributes.Name.upper() if obj.Attributes.Name else "UNNAMED"
                pillars_data[name] = {
                    'tree': KDTree(pts_2d),
                    'pts_3d': [(v.X, v.Y, v.Z) for v in obj.Geometry.Vertices]
                }"""

code = code.replace(old_pillars, new_pillars)

# Replace the radial path logic
old_export = """        # Precompute nearest pillar distances and points for radial_group
        dists_to_pillar_rad = []
        closest_pillar_points_rad = []
        for a in radial_group:
            anchor_2d = [a['rhino_x'], a['rhino_y']]
            min_d = float('inf')
            min_p_pt = None
            for p_data in pillars_data:
                d, idx = p_data['tree'].query(anchor_2d)
                if d < min_d:
                    min_d = d
                    min_p_pt = p_data['pts_3d'][idx]
            dists_to_pillar_rad.append(min_d)
            closest_pillar_points_rad.append(min_p_pt)
            
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
                r_idx = radial_group.index(a)
                
                # Find left pillar (step -1)
                min_val_left = float('inf')
                min_idx_left = -1
                for step in range(1, 15):
                    idx = (r_idx - step) % len(radial_group)
                    if dists_to_pillar_rad[idx] < min_val_left:
                        min_val_left = dists_to_pillar_rad[idx]
                        min_idx_left = idx
                        
                path_left = []
                dist_left = 0.0
                curr = r_idx
                while curr != min_idx_left:
                    a_curr = radial_group[curr]
                    path_left.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    nxt = (curr - 1) % len(radial_group)
                    a_nxt = radial_group[nxt]
                    dx = a_nxt['rhino_x'] - a_curr['rhino_x']
                    dy = a_nxt['rhino_y'] - a_curr['rhino_y']
                    dist_left += (dx**2 + dy**2)**0.5
                    curr = nxt
                
                a_curr = radial_group[min_idx_left]
                path_left.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                p_pt = closest_pillar_points_rad[min_idx_left]
                path_left.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                dist_left += dists_to_pillar_rad[min_idx_left]
                
                # Find right pillar (step +1)
                min_val_right = float('inf')
                min_idx_right = -1
                for step in range(1, 15):
                    idx = (r_idx + step) % len(radial_group)
                    if dists_to_pillar_rad[idx] < min_val_right:
                        min_val_right = dists_to_pillar_rad[idx]
                        min_idx_right = idx
                        
                path_right = []
                dist_right = 0.0
                curr = r_idx
                while curr != min_idx_right:
                    a_curr = radial_group[curr]
                    path_right.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    nxt = (curr + 1) % len(radial_group)
                    a_nxt = radial_group[nxt]
                    dx = a_nxt['rhino_x'] - a_curr['rhino_x']
                    dy = a_nxt['rhino_y'] - a_curr['rhino_y']
                    dist_right += (dx**2 + dy**2)**0.5
                    curr = nxt
                    
                a_curr = radial_group[min_idx_right]
                path_right.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                p_pt = closest_pillar_points_rad[min_idx_right]
                path_right.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                dist_right += dists_to_pillar_rad[min_idx_right]
                
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
            })"""

new_export = """        for i, a in enumerate(floor_group):
            three_x = a['rhino_x'] / 1000.0
            three_y = a['rhino_z'] / 1000.0
            three_z = -a['rhino_y'] / 1000.0
            yaw = -a['rhino_yaw']
            
            is_roof = (f_idx == len(floors) - 1)
            floor_prefix = "Roof" if is_roof else f"F{f_idx}"
            
            mapping = {
                4: ('P0', 'P1'),
                13: ('P1', 'P2'),
                22: ('P2', 'P3'),
                31: ('P3', 'P4'),
                40: ('P4', 'P5'),
                58: ('P5', 'P6'),
                73: ('P6', 'P7'),
                70: ('P7', 'W1'),
                61: ('W2', 'P8'),
                49: ('P8', 'P9')
            }
            
            is_middle = (i in mapping)
            
            pillar_a_dist, pillar_b_dist = None, None
            pillar_a_path, pillar_b_path = None, None
            pillar_a_label, pillar_b_label = "Pillar A", "Pillar B"
            
            if is_middle:
                name_a, name_b = mapping[i]
                tree_a = pillars_data.get(name_a)
                tree_b = pillars_data.get(name_b)
                
                if tree_a and tree_b:
                    r_idx = radial_group.index(a)
                    
                    def find_pillar_in_dir(step_dir):
                        min_dist_a = float('inf')
                        min_dist_b = float('inf')
                        idx_a = -1
                        idx_b = -1
                        
                        for step in range(1, 15):
                            idx = (r_idx + step * step_dir) % len(radial_group)
                            a_curr = radial_group[idx]
                            a_2d = [a_curr['rhino_x'], a_curr['rhino_y']]
                            
                            da, _ = tree_a['tree'].query(a_2d)
                            db, _ = tree_b['tree'].query(a_2d)
                            
                            if da < min_dist_a:
                                min_dist_a = da
                                idx_a = idx
                            if db < min_dist_b:
                                min_dist_b = db
                                idx_b = idx
                                
                        if min_dist_a < min_dist_b:
                            return name_a, tree_a, min_dist_a, idx_a
                        else:
                            return name_b, tree_b, min_dist_b, idx_b

                    # Trace left (-1)
                    target_name_left, target_tree_left, _, min_idx_left = find_pillar_in_dir(-1)
                    path_left = []
                    dist_left = 0.0
                    curr = r_idx
                    while curr != min_idx_left:
                        a_curr = radial_group[curr]
                        path_left.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                        nxt = (curr - 1) % len(radial_group)
                        a_nxt = radial_group[nxt]
                        dist_left += math.hypot(a_nxt['rhino_x'] - a_curr['rhino_x'], a_nxt['rhino_y'] - a_curr['rhino_y'])
                        curr = nxt
                    
                    a_curr = radial_group[min_idx_left]
                    path_left.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    d, idx_p = target_tree_left['tree'].query([a_curr['rhino_x'], a_curr['rhino_y']])
                    p_pt = target_tree_left['pts_3d'][idx_p]
                    path_left.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                    dist_left += d
                    
                    # Trace right (+1)
                    target_name_right, target_tree_right, _, min_idx_right = find_pillar_in_dir(+1)
                    path_right = []
                    dist_right = 0.0
                    curr = r_idx
                    while curr != min_idx_right:
                        a_curr = radial_group[curr]
                        path_right.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                        nxt = (curr + 1) % len(radial_group)
                        a_nxt = radial_group[nxt]
                        dist_right += math.hypot(a_nxt['rhino_x'] - a_curr['rhino_x'], a_nxt['rhino_y'] - a_curr['rhino_y'])
                        curr = nxt
                        
                    a_curr = radial_group[min_idx_right]
                    path_right.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    d, idx_p = target_tree_right['tree'].query([a_curr['rhino_x'], a_curr['rhino_y']])
                    p_pt = target_tree_right['pts_3d'][idx_p]
                    path_right.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                    dist_right += d
                    
                    pillar_a_dist = float(dist_left)
                    pillar_b_dist = float(dist_right)
                    pillar_a_path = path_left
                    pillar_b_path = path_right
                    pillar_a_label = target_name_left
                    pillar_b_label = target_name_right

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
                'pillarBPath': pillar_b_path,
                'pillarALabel': pillar_a_label,
                'pillarBLabel': pillar_b_label
            })"""

code = code.replace(old_export, new_export)

with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(code)

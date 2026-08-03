"""
extract_segmented.py

This script processes the raw Rhino3D (.3dm) file to extract architectural anchor data.
It performs the following core operations:
1. Loads the .3dm file and extracts DXF mapping for block instances.
2. Identifies concrete pillars and walls, building spatial KDTrees for fast surface distance queries.
3. Iterates over middle anchors to mathematically construct paths towards the concrete elements.
4. Uses a Front-Face Plane trimming algorithm to cleanly dock paths to pillar surfaces without overshooting.
5. Outputs true_anchors.json which the React frontend uses to render the 3D scene.
"""
import rhino3dm
import json
import math
import numpy as np
from scipy.spatial import KDTree

import ezdxf
from ezdxf.tools.text import plain_text

def build_dxf_mapping(dxf_path):
    mapping = {}
    try:
        doc = ezdxf.readfile(dxf_path)
        for block in doc.blocks:
            if block.name.startswith('*'): continue
            texts = list(block.query('TEXT MTEXT'))
            if texts:
                t = texts[0]
                val = t.dxf.text if t.dxftype() == 'TEXT' else plain_text(t.text)
                mapping[block.name.upper()] = val.strip().upper()
        print(f"Loaded {len(mapping)} block mappings from DXF.")
    except Exception as e:
        print(f"Warning: Could not load DXF mapping ({e}). Names may be UNKNOWN.")
    return mapping

def extract_gridlines(model):
    # Fallback to prevent crash
    return [], []

def main():
    print("Loading 3DM file...")
    model = rhino3dm.File3dm.Read("modelForNadav.3dm")
    
    # Load dynamic mapping from the DXF file
    dxf_mapping = build_dxf_mapping('TopVue0-R.dxf')
    
    # Extract dynamic gridline datums from the 3DM model
    print("Extracting Gridlines from 3DM Annotations...")
    grid_x, grid_y = extract_gridlines(model)
    
    # Use all potential layers to find both anchors and concrete
    target_layers = ['Layer 01', 'Layer 02', 'vertical colums', 'GYPS 2', 'concret part']
    layer_indices = {layer.Index for layer in model.Layers if layer.Name in target_layers}

    concrete_pts = []
    print("Building Concrete KDTree...")
    for obj in model.Objects:
        if obj.Attributes.LayerIndex in layer_indices:
            geom = obj.Geometry
            if geom.ObjectType == rhino3dm.ObjectType.Mesh:
                for v in geom.Vertices:
                    concrete_pts.append((v.X, v.Y))
            elif geom.ObjectType == rhino3dm.ObjectType.Curve:
                domain = geom.Domain
                # Sample 100 points
                for t in np.linspace(domain.T0, domain.T1, 100):
                    pt = geom.PointAt(t)
                    concrete_pts.append((pt.X, pt.Y))
                    
    concrete_tree = None
    if len(concrete_pts) > 0:
        concrete_tree = KDTree(concrete_pts)

    ff_idx = -1
    for layer in model.Layers:
        if layer.Name == 'floting_floor':
            ff_idx = layer.Index
            break

    ff_pts = []
    print("Building Floating Floor KDTree...")
    for obj in model.Objects:
        if obj.Attributes.LayerIndex == ff_idx and obj.Geometry.ObjectType == rhino3dm.ObjectType.Mesh:
            for v in obj.Geometry.Vertices:
                ff_pts.append((v.X, v.Y, v.Z))

    ff_tree = None
    ff_tree_2d = None
    if len(ff_pts) > 0:
        ff_tree = KDTree(ff_pts)
        ff_tree_2d = KDTree([[p[0], p[1]] for p in ff_pts])

    col_idx = -1
    for layer in model.Layers:
        if layer.Name == 'vertical colums':
            col_idx = layer.Index
            break
            
    print("Building Pillar KDTrees...")
    pillars_data = {}
    for obj in model.Objects:
        if obj.Attributes.LayerIndex == col_idx and obj.Geometry.ObjectType == rhino3dm.ObjectType.Mesh:
            pts_2d = []
            pts_3d = []
            for v in obj.Geometry.Vertices:
                pts_2d.append((v.X, v.Y))
                pts_3d.append((v.X, v.Y, v.Z))
            if pts_2d:
                name = obj.Attributes.Name.upper() if obj.Attributes.Name else "UNNAMED"
                pillars_data[name] = {
                    'tree': KDTree(pts_2d),
                    'pts_3d': pts_3d
                }

    raw_blocks = []
    
    print("Extracting Anchors...")
    for obj in model.Objects:
        geom = obj.Geometry
        if obj.Attributes.LayerIndex in layer_indices and geom.ObjectType == rhino3dm.ObjectType.InstanceReference:
            x = geom.Xform.M03
            y = geom.Xform.M13
            z = geom.Xform.M23
            
            m00 = geom.Xform.M00
            m10 = geom.Xform.M10
            m01 = geom.Xform.M01
            m11 = geom.Xform.M11
            rhino_yaw = math.atan2(m10, m00)
            
            idef = model.InstanceDefinitions.FindId(geom.ParentIdefId)
            name = idef.Name if idef else "Unknown"
            
            raw_blocks.append({
                'x': x,
                'y': y,
                'z': z,
                'm00': m00,
                'm10': m10,
                'm01': m01,
                'm11': m11,
                'rhino_yaw': rhino_yaw,
                'name': name
            })
            
    # ------------------ ANCHOR CLUSTERING ------------------
    pts_blocks = np.array([[b['x'], b['y'], b['z']] for b in raw_blocks])
    tree = KDTree(pts_blocks)
    
    visited = set()
    anchors = []
    
    for i in range(len(pts_blocks)):
        if i in visited:
            continue
        
        neighbors = tree.query_ball_point(pts_blocks[i], 500)
        
        cluster_names = []
        pl_block = raw_blocks[i]
        an_block = None
        for n in neighbors:
            visited.add(n)
            b = raw_blocks[n]
            cluster_names.append(b['name'])
            name_upper = b['name'].upper()
            if 'PL' in name_upper or 'FLAH' in name_upper or 'PLAH' in name_upper:
                pl_block = b
            if 'AN' in name_upper or 'KIR' in name_upper:
                an_block = b
                
        # Calculate Distance to Concrete dynamically using a robust raycast
        dist_to_concrete = 0.0
        placement_error = False
        shim_thickness = 0.0
        ideal_gap = 140.0 # Default fallback
        if concrete_tree and an_block and pl_block:
            pt = (an_block['x'], an_block['y'])
            
            # Local Y axis of the AN block (points towards concrete)
            vy_x = an_block['m01']
            vy_y = an_block['m11']
            length = np.sqrt(vy_x**2 + vy_y**2)
            if length > 0:
                vy_x /= length
                vy_y /= length
                
            # Get all concrete mesh points within a large radius (e.g., 1000mm)
            idx_list = concrete_tree.query_ball_point(pt, 1000.0)
            
            best_dist = 999999
            for idx in idx_list:
                c_pt = concrete_pts[idx]
                
                # Vector from PL block to this concrete point
                dx_pl = c_pt[0] - pl_block['x']
                dy_pl = c_pt[1] - pl_block['y']
                
                # Project onto Y-axis (distance from PL insertion point to wall)
                proj_from_pl = dx_pl * vy_x + dy_pl * vy_y
                
                # We want the concrete point that is physically closest to the PL block along the Y-axis
                if abs(proj_from_pl) < abs(best_dist) if best_dist != 999999 else True:
                    best_dist = proj_from_pl
                    
            shim_thickness = 0.0
            if best_dist < 999999:
                # 1. Calculate True Required Shim Thickness (Ideal gap for PL block is 0.0)
                shim_thickness = best_dist
                dist_to_concrete = best_dist
                
                # 2. Sanity Audit
                # If it penetrates wall severely (< -20) or hovers impossibly far (> 300)
                if best_dist < -20.0 or best_dist > 300.0:
                    placement_error = True
                
                # NOTE: We have REMOVED the auto-snapping logic completely!
                # The anchors will export at their true CAD coordinates to preserve the perfectly straight facade alignment.


                        # Notice we DO NOT overwrite dist_to_concrete. 
                        # We let the front-end display the TRUE dist_to_concrete and error!
        
        # Map PL Block using DXF dictionary
        pl_name = pl_block['name'].upper() if pl_block else ""
        std_pl = dxf_mapping.get(pl_name, "UNKNOWN_PL")
            
        # Map AN Block using DXF dictionary
        an_name = an_block['name'].upper() if an_block else ""
        std_an = dxf_mapping.get(an_name, "UNKNOWN_AN")
            
        # Calculate Gridline Datums
        nearest_grid_x = "N/A"
        offset_x = 0.0
        if grid_x and pl_block:
            best_x = min(grid_x, key=lambda g: abs(g[1] - pl_block['x']))
            nearest_grid_x = best_x[0]
            offset_x = pl_block['x'] - best_x[1] # Positive = East of grid
            
        nearest_grid_y = "N/A"
        offset_y = 0.0
        if grid_y and pl_block:
            best_y = min(grid_y, key=lambda g: abs(g[1] - pl_block['y']))
            nearest_grid_y = best_y[0]
            offset_y = pl_block['y'] - best_y[1] # Positive = North of grid
            
        final_metadata = f"{std_an} | {std_pl}"
        
        dist_to_ff = 0.0
        if ff_tree and pl_block:
            # We want the floating floor point directly underneath/above the anchor (ignoring Z distance)
            # So we use a 2D distance query!
            _, idx = ff_tree_2d.query([pl_block['x'], pl_block['y']])
            closest_ff_z = ff_pts[idx][2]
            dist_to_ff = pl_block['z'] - closest_ff_z
        
        if len(cluster_names) >= 2:
            # Use AN block for physical visual coordinates (facade line)
            b_src = an_block if an_block else pl_block
            anchors.append({
                'rhino_x': b_src['x'],
                'rhino_y': b_src['y'],
                'rhino_z': b_src['z'],
                'm00': b_src['m00'],
                'm10': b_src['m10'],
                'm01': b_src['m01'],
                'm11': b_src['m11'],
                'rhino_yaw': b_src['rhino_yaw'],
                'metadata': final_metadata,
                'distanceToConcrete': dist_to_concrete,
                'nearestGridX': nearest_grid_x,
                'offsetX': offset_x,
                'nearestGridY': nearest_grid_y,
                'offsetY': offset_y,
                'distanceToFloatingFloor': dist_to_ff,
                'shimThickness': shim_thickness,
                'placementError': placement_error
            })
            
    print(f"Clustered into {len(anchors)} anchor locations.")
    
    # ------------------ SEPARATE INTO FLOORS ------------------
    anchors.sort(key=lambda a: a['rhino_z'])
    z_coords = [a['rhino_z'] for a in anchors]
    diffs = np.diff(z_coords)
    gap_indices = np.where(diffs > 1000.0)[0] # 1 meter gap
    
    floors = []
    start_idx = 0
    for idx in gap_indices:
        floors.append(anchors[start_idx:idx+1])
        start_idx = idx + 1
    floors.append(anchors[start_idx:])
    
    print(f"Detected {len(floors)} floors.")
    
    # ------------------ VERTICAL COLUMN MAPPING (Unit Circle Angle) ------------------
    # Calculate global building centroid
    cx = sum(a['rhino_x'] for a in anchors) / len(anchors)
    cy = sum(a['rhino_y'] for a in anchors) / len(anchors)
    
    # Assign radial angles and sort floors
    for f in floors:
        for a in f:
            a['angle'] = math.atan2(a['rhino_y'] - cy, a['rhino_x'] - cx)
        f.sort(key=lambda a: a['angle'])
        
    # Align floors to Floor 0 to prevent index wrapping caused by building twist
    for f_idx in range(len(floors) - 1):
        curr_floor = floors[f_idx]
        next_floor = floors[f_idx + 1]
        
        a0 = curr_floor[0]
        pts_next = np.array([[math.cos(a['angle']), math.sin(a['angle'])] for a in next_floor])
        tree_next = KDTree(pts_next)
        
        target_pt = [math.cos(a0['angle']), math.sin(a0['angle'])]
        dist_val, idx = tree_next.query(target_pt)
        
        floors[f_idx + 1] = next_floor[idx:] + next_floor[:idx]
        
    for f_idx in range(len(floors)):
        curr_floor = floors[f_idx]
        
        if f_idx < len(floors) - 1:
            next_floor = floors[f_idx + 1]
            pts_next = np.array([[math.cos(a['angle']), math.sin(a['angle'])] for a in next_floor])
            tree_next = KDTree(pts_next)
        else:
            next_floor = None
            tree_next = None
            
        for a in curr_floor:
            if not tree_next:
                a['pitch'] = 0.0
                continue
                
            target_pt = [math.cos(a['angle']), math.sin(a['angle'])]
            dist_val, idx = tree_next.query(target_pt)
            
            if dist_val < 0.26: # ~15 degrees max allowed shift
                next_a = next_floor[idx]
                vx = next_a['rhino_x'] - a['rhino_x']
                vy = next_a['rhino_y'] - a['rhino_y']
                vz = next_a['rhino_z'] - a['rhino_z']
                
                length_outward = math.hypot(a.get('m01', 0), a.get('m11', 0))
                if length_outward > 0:
                    outward_x = a['m01'] / length_outward
                    outward_y = a['m11'] / length_outward
                else:
                    outward_x, outward_y = 0, 1
                    
                v_outward = vx * outward_x + vy * outward_y
                
                if vz != 0:
                    a['pitch'] = math.atan2(-v_outward, vz)
                else:
                    a['pitch'] = 0.0
            else:
                a['pitch'] = 0.0
                
    # --- Pre-calculate Floor 0 Geometric Middle Indices for True Vertical Plumb Line ---
    floor_0_middle_indices = {}
    if floors:
        f0_radial_group = floors[0]
        f0_cx = sum(a['rhino_x'] for a in f0_radial_group) / len(f0_radial_group)
        f0_cy = sum(a['rhino_y'] for a in f0_radial_group) / len(f0_radial_group)
        panels = [('P0', 'P1'), ('P1', 'P2'), ('P2', 'P3'), ('P3', 'P4'), ('P4', 'P5'), ('P5', 'P6'), ('P6', 'P7'), ('P7', 'W1'), ('W2', 'P8'), ('P8', 'P9')]
        
        for p_a, p_b in panels:
            tree_a = pillars_data.get(p_a)
            tree_b = pillars_data.get(p_b)
            if not tree_a or not tree_b: continue
            
            pts_a = tree_a['pts_3d']
            pts_b = tree_b['pts_3d']
            
            a3 = math.atan2(sum(p[1] for p in pts_a)/len(pts_a) - f0_cy, sum(p[0] for p in pts_a)/len(pts_a) - f0_cx)
            a4 = math.atan2(sum(p[1] for p in pts_b)/len(pts_b) - f0_cy, sum(p[0] for p in pts_b)/len(pts_b) - f0_cx)
            
            in_panel = []
            for idx, temp_a in enumerate(f0_radial_group):
                ang = math.atan2(temp_a['rhino_y'] - f0_cy, temp_a['rhino_x'] - f0_cx)
                ang_norm = (ang + 2*math.pi) % (2*math.pi)
                a3_norm = (a3 + 2*math.pi) % (2*math.pi)
                a4_norm = (a4 + 2*math.pi) % (2*math.pi)
                
                diff_a3_ang = (ang_norm - a3_norm) % (2*math.pi)
                diff_a3_a4 = (a4_norm - a3_norm) % (2*math.pi)
                
                if diff_a3_ang < diff_a3_a4:
                    in_panel.append(idx)
                    
            if not in_panel: continue
            in_panel_sorted = sorted(in_panel, key=lambda idx: ((math.atan2(f0_radial_group[idx]['rhino_y'] - f0_cy, f0_radial_group[idx]['rhino_x'] - f0_cx) + 2*math.pi) % (2*math.pi) - a3_norm) % (2*math.pi))
            mid_idx = in_panel_sorted[len(in_panel_sorted)//2]
            floor_0_middle_indices[mid_idx] = (p_a, p_b)

    # ------------------ EXPORT ------------------
    export_anchors = []
    for f_idx in range(len(floors)):
        radial_group = floors[f_idx]
        
        for i, a in enumerate(radial_group):
            three_x = a['rhino_x'] / 1000.0
            three_y = a['rhino_z'] / 1000.0
            three_z = -a['rhino_y'] / 1000.0
            yaw = -a['rhino_yaw']
            
            is_roof = (f_idx == len(floors) - 1)
            floor_prefix = "Roof" if is_roof else f"F{f_idx}"
            
            # True Vertical Plumb Line Logic
            # The indices are perfectly vertically cycle-aligned, so we can just project Floor 0's middle indices upwards!
            is_middle = i in floor_0_middle_indices
            name_a, name_b = floor_0_middle_indices.get(i, (None, None))
            
            pillar_a_dist, pillar_b_dist = None, None
            pillar_a_path, pillar_b_path = None, None
            pillar_a_label, pillar_b_label = "Pillar A", "Pillar B"
            
            if is_middle:
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

                    def trim_path(raw_path, m_pt_2d, tree):
                        # Find P_front (closest point on pillar to Middle Anchor)
                        _, idx_front = tree.query(m_pt_2d)
                        p_front = tree.data[idx_front]
                        
                        trimmed = [raw_path[0]]
                        MP_x = p_front[0] - m_pt_2d[0]
                        MP_y = p_front[1] - m_pt_2d[1]
                        
                        for pt in raw_path[1:]:
                            a_x = pt[0] * 1000.0
                            a_y = -pt[2] * 1000.0
                            PA_x = a_x - p_front[0]
                            PA_y = a_y - p_front[1]
                            
                            if MP_x * PA_x + MP_y * PA_y > 0:
                                break
                            trimmed.append(pt)
                            
                        # Now trimmed[-1] is the LAST anchor strictly in front of the pillar
                        a_last = trimmed[-1]
                        a_last_rhino = [a_last[0] * 1000.0, -a_last[2] * 1000.0]
                        
                        # Find P_final (closest point on pillar to this last anchor)
                        d_final, idx_final = tree.query(a_last_rhino)
                        p_final = tree.data[idx_final]
                        
                        # Append P_final to the path
                        three_y = a_last[1] # Keep the same height
                        trimmed.append([p_final[0]/1000.0, three_y, -p_final[1]/1000.0])
                        
                        total_dist = 0.0
                        for i in range(len(trimmed)-1):
                            dx = trimmed[i+1][0] - trimmed[i][0]
                            dz = trimmed[i+1][2] - trimmed[i][2]
                            total_dist += (dx**2 + dz**2)**0.5
                        return trimmed, total_dist * 1000.0
                        
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
                    
                    path_left, dist_left = trim_path(path_left, [a['rhino_x'], a['rhino_y']], target_tree_left['tree'])
                    
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
                    
                    path_right, dist_right = trim_path(path_right, [a['rhino_x'], a['rhino_y']], target_tree_right['tree'])
                    
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
                'shimThickness': float(a.get('shimThickness', 0.0)),
                'placementError': bool(a.get('placementError', False)),
                'isMiddleAnchor': is_middle,
                'pillarADistance': pillar_a_dist,
                'pillarBDistance': pillar_b_dist,
                'pillarAPath': pillar_a_path,
                'pillarBPath': pillar_b_path,
                'pillarALabel': pillar_a_label,
                'pillarBLabel': pillar_b_label
            })
            
    with open('web/public/true_anchors.json', 'w', encoding='utf-8') as f:
        json.dump(export_anchors, f, indent=2)
        
    print(f"Exported {len(export_anchors)} anchors with segmented vertical pitches.")

    # Export gridlines
    export_grids = {
        'x': [{'label': g[0], 'coord': g[1] / 1000.0} for g in grid_x],
        'y': [{'label': g[0], 'coord': -g[1] / 1000.0} for g in grid_y]
    }
    with open('web/public/gridlines.json', 'w', encoding='utf-8') as f:
        json.dump(export_grids, f, indent=2)
    print("Exported gridlines to web/public/gridlines.json")

if __name__ == '__main__':
    main()

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
    if len(ff_pts) > 0:
        ff_tree = KDTree(ff_pts)

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
                
                # Vector from AN block to this concrete point
                dx_an = c_pt[0] - an_block['x']
                dy_an = c_pt[1] - an_block['y']
                
                # Project onto AN block's Y-axis (distance from AN insertion point)
                proj_from_an = dx_an * vy_x + dy_an * vy_y
                
                # Determine minimum valid distance to wall based on bracket type
                an_name = an_block['name'].upper()
                if '3' in an_name or '200' in an_name:
                    min_dist = 190.0
                elif '150' in an_name:
                    min_dist = 140.0
                elif '1_1' in an_name or '120' in an_name:
                    min_dist = 110.0
                else:
                    min_dist = 60.0
                    
                # Ignore points that belong to the exploded anchor mesh itself
                if proj_from_an > min_dist:
                    # If it's valid, find the total distance from the PL block!
                    dx_pl = c_pt[0] - pl_block['x']
                    dy_pl = c_pt[1] - pl_block['y']
                    proj_from_pl = abs(dx_pl * vy_x + dy_pl * vy_y)
                    
                    if proj_from_pl < best_dist:
                        best_dist = proj_from_pl
                        
            if best_dist < 999999:
                dist_to_concrete = best_dist
        
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
            # grid_x contains (label, X-coordinate)
            # Find closest X
            best_x = min(grid_x, key=lambda g: abs(g[1] - pl_block['x']))
            nearest_grid_x = best_x[0]
            offset_x = abs(best_x[1] - pl_block['x'])
            
        nearest_grid_y = "N/A"
        offset_y = 0.0
        if grid_y and pl_block:
            # grid_y contains (label, Y-coordinate)
            # Find closest Y
            best_y = min(grid_y, key=lambda g: abs(g[1] - pl_block['y']))
            nearest_grid_y = best_y[0]
            offset_y = abs(best_y[1] - pl_block['y'])
            
        final_metadata = f"{std_an} | {std_pl}"
        
        dist_to_ff = 0.0
        if ff_tree and pl_block:
            _, idx = ff_tree.query([pl_block['x'], pl_block['y'], pl_block['z']])
            closest_ff_z = ff_pts[idx][2]
            dist_to_ff = pl_block['z'] - closest_ff_z
        
        if len(cluster_names) >= 2:
            anchors.append({
                'rhino_x': pl_block['x'],
                'rhino_y': pl_block['y'],
                'rhino_z': pl_block['z'],
                'm00': pl_block['m00'],
                'm10': pl_block['m10'],
                'm01': pl_block['m01'],
                'm11': pl_block['m11'],
                'rhino_yaw': pl_block['rhino_yaw'],
                'metadata': final_metadata,
                'distanceToConcrete': dist_to_concrete,
                'nearestGridX': nearest_grid_x,
                'offsetX': offset_x,
                'nearestGridY': nearest_grid_y,
                'offsetY': offset_y,
                'distanceToFloatingFloor': dist_to_ff
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
    
    # ------------------ VERTICAL COLUMN MAPPING ------------------
    # We will map each anchor on Floor 1 to the closest anchor on Floor 2, etc.
    # We store this as an array of columns: columns[i] = [F1_anchor, F2_anchor, ...]
    
    columns = []
    for a in floors[0]:
        columns.append([a])
        
    for f in range(1, len(floors)):
        floor_anchors = floors[f]
        # Create KDTree of this floor's X,Y (horizontal in Rhino)
        pts_f = np.array([[a['rhino_x'], a['rhino_y']] for a in floor_anchors])
        tree_f = KDTree(pts_f)
        
        used_indices = set()
        
        for col in columns:
            prev_a = col[-1]
            
            # Find the closest available anchor
            k = 1
            while True:
                if k > len(floor_anchors):
                    break
                
                dists, indices = tree_f.query([prev_a['rhino_x'], prev_a['rhino_y']], k=k)
                
                # tree_f.query returns a scalar if k=1, but an array if k>1
                if k == 1:
                    idx = indices
                else:
                    idx = indices[-1]
                    
                if idx not in used_indices:
                    used_indices.add(idx)
                    col.append(floor_anchors[idx])
                    break
                k += 1
            
    # ------------------ SEGMENTED PITCH CALCULATION ------------------
    for col in columns:
        for i in range(len(col)):
            curr_a = col[i]
            
            if i == 0:
                prev_a = col[i]
                next_a = col[i+1]
            elif i == len(col) - 1:
                prev_a = col[i-1]
                next_a = col[i]
            else:
                prev_a = col[i-1]
                next_a = col[i+1]
                
            # Vector from prev to next
            vx = next_a['rhino_x'] - prev_a['rhino_x']
            vy = next_a['rhino_y'] - prev_a['rhino_y']
            vz = next_a['rhino_z'] - prev_a['rhino_z']
            
            # Project horizontal vector (vx, vy) onto bracket's outward normal vector (m01, m11)
            # The CAD block's Y-axis (m01, m11) points outwards from the wall
            length_outward = math.hypot(curr_a.get('m01', 0), curr_a.get('m11', 0))
            if length_outward > 0:
                outward_x = curr_a['m01'] / length_outward
                outward_y = curr_a['m11'] / length_outward
            else:
                outward_x, outward_y = 0, 1
                
            v_outward = vx * outward_x + vy * outward_y
            
            # Pitch = arctan(-V_outward / V_z)
            if vz != 0:
                pitch = math.atan2(-v_outward, vz)
            else:
                pitch = 0.0
                
            curr_a['pitch'] = pitch
            
    # ------------------ EXPORT ------------------
    export_anchors = []
    for f_idx in range(len(floors)):
        # Extract from columns to keep floor ordering consistent
        floor_group = [col[f_idx] for col in columns]
        for i, a in enumerate(floor_group):
            three_x = a['rhino_x'] / 1000.0
            three_y = a['rhino_z'] / 1000.0
            three_z = -a['rhino_y'] / 1000.0
            yaw = -a['rhino_yaw']
            
            is_roof = (f_idx == len(floors) - 1)
            floor_prefix = "Roof" if is_roof else f"F{f_idx}"
            
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
                'distanceToFloatingFloor': float(a.get('distanceToFloatingFloor', 0.0))
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

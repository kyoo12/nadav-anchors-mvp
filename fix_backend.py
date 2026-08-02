with open("extract_segmented.py", "r", encoding="utf-8") as f:
    script = f.read()

# 1. Clustering Radius
script = script.replace("neighbors = tree.query_ball_point(pts_blocks[i], 500)",
                        "neighbors = tree.query_ball_point(pts_blocks[i], 150)")

# 2. Concrete Distance `abs` bug and saving Error metrics
script = script.replace("""                    # If it's valid, find the total distance from the PL block!
                    dx_pl = c_pt[0] - pl_block['x']
                    dy_pl = c_pt[1] - pl_block['y']
                    proj_from_pl = abs(dx_pl * vy_x + dy_pl * vy_y)
                    
                    if proj_from_pl < best_dist:
                        best_dist = proj_from_pl
                        
            if best_dist < 999999:
                # 1. Sanity Audit
                if best_dist < 20.0 or best_dist > ideal_gap + 300.0:
                    placement_error = True
                    dist_to_concrete = best_dist
                else:
                    # 2. Surface Snapping Auto-Correction
                    shift_amount = best_dist - ideal_gap
                    if abs(shift_amount) > 1.0:
                        pl_block['x'] += shift_amount * vy_x
                        pl_block['y'] += shift_amount * vy_y
                    dist_to_concrete = ideal_gap""",
"""                    # If it's valid, find the total distance from the PL block!
                    dx_pl = c_pt[0] - pl_block['x']
                    dy_pl = c_pt[1] - pl_block['y']
                    proj_from_pl = dx_pl * vy_x + dy_pl * vy_y
                    
                    # We want the absolute value ONLY to find the closest concrete vertex, 
                    # but we must preserve the sign (embedded vs gap).
                    if abs(proj_from_pl) < abs(best_dist) if best_dist != 999999 else True:
                        best_dist = proj_from_pl
                        
            placement_error_amount = 0.0
            if best_dist < 999999:
                # 1. Calculate True Placement Error
                placement_error_amount = best_dist - ideal_gap
                
                # Report the TRUE distance, not the snapped distance!
                dist_to_concrete = best_dist
                
                # 2. Sanity Audit
                # If it penetrates wall (best_dist < 20) or hovers too far
                if best_dist < 20.0 or best_dist > ideal_gap + 300.0:
                    placement_error = True
                else:
                    # 3. Surface Snapping Auto-Correction (for Visual 3D model ONLY)
                    # We still shift the coordinates in the JSON so the 3D viewer looks perfect.
                    if abs(placement_error_amount) > 1.0:
                        pl_block['x'] += placement_error_amount * vy_x
                        pl_block['y'] += placement_error_amount * vy_y
                        # Notice we DO NOT overwrite dist_to_concrete. 
                        # We let the front-end display the TRUE dist_to_concrete and error!""")


# Initialize placement_error_amount at the top of the loop
script = script.replace("        placement_error = False", "        placement_error = False\n        placement_error_amount = 0.0")


# 3. Gridline signs
script = script.replace("""        if grid_x and pl_block:
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
            offset_y = abs(best_y[1] - pl_block['y'])""",
"""        if grid_x and pl_block:
            best_x = min(grid_x, key=lambda g: abs(g[1] - pl_block['x']))
            nearest_grid_x = best_x[0]
            offset_x = pl_block['x'] - best_x[1] # Positive = East of grid
            
        nearest_grid_y = "N/A"
        offset_y = 0.0
        if grid_y and pl_block:
            best_y = min(grid_y, key=lambda g: abs(g[1] - pl_block['y']))
            nearest_grid_y = best_y[0]
            offset_y = pl_block['y'] - best_y[1] # Positive = North of grid""")

# 4. JSON Export
script = script.replace("'distanceToFloatingFloor': dist_to_ff,",
                        "'distanceToFloatingFloor': dist_to_ff,\n                'placementErrorAmount': placement_error_amount,")
script = script.replace("'distanceToFloatingFloor': float(a.get('distanceToFloatingFloor', 0.0)),",
                        "'distanceToFloatingFloor': float(a.get('distanceToFloatingFloor', 0.0)),\n                'placementErrorAmount': float(a.get('placementErrorAmount', 0.0)),")


with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(script)

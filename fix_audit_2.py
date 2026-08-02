with open("extract_segmented.py", "r", encoding="utf-8") as f:
    script = f.read()

import re

# Remove the whole min_dist calculation block
script = re.sub(r"# Determine minimum valid distance to wall based on bracket type.*?ideal_gap = min_dist", 
                "ideal_gap = 0.0", 
                script, flags=re.DOTALL)


# The loop should just find the closest concrete wall to the PL block
replacement = """            best_dist = 999999
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
                    
            placement_error_amount = 0.0
            if best_dist < 999999:
                # 1. Calculate True Placement Error (Ideal gap for PL block is 0.0)
                placement_error_amount = best_dist
                dist_to_concrete = best_dist
                
                # 2. Sanity Audit
                # If it penetrates wall severely (< -100) or hovers too far (> 150)
                if best_dist < -100.0 or best_dist > 150.0:
                    placement_error = True
                else:
                    # 3. Surface Snapping Auto-Correction
                    if abs(placement_error_amount) > 1.0:
                        pl_block['x'] += placement_error_amount * vy_x
                        pl_block['y'] += placement_error_amount * vy_y
"""

script = re.sub(r"            best_dist = 999999.*?pl_block\['y'\] \+= placement_error_amount \* vy_y", 
                replacement, 
                script, flags=re.DOTALL)

with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(script)

import re

with open("extract_segmented.py", "r", encoding="utf-8") as f:
    code = f.read()

# I need to insert the trim_path function right before target_name_left
old_logic = """                    # Trace left (-1)
                    target_name_left, target_tree_left, _, min_idx_left = find_pillar_in_dir(-1)"""

new_logic = """                    def trim_path(raw_path, p_pt_2d, m_pt_2d):
                        trimmed = [raw_path[0]]
                        MP_x = p_pt_2d[0] - m_pt_2d[0]
                        MP_y = p_pt_2d[1] - m_pt_2d[1]
                        for pt in raw_path[1:-1]:
                            a_x = pt[0] * 1000.0
                            a_y = -pt[2] * 1000.0
                            PA_x = a_x - p_pt_2d[0]
                            PA_y = a_y - p_pt_2d[1]
                            if MP_x * PA_x + MP_y * PA_y > 0:
                                break
                            trimmed.append(pt)
                        trimmed.append(raw_path[-1])
                        total_dist = 0.0
                        for i in range(len(trimmed)-1):
                            dx = trimmed[i+1][0] - trimmed[i][0]
                            dz = trimmed[i+1][2] - trimmed[i][2]
                            total_dist += (dx**2 + dz**2)**0.5
                        return trimmed, total_dist * 1000.0
                        
                    # Trace left (-1)
                    target_name_left, target_tree_left, _, min_idx_left = find_pillar_in_dir(-1)"""

code = code.replace(old_logic, new_logic)


# And replace the dist_left and dist_right calculations with trim_path
old_dist_left = """                    a_curr = radial_group[min_idx_left]
                    path_left.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    d, idx_p = target_tree_left['tree'].query([a_curr['rhino_x'], a_curr['rhino_y']])
                    p_pt = target_tree_left['pts_3d'][idx_p]
                    path_left.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                    dist_left += d"""

new_dist_left = """                    a_curr = radial_group[min_idx_left]
                    path_left.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    d, idx_p = target_tree_left['tree'].query([a_curr['rhino_x'], a_curr['rhino_y']])
                    p_pt = target_tree_left['pts_3d'][idx_p]
                    path_left.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                    
                    path_left, dist_left = trim_path(path_left, [p_pt[0], p_pt[1]], [a['rhino_x'], a['rhino_y']])"""

code = code.replace(old_dist_left, new_dist_left)


old_dist_right = """                    a_curr = radial_group[min_idx_right]
                    path_right.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    d, idx_p = target_tree_right['tree'].query([a_curr['rhino_x'], a_curr['rhino_y']])
                    p_pt = target_tree_right['pts_3d'][idx_p]
                    path_right.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                    dist_right += d"""

new_dist_right = """                    a_curr = radial_group[min_idx_right]
                    path_right.append([a_curr['rhino_x']/1000.0, three_y, -a_curr['rhino_y']/1000.0])
                    d, idx_p = target_tree_right['tree'].query([a_curr['rhino_x'], a_curr['rhino_y']])
                    p_pt = target_tree_right['pts_3d'][idx_p]
                    path_right.append([p_pt[0]/1000.0, three_y, -p_pt[1]/1000.0])
                    
                    path_right, dist_right = trim_path(path_right, [p_pt[0], p_pt[1]], [a['rhino_x'], a['rhino_y']])"""

code = code.replace(old_dist_right, new_dist_right)


with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(code)

with open("extract_segmented.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace .append
old_str = """            if pts_2d:
                pillars_data.append({
                    'tree': KDTree(pts_2d),
                    'pts_3d': pts_3d
                })"""

new_str = """            if pts_2d:
                name = obj.Attributes.Name.upper() if obj.Attributes.Name else "UNNAMED"
                pillars_data[name] = {
                    'tree': KDTree(pts_2d),
                    'pts_3d': pts_3d
                }"""

code = code.replace(old_str, new_str)

with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(code)

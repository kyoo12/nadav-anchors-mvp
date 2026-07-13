import re

with open('extract_segmented.py', 'r') as f:
    code = f.read()

# Remove extract_gridlines function
code = re.sub(r'def extract_gridlines\(.*?(?=def main\(\):)', '', code, flags=re.DOTALL)

# Remove grid extraction calls
code = re.sub(r'print\(\"Extracting Gridlines from 3DM Annotations\.\.\.\"\)\s*grid_lines = extract_gridlines\(model\)\s*print\(f\"Extracted \{len\(grid_lines\[\'x\'\]\)\} X-gridlines and \{len\(grid_lines\[\'y\'\]\)\} Y-gridlines from 3DM\.\"\)', '', code)

# Remove nearestGridX logic
code = re.sub(r'# Calculate layout datums.*?a\[\'offsetY\'\] = abs\(min_y\[1\]\)', '', code, flags=re.DOTALL)

# Remove gridline export block
code = re.sub(r'# Export physical datums.*?print\(\"Exported gridlines to web/public/gridlines\.json\"\)', '', code, flags=re.DOTALL)

with open('extract_segmented.py', 'w') as f:
    f.write(code)

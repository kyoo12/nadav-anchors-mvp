with open("extract_segmented.py", "r", encoding="utf-8") as f:
    content = f.read()

docstring = """\"\"\"
extract_segmented.py

This script processes the raw Rhino3D (.3dm) file to extract architectural anchor data.
It performs the following core operations:
1. Loads the .3dm file and extracts DXF mapping for block instances.
2. Identifies concrete pillars and walls, building spatial KDTrees for fast surface distance queries.
3. Iterates over middle anchors to mathematically construct paths towards the concrete elements.
4. Uses a Front-Face Plane trimming algorithm to cleanly dock paths to pillar surfaces without overshooting.
5. Outputs true_anchors.json which the React frontend uses to render the 3D scene.
\"\"\"
"""

if not content.startswith('"""'):
    content = docstring + content

with open("extract_segmented.py", "w", encoding="utf-8") as f:
    f.write(content)

with open("web/src/components/AnchorVisualizer.tsx", "r", encoding="utf-8") as f:
    content = f.read()

docstring = """/**
 * AnchorVisualizer.tsx
 * 
 * Core 3D rendering component using React Three Fiber.
 * 
 * Performance & Architecture:
 * - Uses InstancedMesh for rendering thousands of standard square anchors in a single draw call.
 * - Split-sphere geometries (Top/Bottom hemispheres) for Middle Anchors to color-code AN vs PL connections without Z-fighting.
 * - Dynamic Line drawing for calculated measurement paths connecting anchors to the structural pillars.
 * - Reactively rebuilds matrices only when the visible floors toggle changes to maintain 60 FPS.
 */
"""

if not content.startswith('/**'):
    content = docstring + content

with open("web/src/components/AnchorVisualizer.tsx", "w", encoding="utf-8") as f:
    f.write(content)

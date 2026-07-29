with open("web/src/App.tsx", "r", encoding="utf-8") as f:
    content = f.read()

docstring = """/**
 * App.tsx
 * 
 * Main React orchestrator for the Nadav Anchors MVP.
 * 
 * Architecture:
 * - Fetches pre-processed anchor data (true_anchors.json) built by extract_segmented.py.
 * - Manages state for UI visibility (floors, square anchor toggle, selected items).
 * - Implements a Tablet-First touch-optimized floating UI (Glassmorphism + 48px touch targets).
 * - Passes active state down to the Three.js AnchorVisualizer for WebGL rendering.
 */
"""

if not content.startswith('/**'):
    content = docstring + content

with open("web/src/App.tsx", "w", encoding="utf-8") as f:
    f.write(content)

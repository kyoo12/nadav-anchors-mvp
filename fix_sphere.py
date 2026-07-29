import re

with open("web/src/components/AnchorVisualizer.tsx", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the single halfSphereGeometry with top and bottom geometries
code = code.replace(
    "const halfSphereGeometry = new THREE.SphereGeometry(0.4, 32, 16, 0, Math.PI);",
    "const topSphereGeometry = new THREE.SphereGeometry(0.4, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2);\nconst bottomSphereGeometry = new THREE.SphereGeometry(0.4, 32, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2);"
)

# Fix the JSX to use top and bottom
code = code.replace(
    "ref={meshRefSpherePL}\n        args={[halfSphereGeometry",
    "ref={meshRefSpherePL}\n        args={[bottomSphereGeometry"
)
code = code.replace(
    "ref={meshRefSphereAN}\n        args={[halfSphereGeometry",
    "ref={meshRefSphereAN}\n        args={[topSphereGeometry"
)

# Remove the rotateZ hack in applyMatrices
code = code.replace("if (isSphere) dummy.rotateZ(Math.PI); // Top hemisphere", "")

# Remove the rotateZ hack in useFrame
code = code.replace("if (isSphere) dummy.rotateZ(Math.PI);", "")

with open("web/src/components/AnchorVisualizer.tsx", "w", encoding="utf-8") as f:
    f.write(code)

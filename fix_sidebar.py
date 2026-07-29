import re

with open("web/src/components/AnchorVisualizer.tsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("pillarBPath?: [number, number, number][];", "pillarBPath?: [number, number, number][];\n  pillarALabel?: string;\n  pillarBLabel?: string;")

with open("web/src/components/AnchorVisualizer.tsx", "w", encoding="utf-8") as f:
    f.write(code)


with open("web/src/components/RightSidebar.tsx", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("<span>Distance to Pillar A</span>", "<span>Distance to Pillar {selectedAnchor.pillarALabel || 'A'}</span>")
code = code.replace("<span>Distance to Pillar B</span>", "<span>Distance to Pillar {selectedAnchor.pillarBLabel || 'B'}</span>")

with open("web/src/components/RightSidebar.tsx", "w", encoding="utf-8") as f:
    f.write(code)

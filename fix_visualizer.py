import re

with open('web/src/components/AnchorVisualizer.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Update Anchor interface
code = code.replace('pillarAPoint?: [number, number, number];', 'pillarAPath?: [number, number, number][];')
code = code.replace('pillarBPoint?: [number, number, number];', 'pillarBPath?: [number, number, number][];')

# Update JSX lines
old_lines = """      {/* 3D Verification Lines to Pillars for hovered/selected Middle Anchors */}
      {middleAnchors.map(a => {
        if (!a.pillarAPoint || !a.pillarBPoint) return null;
        if (a.id !== selectedAnchorId && a.id !== hoveredAnchorId) return null;
        return (
          <group key={`lines-${a.id}`}>
            <Line points={[[a.x, a.y, a.z], a.pillarAPoint]} color="#ea580c" lineWidth={2} dashed={true} dashSize={0.5} gapSize={0.2} opacity={0.6} transparent />
            <Line points={[[a.x, a.y, a.z], a.pillarBPoint]} color="#ea580c" lineWidth={2} dashed={true} dashSize={0.5} gapSize={0.2} opacity={0.6} transparent />
          </group>
        )
      })}"""

new_lines = """      {/* 3D Verification Lines to Pillars for hovered/selected Middle Anchors */}
      {middleAnchors.map(a => {
        if (!a.pillarAPath || !a.pillarBPath) return null;
        if (a.id !== selectedAnchorId && a.id !== hoveredAnchorId) return null;
        return (
          <group key={`lines-${a.id}`}>
            <Line points={a.pillarAPath} color="#10b981" lineWidth={3} dashed={false} opacity={0.8} transparent />
            <Line points={a.pillarBPath} color="#3b82f6" lineWidth={3} dashed={false} opacity={0.8} transparent />
          </group>
        )
      })}"""

code = code.replace(old_lines, new_lines)

with open('web/src/components/AnchorVisualizer.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

import re

with open('web/src/components/AnchorVisualizer.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace useFrame
frame_pattern = r'  // Only run the pulsing animation in useFrame for the selected anchor.*?    meshRefPL\.current\.instanceMatrix\.needsUpdate = true;\n  \}\);\n'
new_frame = """  // Only run the pulsing animation in useFrame for the selected anchor
  useFrame(() => {
    if (!meshRefPL.current || !meshRefAN.current || !meshRefSpherePL.current || !meshRefSphereAN.current || !selectedAnchorId) return;
    
    // Check which array it belongs to
    const isSphere = middleAnchors.some(a => a.id === selectedAnchorId);
    const anchorsList = isSphere ? middleAnchors : regularAnchors;
    const refAN = isSphere ? meshRefSphereAN : meshRefAN;
    const refPL = isSphere ? meshRefSpherePL : meshRefPL;
    
    const selectedIdx = anchorsList.findIndex(a => a.id === selectedAnchorId);
    if (selectedIdx === -1) return;

    const anchor = anchorsList[selectedIdx];
    
    const time = Date.now() / 1000;
    const baseScale = isSphere ? 1.7 : 1.15;
    const scale = baseScale + Math.sin(time * 5) * 0.15;
    
    // Animate AN half (Top)
    dummy.position.set(anchor.x, anchor.y, anchor.z);
    dummy.rotation.set(anchor.pitch, anchor.yaw, 0, 'YXZ');
    dummy.translateY(isSphere ? 0 : 0.15);
    if (isSphere) dummy.rotateZ(Math.PI);
    dummy.scale.set(scale, scale, scale);
    dummy.updateMatrix();
    refAN.current.setMatrixAt(selectedIdx, dummy.matrix);
    refAN.current.instanceMatrix.needsUpdate = true;
    
    // Animate PL half (Bottom)
    dummy.position.set(anchor.x, anchor.y, anchor.z);
    dummy.rotation.set(anchor.pitch, anchor.yaw, 0, 'YXZ');
    dummy.translateY(isSphere ? 0 : -0.15);
    dummy.scale.set(scale, scale, scale);
    dummy.updateMatrix();
    refPL.current.setMatrixAt(selectedIdx, dummy.matrix);
    refPL.current.instanceMatrix.needsUpdate = true;
  });
"""
code = re.sub(frame_pattern, new_frame, code, flags=re.DOTALL)

code = code.replace("""  const handlePointerOver = (e: any) => {
    e.stopPropagation();
    if (e.instanceId !== undefined) {
      setHoveredIdx(e.instanceId);
    }
  };""", """  const handlePointerOver = (anchorsList: Anchor[]) => (e: any) => {
    e.stopPropagation();
    if (e.instanceId !== undefined) {
      setHoveredAnchorId(anchorsList[e.instanceId].id);
    }
  };""")

jsx_pattern = r'    <>\n      <instancedMesh.*?/>\n      \n      \{\/\* Tooltip'
new_jsx = """    <>
      {/* Regular Cubes */}
      <instancedMesh
        ref={meshRefPL}
        args={[halfGeometry, plateMaterial, regularAnchors.length]}
        onPointerOver={handlePointerOver(regularAnchors)}
        onPointerOut={handlePointerOut}
        onClick={(e) => { e.stopPropagation(); if (e.instanceId !== undefined) onSelectAnchor(selectedAnchorId === regularAnchors[e.instanceId].id ? null : regularAnchors[e.instanceId]); }}
      />
      <instancedMesh
        ref={meshRefAN}
        args={[halfGeometry, plateMaterial, regularAnchors.length]}
        onPointerOver={handlePointerOver(regularAnchors)}
        onPointerOut={handlePointerOut}
        onClick={(e) => { e.stopPropagation(); if (e.instanceId !== undefined) onSelectAnchor(selectedAnchorId === regularAnchors[e.instanceId].id ? null : regularAnchors[e.instanceId]); }}
      />
      
      {/* Middle Spheres */}
      <instancedMesh
        ref={meshRefSpherePL}
        args={[halfSphereGeometry, plateMaterial, middleAnchors.length]}
        onPointerOver={handlePointerOver(middleAnchors)}
        onPointerOut={handlePointerOut}
        onClick={(e) => { e.stopPropagation(); if (e.instanceId !== undefined) onSelectAnchor(selectedAnchorId === middleAnchors[e.instanceId].id ? null : middleAnchors[e.instanceId]); }}
      />
      <instancedMesh
        ref={meshRefSphereAN}
        args={[halfSphereGeometry, plateMaterial, middleAnchors.length]}
        onPointerOver={handlePointerOver(middleAnchors)}
        onPointerOut={handlePointerOut}
        onClick={(e) => { e.stopPropagation(); if (e.instanceId !== undefined) onSelectAnchor(selectedAnchorId === middleAnchors[e.instanceId].id ? null : middleAnchors[e.instanceId]); }}
      />
      
      {/* 3D Verification Lines to Pillars for hovered/selected Middle Anchors */}
      {middleAnchors.map(a => {
        if (!a.pillarAPoint || !a.pillarBPoint) return null;
        if (a.id !== selectedAnchorId && a.id !== hoveredAnchorId) return null;
        return (
          <group key={`lines-${a.id}`}>
            <Line points={[[a.x, a.y, a.z], a.pillarAPoint]} color="#ea580c" lineWidth={2} dashed={true} dashSize={0.5} gapSize={0.2} opacity={0.6} transparent />
            <Line points={[[a.x, a.y, a.z], a.pillarBPoint]} color="#ea580c" lineWidth={2} dashed={true} dashSize={0.5} gapSize={0.2} opacity={0.6} transparent />
          </group>
        )
      })}
      
      {/* Tooltip"""

code = re.sub(jsx_pattern, new_jsx, code, flags=re.DOTALL)

with open('web/src/components/AnchorVisualizer.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

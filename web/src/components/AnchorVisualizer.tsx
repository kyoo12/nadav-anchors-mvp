import { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Html } from '@react-three/drei';
import { motion, AnimatePresence } from 'framer-motion';

export interface Anchor {
  id: string;
  floor: number;
  x: number;
  y: number;
  z: number;
  pitch: number;
  yaw: number;
  metadata?: string;
  distanceToConcrete?: number;
  distanceToFloatingFloor?: number;
}

// Pre-allocate colors to prevent memory leaks during rapid hovering
const COLOR_EMERALD = new THREE.Color('#10b981');
const COLOR_YELLOW = new THREE.Color('#eab308');
const COLOR_ORANGE = new THREE.Color('#f97316');
const COLOR_RED = new THREE.Color('#ef4444');
const COLOR_PURPLE = new THREE.Color('#8b5cf6');
const COLOR_BLUE = new THREE.Color('#3b82f6');
const COLOR_WHITE = new THREE.Color('#ffffff');
const COLOR_CYAN = new THREE.Color('#06b6d4');

// Helper to get color based on PL type
const getPlColor = (plName: string) => {
  const meta = plName.toUpperCase();
  if (meta.includes('PL70')) return COLOR_EMERALD;
  if (meta.includes('PL90')) return COLOR_YELLOW;
  if (meta.includes('PL110') || meta.includes('ELYON 1')) return COLOR_ORANGE;
  if (meta.includes('150')) return COLOR_RED;
  if (meta.includes('200')) return COLOR_PURPLE;
  return COLOR_BLUE;
};

// Helper to get color based on AN type
const getAnColor = (anName: string) => {
  const meta = anName.toUpperCase();
  if (meta.includes('AN70')) return COLOR_EMERALD;
  if (meta.includes('AN120')) return COLOR_YELLOW;
  if (meta.includes('AN150')) return COLOR_ORANGE;
  if (meta.includes('AN200')) return COLOR_RED;
  return COLOR_BLUE;
};

interface Props {
  anchors: Anchor[];
  visibleFloors: Set<number>;
  onSelectAnchor: (anchor: Anchor | null) => void;
  selectedAnchorId: string | null;
}

const halfGeometry = new THREE.BoxGeometry(0.6, 0.3, 0.15);
const plateMaterial = new THREE.MeshStandardMaterial({ 
  color: '#ffffff', // Base color white so instance colors map perfectly
  metalness: 0.5,
  roughness: 0.4
});

// Pre-allocate a single dummy object to prevent GC stuttering in loops
const dummy = new THREE.Object3D();

export default function AnchorVisualizer({ anchors, visibleFloors, onSelectAnchor, selectedAnchorId }: Props) {
  const meshRefPL = useRef<THREE.InstancedMesh>(null);
  const meshRefAN = useRef<THREE.InstancedMesh>(null);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  // Filter anchors based on visible floors
  const visibleAnchors = useMemo(() => {
    return anchors.filter(a => visibleFloors.has(a.floor));
  }, [anchors, visibleFloors]);

  // (Rail lines removed to declutter view)

  // Setup initial matrices and base colors
  useEffect(() => {
    if (!meshRefPL.current || !meshRefAN.current) return;
    
    visibleAnchors.forEach((anchor, i) => {
      const isSelected = anchor.id === selectedAnchorId;
      const isHovered = hoveredIdx === i;
      const s = isSelected ? 1.15 : (isHovered ? 1.2 : 1.0);
      
      const metaParts = (anchor.metadata || '').split('|');
      const anName = metaParts[0]?.trim() || '';
      const plName = metaParts[1]?.trim() || '';
      
      // --- AN MESH (Top Half) ---
      dummy.position.set(anchor.x, anchor.y, anchor.z);
      dummy.rotation.set(anchor.pitch, anchor.yaw, 0, 'YXZ');
      dummy.translateY(0.15); // Move UP
      dummy.scale.set(s, s, s);
      dummy.updateMatrix();
      meshRefAN.current!.setMatrixAt(i, dummy.matrix);
      
      if (isSelected) meshRefAN.current!.setColorAt(i, COLOR_WHITE);
      else if (isHovered) meshRefAN.current!.setColorAt(i, COLOR_CYAN);
      else meshRefAN.current!.setColorAt(i, getAnColor(anName));
      
      // --- PL MESH (Bottom Half) ---
      dummy.position.set(anchor.x, anchor.y, anchor.z);
      dummy.rotation.set(anchor.pitch, anchor.yaw, 0, 'YXZ');
      dummy.translateY(-0.15); // Move DOWN
      dummy.scale.set(s, s, s);
      dummy.updateMatrix();
      meshRefPL.current!.setMatrixAt(i, dummy.matrix);
      
      if (isSelected) meshRefPL.current!.setColorAt(i, COLOR_WHITE);
      else if (isHovered) meshRefPL.current!.setColorAt(i, COLOR_CYAN);
      else meshRefPL.current!.setColorAt(i, getPlColor(plName));
    });
    
    meshRefAN.current.instanceMatrix.needsUpdate = true;
    if (meshRefAN.current.instanceColor) {
      meshRefAN.current.instanceColor.needsUpdate = true;
    }
    
    meshRefPL.current.instanceMatrix.needsUpdate = true;
    if (meshRefPL.current.instanceColor) {
      meshRefPL.current.instanceColor.needsUpdate = true;
    }

    // CRITICAL: Compute bounding spheres so raycasting doesn't fail when the camera zooms in
    meshRefAN.current.computeBoundingSphere();
    meshRefPL.current.computeBoundingSphere();
  }, [visibleAnchors, hoveredIdx, selectedAnchorId]);

  // Only run the pulsing animation in useFrame for the selected anchor
  useFrame(() => {
    if (!meshRefPL.current || !meshRefAN.current || !selectedAnchorId) return;
    
    // Find index of selected anchor
    const selectedIdx = visibleAnchors.findIndex(a => a.id === selectedAnchorId);
    if (selectedIdx === -1) return;

    const anchor = visibleAnchors[selectedIdx];
    
    const time = Date.now() / 1000;
    const scale = 1.0 + Math.sin(time * 5) * 0.15;
    
    // Animate AN half (Top)
    dummy.position.set(anchor.x, anchor.y, anchor.z);
    dummy.rotation.set(anchor.pitch, anchor.yaw, 0, 'YXZ');
    dummy.translateY(0.15);
    dummy.scale.set(scale, scale, scale);
    dummy.updateMatrix();
    meshRefAN.current.setMatrixAt(selectedIdx, dummy.matrix);
    meshRefAN.current.instanceMatrix.needsUpdate = true;
    
    // Animate PL half (Bottom)
    dummy.position.set(anchor.x, anchor.y, anchor.z);
    dummy.rotation.set(anchor.pitch, anchor.yaw, 0, 'YXZ');
    dummy.translateY(-0.15);
    dummy.scale.set(scale, scale, scale);
    dummy.updateMatrix();
    meshRefPL.current.setMatrixAt(selectedIdx, dummy.matrix);
    meshRefPL.current.instanceMatrix.needsUpdate = true;
  });

  const handlePointerOver = (e: any) => {
    e.stopPropagation();
    if (e.instanceId !== undefined) {
      setHoveredIdx(e.instanceId);
    }
  };

  const handlePointerOut = () => {
    setHoveredIdx(null);
  };

  const hoveredAnchor = hoveredIdx !== null ? visibleAnchors[hoveredIdx] : null;
  const hoveredMetaParts = (hoveredAnchor?.metadata || '').split('|');
  const hoveredAnName = hoveredMetaParts[0]?.trim() || 'Unknown';
  const hoveredPlName = hoveredMetaParts[1]?.trim() || 'Unknown';

  return (
    <>
      <instancedMesh
        ref={meshRefPL}
        args={[halfGeometry, plateMaterial, visibleAnchors.length]}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
        onClick={(e) => {
          e.stopPropagation();
          if (e.instanceId !== undefined) {
            const clickedAnchor = visibleAnchors[e.instanceId];
            onSelectAnchor(selectedAnchorId === clickedAnchor.id ? null : clickedAnchor);
          }
        }}
      />
      <instancedMesh
        ref={meshRefAN}
        args={[halfGeometry, plateMaterial, visibleAnchors.length]}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
        onClick={(e) => {
          e.stopPropagation();
          if (e.instanceId !== undefined) {
            const clickedAnchor = visibleAnchors[e.instanceId];
            onSelectAnchor(selectedAnchorId === clickedAnchor.id ? null : clickedAnchor);
          }
        }}
      />
      
      {/* Tooltip anchored to the 3D position */}
      {hoveredAnchor && (
        <Html position={[hoveredAnchor.x, hoveredAnchor.y, hoveredAnchor.z]} zIndexRange={[100, 0]} style={{ pointerEvents: 'none' }}>
          <AnimatePresence>
            <motion.div 
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className="tooltip-container"
              style={{ pointerEvents: 'none' }}
            >
              <div 
                className="glass-panel tooltip" 
                style={{ borderTop: `4px solid #${getAnColor(hoveredAnName).getHexString()}` }}
              >
                <div className="tooltip-header">
                  <span>{hoveredAnchor.id}</span>
                  <span className="tooltip-badge">{hoveredAnchor.floor === 8 ? 'Roof' : `Floor ${hoveredAnchor.floor}`}</span>
                </div>
                
                <div className="tooltip-row" style={{ marginBottom: '8px' }}>
                  <span className="tooltip-label">AN Block:</span>
                  <span className="tooltip-value" style={{ 
                    color: '#' + getAnColor(hoveredAnName).getHexString(), 
                    fontWeight: 'bold' 
                  }}>
                    {hoveredAnName}
                  </span>
                </div>
                <div className="tooltip-row" style={{ marginBottom: '12px' }}>
                  <span className="tooltip-label">PL Block:</span>
                  <span className="tooltip-value" style={{ 
                    color: '#' + getPlColor(hoveredPlName).getHexString(),
                    fontWeight: 'bold'
                  }}>
                    {hoveredPlName}
                  </span>
                </div>
                
                <div className="tooltip-row" style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                  <span className="tooltip-label">Click for Details</span>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </Html>
      )}
    </>
  );
}

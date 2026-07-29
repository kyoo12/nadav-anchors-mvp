import { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Html, Line } from '@react-three/drei';
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
  isMiddleAnchor?: boolean;
  pillarADistance?: number;
  pillarBDistance?: number;
  pillarAPath?: [number, number, number][];
  pillarBPath?: [number, number, number][];
  pillarALabel?: string;
  pillarBLabel?: string;
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
const halfSphereGeometry = new THREE.SphereGeometry(0.4, 32, 16, 0, Math.PI);
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
  const meshRefSpherePL = useRef<THREE.InstancedMesh>(null);
  const meshRefSphereAN = useRef<THREE.InstancedMesh>(null);
  const [hoveredAnchorId, setHoveredAnchorId] = useState<string | null>(null);

  // Filter anchors based on visible floors
  const visibleAnchors = useMemo(() => {
    return anchors.filter(a => visibleFloors.has(a.floor));
  }, [anchors, visibleFloors]);

  const regularAnchors = useMemo(() => visibleAnchors.filter(a => !a.isMiddleAnchor), [visibleAnchors]);
  const middleAnchors = useMemo(() => visibleAnchors.filter(a => a.isMiddleAnchor), [visibleAnchors]);


  // (Rail lines removed to declutter view)

  // Setup initial matrices and base colors
  useEffect(() => {
    if (!meshRefPL.current || !meshRefAN.current || !meshRefSpherePL.current || !meshRefSphereAN.current) return;
    
    const applyMatrices = (
      anchorsList: Anchor[],
      refAN: any,
      refPL: any,
      isSphere: boolean
    ) => {
      anchorsList.forEach((anchor: Anchor, i: number) => {
        const isSelected = anchor.id === selectedAnchorId;
        const isHovered = anchor.id === hoveredAnchorId;
        const s = isSelected ? (isSphere ? 1.7 : 1.15) : (isHovered ? (isSphere ? 1.8 : 1.2) : (isSphere ? 1.5 : 1.0));
        
        const metaParts = (anchor.metadata || '').split('|');
        const anName = metaParts[0]?.trim() || '';
        const plName = metaParts[1]?.trim() || '';
        
        // --- AN MESH (Top Half) ---
        dummy.position.set(anchor.x, anchor.y, anchor.z);
        dummy.rotation.set(anchor.pitch, anchor.yaw, 0, 'YXZ');
        dummy.translateY(isSphere ? 0 : 0.15); // Spheres stay at center, just rotated
        if (isSphere) dummy.rotateZ(Math.PI); // Top hemisphere
        dummy.scale.set(s, s, s);
        dummy.updateMatrix();
        refAN.current!.setMatrixAt(i, dummy.matrix);
        
        if (isSelected) refAN.current!.setColorAt(i, COLOR_WHITE);
        else if (isHovered) refAN.current!.setColorAt(i, COLOR_CYAN);
        else refAN.current!.setColorAt(i, getAnColor(anName)); // e.g. Blue
        
        // --- PL MESH (Bottom Half) ---
        dummy.position.set(anchor.x, anchor.y, anchor.z);
        dummy.rotation.set(anchor.pitch, anchor.yaw, 0, 'YXZ');
        dummy.translateY(isSphere ? 0 : -0.15); 
        dummy.scale.set(s, s, s);
        dummy.updateMatrix();
        refPL.current!.setMatrixAt(i, dummy.matrix);
        
        if (isSelected) refPL.current!.setColorAt(i, COLOR_WHITE);
        else if (isHovered) refPL.current!.setColorAt(i, COLOR_CYAN);
        else refPL.current!.setColorAt(i, getPlColor(plName)); // e.g. Orange
      });
      
      refAN.current!.instanceMatrix.needsUpdate = true;
      if (refAN.current!.instanceColor) refAN.current!.instanceColor.needsUpdate = true;
      refPL.current!.instanceMatrix.needsUpdate = true;
      if (refPL.current!.instanceColor) refPL.current!.instanceColor.needsUpdate = true;
      refAN.current!.computeBoundingSphere();
      refPL.current!.computeBoundingSphere();
    };

    applyMatrices(regularAnchors, meshRefAN, meshRefPL, false);
    applyMatrices(middleAnchors, meshRefSphereAN, meshRefSpherePL, true);

  }, [regularAnchors, middleAnchors, hoveredAnchorId, selectedAnchorId]);

  // Only run the pulsing animation in useFrame for the selected anchor
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
    refAN.current!.setMatrixAt(selectedIdx, dummy.matrix);
    refAN.current!.instanceMatrix.needsUpdate = true;
    
    // Animate PL half (Bottom)
    dummy.position.set(anchor.x, anchor.y, anchor.z);
    dummy.rotation.set(anchor.pitch, anchor.yaw, 0, 'YXZ');
    dummy.translateY(isSphere ? 0 : -0.15);
    dummy.scale.set(scale, scale, scale);
    dummy.updateMatrix();
    refPL.current!.setMatrixAt(selectedIdx, dummy.matrix);
    refPL.current!.instanceMatrix.needsUpdate = true;
  });

  const handlePointerOver = (anchorsList: Anchor[]) => (e: any) => {
    e.stopPropagation();
    if (e.instanceId !== undefined) {
      setHoveredAnchorId(anchorsList[e.instanceId].id);
    }
  };

  const handlePointerOut = () => {
    setHoveredAnchorId(null);
  };

  const hoveredAnchor = hoveredAnchorId ? visibleAnchors.find(a => a.id === hoveredAnchorId) : null;
  const hoveredMetaParts = (hoveredAnchor?.metadata || '').split('|');
  const hoveredAnName = hoveredMetaParts[0]?.trim() || 'Unknown';
  const hoveredPlName = hoveredMetaParts[1]?.trim() || 'Unknown';

  return (
    <>
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
        if (!a.pillarAPath || !a.pillarBPath) return null;
        if (a.id !== selectedAnchorId && a.id !== hoveredAnchorId) return null;
        return (
          <group key={`lines-${a.id}`}>
            <Line points={a.pillarAPath} color="#10b981" lineWidth={3} dashed={false} opacity={0.8} transparent />
            <Line points={a.pillarBPath} color="#3b82f6" lineWidth={3} dashed={false} opacity={0.8} transparent />
          </group>
        )
      })}
      
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

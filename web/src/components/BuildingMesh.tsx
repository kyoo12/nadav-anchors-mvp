import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';
import { useMemo } from 'react';

export default function BuildingMesh() {
  const { scene } = useGLTF('/concrete-draco.glb');

  // Apply a premium glassmorphic/wireframe look to the building
  useMemo(() => {
    scene.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.raycast = () => null;
        child.material = new THREE.MeshPhysicalMaterial({
          color: '#1e293b',
          metalness: 0.1,
          roughness: 0.8,
          transparent: true,
          opacity: 0.4,
          side: THREE.DoubleSide,
        });
      }
    });
  }, [scene]);

  return <primitive object={scene} position={[0, 0, 0]} raycast={() => null} />;
}

useGLTF.preload('/concrete-draco.glb');

import { useLoader } from '@react-three/fiber';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import * as THREE from 'three';
import { useMemo } from 'react';

export default function FloatingFloorMesh() {
  const obj = useLoader(OBJLoader, '/floating_floor.obj');

  const clonedObj = useMemo(() => {
    const clone = obj.clone();
    clone.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.raycast = () => null;
        child.material = new THREE.MeshPhysicalMaterial({
          color: '#94a3b8', 
          metalness: 0.1,
          roughness: 0.8,
          transparent: true,
          opacity: 0.5,
          depthWrite: false,
          side: THREE.DoubleSide,
          wireframe: false, 
        });
      }
    });
    return clone;
  }, [obj]);

  return <primitive object={clonedObj} position={[0, 0, 0]} />;
}

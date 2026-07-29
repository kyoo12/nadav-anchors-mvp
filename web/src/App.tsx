import { useState, useEffect, useRef } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Environment, Grid } from '@react-three/drei'
import AnchorVisualizer, { type Anchor } from './components/AnchorVisualizer'
import { motion } from 'framer-motion'
import RightSidebar from './components/RightSidebar'
import LoadingScreen from './components/LoadingScreen'
import BuildingMesh from './components/BuildingMesh'
import { Suspense } from 'react'
import { useQuery } from '@tanstack/react-query'
import * as THREE from 'three'

// CameraController smoothly flies the camera and orbit controls to the selected anchor
function CameraController({ selectedAnchor }: { selectedAnchor: Anchor | null }) {
  const { controls } = useThree();
  const targetRef = useRef<THREE.Vector3 | null>(null);
  
  useEffect(() => {
    if (selectedAnchor) {
      targetRef.current = new THREE.Vector3(selectedAnchor.x, selectedAnchor.y, selectedAnchor.z);
    }
  }, [selectedAnchor]);

  useFrame(() => {
    if (targetRef.current && controls) {
      const currentTarget = (controls as any).target as THREE.Vector3;
      if (currentTarget.distanceTo(targetRef.current) > 0.5) {
        currentTarget.lerp(targetRef.current, 0.05);
        (controls as any).update();
      } else {
        targetRef.current = null; // stop moving once close so user can manually orbit
      }
    }
  });
  return null;
}

const formatFloor = (f: number) => f === 8 ? 'Roof' : `Floor ${f}`;

function App() {
  const [visibleFloors, setVisibleFloors] = useState<Set<number>>(new Set());
  const [showRegularAnchors, setShowRegularAnchors] = useState(true);
  const [floors, setFloors] = useState<number[]>([]);
  const [selectedAnchor, setSelectedAnchor] = useState<Anchor | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: anchors = [], isLoading, isError } = useQuery({
    queryKey: ['anchors'],
    queryFn: async () => {
      const res = await fetch(`/true_anchors.json?t=${Date.now()}`);
      if (!res.ok) throw new Error('Failed to fetch anchors');
      return res.json() as Promise<Anchor[]>;
    }
  });

  // Setup floors when data arrives
  useEffect(() => {
    if (anchors.length > 0) {
      const uniqueFloors = Array.from(new Set(anchors.map((a: Anchor) => a.floor))).sort((a, b) => a - b);
      setFloors(uniqueFloors);
      // Default to all floors if none are set
      setVisibleFloors(prev => prev.size === 0 ? new Set(uniqueFloors) : prev);
    }
  }, [anchors]);



  const toggleFloor = (floor: number) => {
    setVisibleFloors(prev => {
      const next = new Set(prev);
      if (next.has(floor)) {
        next.delete(floor);
      } else {
        next.add(floor);
      }
      return next;
    });
  };

  const toggleAll = () => {
    if (visibleFloors.size === floors.length) {
      setVisibleFloors(new Set());
    } else {
      setVisibleFloors(new Set(floors));
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;
    const found = anchors.find(a => a.id.toLowerCase() === searchQuery.toLowerCase());
    if (found) {
      setSelectedAnchor(found);
      // Ensure the floor is visible
      setVisibleFloors(prev => new Set(prev).add(found.floor));
      setSearchQuery('');
    } else {
      alert(`Anchor ${searchQuery} not found!`);
    }
  };

  return (
    <>
      <motion.div 
        className="sidebar glass-panel"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <img src="/logo.png" alt="Logo" style={{ height: '40px', objectFit: 'contain' }} />
          <h1 style={{ margin: 0 }}>Building Anchors</h1>
        </div>
        <p>Interactive 3D visualizer. Toggle floors below and click on an anchor for details.</p>
        
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
          <input 
            type="text" 
            placeholder="Search ID (e.g. F3_12)" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ 
              flex: 1, padding: '8px 12px', borderRadius: '4px', 
              border: '1px solid var(--border-glass)', background: '#f8fafc', color: 'var(--text-main)' 
            }} 
          />
          <button type="submit" style={{ padding: '8px 16px', borderRadius: '4px', background: 'var(--accent-blue)', color: 'white', border: 'none', cursor: 'pointer' }}>
            Find
          </button>
        </form>

        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Showing {anchors.filter(a => visibleFloors.has(a.floor)).length} / {anchors.length}
          </span>
          <button 
            onClick={toggleAll}
            style={{
              background: 'none', border: 'none', color: 'var(--accent-blue)', 
              cursor: 'pointer', fontSize: '0.9rem'
            }}
          >
            {visibleFloors.size === floors.length ? 'Hide All' : 'Show All'}
          </button>
        </div>
        
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '0.9rem', cursor: 'pointer', color: 'var(--text-main)' }}>
          <input type="checkbox" checked={showRegularAnchors} onChange={(e) => setShowRegularAnchors(e.target.checked)} />
          Show Square Anchors
        </label>

        <div className="floor-toggles">
          {floors.map(floor => {
            const count = anchors.filter(a => a.floor === floor).length;
            const isActive = visibleFloors.has(floor);
            return (
              <div 
                key={floor} 
                className={`floor-toggle ${isActive ? 'active' : ''}`}
                onClick={() => toggleFloor(floor)}
              >
                <span className="toggle-label">{formatFloor(floor)}</span>
                <span className="toggle-count">{count}</span>
              </div>
            );
          })}
        </div>
      </motion.div>

      <RightSidebar 
        selectedAnchor={selectedAnchor} 
        allAnchors={anchors} 
        onClose={() => setSelectedAnchor(null)} 
      />

      <Canvas camera={{ position: [0, 40, 60], fov: 45 }}>
        <color attach="background" args={['#f1f5f9']} />
        
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 20, 10]} intensity={1} />
        <Environment preset="city" />

        <Grid 
          raycast={() => null}
          position={[0, -0.1, 0]} 
          args={[200, 200]} 
          cellSize={1} 
          cellThickness={1} 
          cellColor="#cbd5e1" 
          sectionSize={10} 
          sectionThickness={1.5} 
          sectionColor="#94a3b8" 
          fadeDistance={100} 
          fadeStrength={1} 
        />

        <Suspense fallback={<LoadingScreen />}>
          <BuildingMesh />
          {anchors.length > 0 && !isLoading && !isError && (
            <AnchorVisualizer 
              anchors={anchors} 
              visibleFloors={visibleFloors} 
              onSelectAnchor={setSelectedAnchor}
              selectedAnchorId={selectedAnchor?.id || null}
              showRegularAnchors={showRegularAnchors}
            />
          )}
        </Suspense>

        <CameraController selectedAnchor={selectedAnchor} />
        
        <OrbitControls 
          makeDefault 
          minDistance={2} 
          maxDistance={150} 
          maxPolarAngle={Math.PI / 2 + 0.1} // Prevent going under the ground completely, but allow slight undersight
          target={[0, 15, 0]} 
        />
      </Canvas>
    </>
  )
}

export default App

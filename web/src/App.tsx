/**
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
import { useState, useEffect, useRef } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Environment, Grid } from '@react-three/drei'
import AnchorVisualizer, { type Anchor } from './components/AnchorVisualizer'
import { motion } from 'framer-motion'
import RightSidebar from './components/RightSidebar'
import LoadingScreen from './components/LoadingScreen'
import BuildingMesh from './components/BuildingMesh'
import FloatingFloorMesh from './components/FloatingFloorMesh'
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
  useEffect(() => {
    const link = document.createElement('link');
    link.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Roboto+Mono:wght@400;500;600;700&display=swap';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
    return () => { document.head.removeChild(link); }
  }, []);

  
  const [theme, setTheme] = useState<'midnight' | 'field'>('midnight');
  const [isLeftCollapsed, setIsLeftCollapsed] = useState(false);
  const [visibleFloors, setVisibleFloors] = useState<Set<number>>(new Set());
  
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);
  const [showRegularAnchors, setShowRegularAnchors] = useState(true);
  const [visibleBrackets, setVisibleBrackets] = useState<Set<string>>(new Set());
  const [allBracketTypes, setAllBracketTypes] = useState<string[]>([]);

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

      // Extract unique bracket types
      const uniqueBrackets = new Set<string>();
      anchors.forEach((a: Anchor) => {
        const parts = (a.metadata || '').split('|');
        if (parts[0]) {
          const typeName = parts[0].trim();
          if (typeName) uniqueBrackets.add(typeName);
        }
      });
      const bracketArray = Array.from(uniqueBrackets).sort();
      setAllBracketTypes(bracketArray);
      setVisibleBrackets(prev => prev.size === 0 ? new Set(bracketArray) : prev);

    }
  }, [anchors]);



  
  const toggleBracket = (b: string) => {
    setVisibleBrackets(prev => {
      const next = new Set(prev);
      if (next.has(b)) next.delete(b);
      else next.add(b);
      return next;
    });
  };

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

  const exportCSV = () => {
    const visibleAnchors = anchors.filter(a => {
      const parts = (a.metadata || '').split('|');
      const typeName = parts[0]?.trim() || '';
      return visibleFloors.has(a.floor) && visibleBrackets.has(typeName);
    });
    const header = "PointID,X,Y,Z,Floor,Type,NearestGridX,OffsetX,NearestGridY,OffsetY,WallGap\\n";
    const rows = visibleAnchors.map(a => 
      `${a.id},${a.x.toFixed(3)},${a.y.toFixed(3)},${a.z.toFixed(3)},${a.floor},${a.metadata},${a.nearestGridX},${(a.offsetX || 0).toFixed(1)},${a.nearestGridY},${(a.offsetY || 0).toFixed(1)},${(a.distanceToConcrete || 0).toFixed(1)}`
    ).join("\\n");
    
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'nadav_anchors_export.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
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
        className="sidebar-container"
        initial={{ x: -400, opacity: 0 }}
        animate={{ x: isLeftCollapsed ? '-110%' : 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <button 
          onClick={() => setIsLeftCollapsed(!isLeftCollapsed)}
          style={{
            position: 'absolute',
            right: '-60px',
            top: '0',
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: 'var(--bg-panel)',
            border: '1px solid var(--border-glass)',
            color: 'var(--text-main)',
            cursor: 'pointer',
            zIndex: 20,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.2rem',
            fontWeight: 'bold',
            pointerEvents: 'auto',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
          }}
        >
          {isLeftCollapsed ? '>>' : '<<'}
        </button>
        
        {/* Module A: Header & Actions */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h1 style={{ fontSize: '2rem', margin: 0, fontWeight: 800 }}>Nadav Anchors</h1>
              <p style={{ margin: 0, color: 'var(--text-muted)' }}>Total Anchors: {anchors.length}</p>
            </div>
            <button 
              onClick={() => setTheme(t => t === 'midnight' ? 'field' : 'midnight')}
              style={{ padding: '12px 16px', borderRadius: '12px', background: 'var(--bg-dark)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', cursor: 'pointer', fontWeight: 600, minHeight: '56px' }}
            >
              {theme === 'midnight' ? '?? Field Mode' : '?? Dark Mode'}
            </button>
          </div>
          
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px' }}>
            <input 
              type="text" 
              placeholder="Search ID (e.g. 104)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ flex: 1, padding: '0 16px', borderRadius: '12px', border: '1px solid var(--border-glass)', background: 'var(--bg-dark)', color: 'var(--text-main)', fontSize: '1rem', outline: 'none', minHeight: '56px' }}
            />
            <button type="submit" style={{ padding: '0 24px', background: 'var(--accent-blue)', color: '#fff', border: 'none', borderRadius: '12px', cursor: 'pointer', fontWeight: 600, fontSize: '1rem', minHeight: '56px' }}>
              Find
            </button>
          </form>

          <button 
            onClick={exportCSV}
            style={{ 
              padding: '0 16px', 
              background: 'transparent', 
              border: '2px solid var(--accent-cyan)',
              color: 'var(--accent-cyan)',
              borderRadius: '12px',
              fontSize: '1rem',
              fontWeight: 700,
              cursor: 'pointer',
              minHeight: '56px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            ?? Export Visible CSV
          </button>
        </div>

        <div className="bento-scroll">
          {/* Module B: Floor Filters */}
          <div className="glass-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>Floors</h2>
              <button 
                onClick={toggleAll}
                style={{ background: 'transparent', color: 'var(--accent-blue)', border: 'none', cursor: 'pointer', fontSize: '1rem', fontWeight: 600, minHeight: '48px', padding: '0 12px' }}
              >
                {visibleFloors.size === floors.length ? 'Hide All' : 'Show All'}
              </button>
            </div>
            <div className="floor-toggles">
              {floors.map(floor => {
                const count = anchors.filter(a => a.floor === floor).length;
                const isActive = visibleFloors.has(floor);
                return (
                  <div 
                    key={floor} 
                    className={`floor-toggle ${isActive ? 'active' : ''}`}
                    onClick={() => toggleFloor(floor)}
                    style={{ minHeight: '56px' }}
                  >
                    <span className="toggle-label">{formatFloor(floor)}</span>
                    <span className="toggle-count">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Module C: Bracket Filters */}
          <div className="glass-panel">
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', margin: 0, marginBottom: '16px' }}>Bracket Types</h2>
            <div className="floor-toggles">
              {allBracketTypes.map(b => (
                <div 
                  key={b} 
                  className={`floor-toggle ${visibleBrackets.has(b) ? 'active' : ''}`}
                  onClick={() => toggleBracket(b)}
                  style={{ minHeight: '56px' }}
                >
                  <span className="toggle-label">{b}</span>
                  <span className="toggle-count"></span>
                </div>
              ))}
            </div>
          </div>

          {/* Module D: Global Settings */}
          <div className="glass-panel">
            <label style={{ display: 'flex', alignItems: 'center', gap: '16px', cursor: 'pointer', minHeight: '56px', margin: 0, color: 'var(--text-main)' }}>
              <input 
                type="checkbox" 
                checked={showRegularAnchors}
                onChange={(e) => setShowRegularAnchors(e.target.checked)}
                style={{ width: '24px', height: '24px', cursor: 'pointer' }}
              />
              <span style={{ fontSize: '1rem', fontWeight: 500 }}>Show Regular Square Anchors</span>
            </label>
          </div>
        </div>

      </motion.div>

      <RightSidebar 
        selectedAnchor={selectedAnchor} 
        allAnchors={anchors} 
        onClose={() => setSelectedAnchor(null)} 
      />

      <Canvas camera={{ position: [0, 40, 60], fov: 45 }}>
        <color attach="background" args={[theme === 'field' ? '#f1f5f9' : '#020617']} />
        
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
          <FloatingFloorMesh />
          {anchors.length > 0 && !isLoading && !isError && (
            <AnchorVisualizer 
              anchors={anchors} 
              visibleFloors={visibleFloors} 
              onSelectAnchor={setSelectedAnchor}
              selectedAnchorId={selectedAnchor?.id || null}
              showRegularAnchors={showRegularAnchors}
          visibleBrackets={visibleBrackets}
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

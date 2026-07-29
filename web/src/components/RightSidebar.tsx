import { useMemo } from 'react';
import type { Anchor } from './AnchorVisualizer';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  selectedAnchor: Anchor | null;
  allAnchors: Anchor[];
  onClose: () => void;
}

export default function RightSidebar({ selectedAnchor, allAnchors, onClose }: Props) {
  const details = useMemo(() => {
    if (!selectedAnchor) return null;

    const floorAnchors = allAnchors.filter(a => a.floor === selectedAnchor.floor && a.id !== selectedAnchor.id);
    const floorAboveAnchors = allAnchors.filter(a => a.floor === selectedAnchor.floor + 1);
    const floorBelowAnchors = allAnchors.filter(a => a.floor === selectedAnchor.floor - 1);
    
    // Find the 2 closest horizontal anchors on the same floor
    const neighbors = floorAnchors.map(a => ({
      anchor: a,
      dist: Math.hypot(a.x - selectedAnchor.x, a.y - selectedAnchor.y, a.z - selectedAnchor.z)
    })).sort((a, b) => a.dist - b.dist);
    
    // Find closest anchor directly above (minimizing horizontal drift)
    const aboveNeighbors = floorAboveAnchors.map(a => ({
      anchor: a,
      dist: Math.hypot(a.x - selectedAnchor.x, a.z - selectedAnchor.z)
    })).sort((a, b) => a.dist - b.dist);

    // Find closest anchor directly below
    const belowNeighbors = floorBelowAnchors.map(a => ({
      anchor: a,
      dist: Math.hypot(a.x - selectedAnchor.x, a.z - selectedAnchor.z)
    })).sort((a, b) => a.dist - b.dist);
    
    const leftAnchor = neighbors.length > 0 ? neighbors[0].anchor : null;
    const rightAnchor = neighbors.length > 1 ? neighbors[1].anchor : null;
    const aboveAnchor = aboveNeighbors.length > 0 ? aboveNeighbors[0].anchor : null;
    const belowAnchor = belowNeighbors.length > 0 ? belowNeighbors[0].anchor : null;

    const getDist = (a: Anchor) => (Math.hypot(
      a.x - selectedAnchor.x,
      a.y - selectedAnchor.y,
      a.z - selectedAnchor.z
    ) * 1000).toFixed(0);

    const metaParts = (selectedAnchor.metadata || '').split('|');
    const anName = metaParts[0]?.trim() || 'Unknown';
    const plName = metaParts[1]?.trim() || 'Unknown';

    return {
      left: leftAnchor ? getDist(leftAnchor) : 'N/A',
      right: rightAnchor ? getDist(rightAnchor) : 'N/A',
      above: aboveAnchor ? getDist(aboveAnchor) : 'N/A',
      below: belowAnchor ? getDist(belowAnchor) : 'N/A',
      anName,
      plName
    };
  }, [selectedAnchor, allAnchors]);

  return (
    <AnimatePresence>
      {selectedAnchor && details && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2 }}
          className="sidebar right glass-panel"
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h1 style={{ margin: 0, fontSize: '1.25rem' }}>Anchor Details</h1>
            <button 
              onClick={onClose}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.2rem' }}
            >
              ×
            </button>
          </div>

          <div className="detail-section">
            <h2>Identity</h2>
            <div className="detail-item">
              <span className="detail-label">ID</span>
              <span className="detail-value">{selectedAnchor.id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Floor</span>
              <span className="detail-value">{selectedAnchor.floor === 8 ? 'Roof' : `Floor ${selectedAnchor.floor}`}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">AN Block</span>
              <span className="detail-value" style={{ color: 'var(--accent-cyan)' }}>{details.anName}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">PL Block</span>
              <span className="detail-value" style={{ color: 'var(--accent-cyan)' }}>{details.plName}</span>
            </div>
          </div>

          <div className="detail-section">
            <h2>Position & Orientation</h2>
            <div className="detail-item">
              <span className="detail-label">Distance to Concrete Floor (Z)</span>
              <span className="detail-value">
                {selectedAnchor.distanceToFloatingFloor !== undefined && selectedAnchor.distanceToFloatingFloor !== 0 ? 
                  `${selectedAnchor.distanceToFloatingFloor > 0 ? '+' : ''}${selectedAnchor.distanceToFloatingFloor.toFixed(1)} mm` 
                  : 'N/A'}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Pitch</span>
              <span className="detail-value">{(selectedAnchor.pitch * 180 / Math.PI).toFixed(1)}°</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Yaw</span>
              <span className="detail-value">{(selectedAnchor.yaw * 180 / Math.PI).toFixed(1)}°</span>
            </div>
          </div>

          <div className="detail-section">
            <h2>Clearances & Neighbors</h2>
            <div className="detail-item">
              <span className="detail-label">Distance to Left Neighbor</span>
              <span className="detail-value">{details.left} {details.left !== 'N/A' && 'mm'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Distance to Right Neighbor</span>
              <span className="detail-value">{details.right} {details.right !== 'N/A' && 'mm'}</span>
            </div>
            {selectedAnchor.isMiddleAnchor && (
              <>
                <div className="detail-item">
                  <span className="detail-label" style={{ color: 'var(--accent-orange)' }}>Distance to Pillar A</span>
                  <span className="detail-value">
                    {selectedAnchor.pillarADistance !== undefined ? `${selectedAnchor.pillarADistance.toFixed(1)} mm` : 'N/A'}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label" style={{ color: 'var(--accent-orange)' }}>Distance to Pillar B</span>
                  <span className="detail-value">
                    {selectedAnchor.pillarBDistance !== undefined ? `${selectedAnchor.pillarBDistance.toFixed(1)} mm` : 'N/A'}
                  </span>
                </div>
              </>
            )}
            <div className="detail-item">
              <span className="detail-label">Distance to Anchor Above</span>
              <span className="detail-value">{details.above} {details.above !== 'N/A' && 'mm'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Distance to Anchor Below</span>
              <span className="detail-value">{details.below} {details.below !== 'N/A' && 'mm'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Distance to Concrete</span>
              <span className="detail-value">
                {selectedAnchor.distanceToConcrete !== undefined ? `${selectedAnchor.distanceToConcrete.toFixed(1)} mm` : 'Pending'}
              </span>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

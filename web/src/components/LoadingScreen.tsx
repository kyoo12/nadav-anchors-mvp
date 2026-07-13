import { useProgress, Html } from '@react-three/drei';
import { motion } from 'framer-motion';

export default function LoadingScreen() {
  const { progress } = useProgress();

  return (
    <Html center zIndexRange={[1000, 0]}>
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0 }}
        className="glass-panel"
        style={{
          padding: '30px 40px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '16px',
          width: '300px',
          pointerEvents: 'none',
        }}
      >
        <h2 style={{ 
          fontSize: '1.25rem', 
          margin: 0,
          background: 'linear-gradient(to right, #3b82f6, #06b6d4)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>Loading Environment</h2>
        
        <div style={{
          width: '100%',
          height: '6px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '3px',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            width: `${progress}%`,
            background: 'linear-gradient(90deg, #3b82f6, #06b6d4)',
            transition: 'width 0.3s ease-out'
          }} />
        </div>
        
        <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          {progress.toFixed(0)}%
        </span>
      </motion.div>
    </Html>
  );
}

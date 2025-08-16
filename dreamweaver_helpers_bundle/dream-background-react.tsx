import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Main Dream Background Component
const DreamBackground = ({ 
  effect = 'aurora', 
  intensity = 0.8, 
  interactive = true,
  poetryEnabled = true,
  className = '' 
}) => {
  const [currentPoetry, setCurrentPoetry] = useState(0);
  const [particles, setParticles] = useState([]);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  
  // Poetry collection for dream states
  const poetryLines = [
    "Consciousness stirs in quantum waves of possibility",
    "Neural constellations map the geography of thought",
    "Dreams cascade through synaptic waterfalls",
    "Memory crystallizes in the amber of awareness",
    "The mind's eye opens to infinite horizons"
  ];

  // Generate particles on mount
  useEffect(() => {
    const particleArray = [];
    for (let i = 0; i < 50; i++) {
      particleArray.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 3 + 1,
        duration: Math.random() * 20 + 10,
        delay: Math.random() * 5
      });
    }
    setParticles(particleArray);
  }, []);

  // Rotate poetry
  useEffect(() => {
    if (!poetryEnabled) return;
    const interval = setInterval(() => {
      setCurrentPoetry((prev) => (prev + 1) % poetryLines.length);
    }, 8000);
    return () => clearInterval(interval);
  }, [poetryEnabled]);

  // Track mouse for interactive effects
  const handleMouseMove = (e) => {
    if (!interactive) return;
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: ((e.clientX - rect.left) / rect.width) * 100,
      y: ((e.clientY - rect.top) / rect.height) * 100
    });
  };

  return (
    <div 
      className={`dream-background-container ${className}`}
      onMouseMove={handleMouseMove}
      style={{
        position: 'absolute',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        pointerEvents: interactive ? 'auto' : 'none'
      }}
    >
      {/* Base gradient background */}
      <div className="base-gradient" style={{
        position: 'absolute',
        width: '100%',
        height: '100%',
        background: effect === 'aurora' 
          ? 'linear-gradient(to bottom, #000428 0%, #004e92 100%)'
          : effect === 'neural'
          ? 'linear-gradient(to bottom, #000011, #000033, #000044)'
          : effect === 'rem'
          ? 'radial-gradient(ellipse at center, #1e3c72 0%, #2a5298 50%, #0e1a34 100%)'
          : effect === 'dream'
          ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          : 'linear-gradient(180deg, #0a0e27 0%, #1a1f3a 50%, #2d1b69 100%)',
        opacity: intensity
      }} />

      {/* Aurora Effect */}
      {effect === 'aurora' && <AuroraEffect intensity={intensity} />}
      
      {/* Neural Constellation */}
      {effect === 'neural' && <NeuralConstellation mousePos={mousePosition} />}
      
      {/* REM Stage */}
      {effect === 'rem' && <REMStage />}
      
      {/* Dream Particles */}
      {effect === 'dream' && (
        <div className="dream-particles">
          {particles.map((particle) => (
            <motion.div
              key={particle.id}
              className="particle"
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: [0, 0.6, 0],
                scale: [0, 1, 0],
                x: [particle.x + '%', (particle.x + 20) + '%'],
                y: [particle.y + '%', (particle.y - 30) + '%']
              }}
              transition={{
                duration: particle.duration,
                delay: particle.delay,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              style={{
                position: 'absolute',
                width: particle.size * 10 + 'px',
                height: particle.size * 10 + 'px',
                background: 'radial-gradient(circle, rgba(255, 255, 255, 0.8), transparent)',
                borderRadius: '50%',
                filter: 'blur(1px)'
              }}
            />
          ))}
        </div>
      )}

      {/* Sleep Waves */}
      {effect === 'sleep' && <SleepWaves />}

      {/* Mystical Fog */}
      {effect === 'fog' && <MysticalFog intensity={intensity} />}

      {/* Poetry Overlay */}
      {poetryEnabled && (
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPoetry}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 0.6, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 2 }}
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
              color: 'white',
              fontSize: '1.5rem',
              fontWeight: '100',
              maxWidth: '600px',
              pointerEvents: 'none',
              textShadow: '0 0 20px rgba(0,0,0,0.5)'
            }}
          >
            {poetryLines[currentPoetry]}
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  );
};

// Aurora Effect Component
const AuroraEffect = ({ intensity }) => {
  const colors = [
    'rgba(0, 255, 170, 0.3)',
    'rgba(0, 170, 255, 0.5)',
    'rgba(170, 0, 255, 0.3)',
    'rgba(255, 0, 170, 0.3)',
    'rgba(0, 255, 255, 0.4)'
  ];

  return (
    <div style={{ position: 'absolute', width: '100%', height: '100%' }}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          animate={{
            x: ['-10%', '10%', '-10%'],
            opacity: [0, intensity * 0.8, 0],
            skewX: [0, -5, 0]
          }}
          transition={{
            duration: 15 + index * 3,
            delay: index * 5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{
            position: 'absolute',
            width: '200%',
            height: '60%',
            top: '20%',
            left: '-50%',
            background: `linear-gradient(90deg, transparent 0%, ${colors[index]} 20%, ${colors[index + 1]} 50%, ${colors[index + 2]} 80%, transparent 100%)`,
            filter: 'blur(60px)',
            mixBlendMode: 'screen'
          }}
        />
      ))}
    </div>
  );
};

// Neural Constellation Component
const NeuralConstellation = ({ mousePos }) => {
  const nodes = useMemo(() => {
    const nodeArray = [];
    for (let i = 0; i < 30; i++) {
      nodeArray.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        connections: []
      });
    }
    
    // Create connections between nearby nodes
    nodeArray.forEach((node, i) => {
      nodeArray.forEach((otherNode, j) => {
        if (i !== j) {
          const distance = Math.sqrt(
            Math.pow(node.x - otherNode.x, 2) + 
            Math.pow(node.y - otherNode.y, 2)
          );
          if (distance < 20) {
            node.connections.push(j);
          }
        }
      });
    });
    
    return nodeArray;
  }, []);

  return (
    <svg 
      style={{ 
        position: 'absolute', 
        width: '100%', 
        height: '100%',
        pointerEvents: 'none'
      }}
    >
      {/* Draw connections */}
      {nodes.map((node) => 
        node.connections.map((targetId) => {
          const target = nodes[targetId];
          const distance = Math.sqrt(
            Math.pow((mousePos.x - node.x), 2) + 
            Math.pow((mousePos.y - node.y), 2)
          );
          const opacity = distance < 30 ? 0.5 : 0.1;
          
          return (
            <motion.line
              key={`${node.id}-${targetId}`}
              x1={`${node.x}%`}
              y1={`${node.y}%`}
              x2={`${target.x}%`}
              y2={`${target.y}%`}
              stroke="rgba(100, 200, 255, 1)"
              strokeWidth="1"
              initial={{ opacity: 0 }}
              animate={{ opacity }}
              transition={{ duration: 0.3 }}
            />
          );
        })
      )}
      
      {/* Draw nodes */}
      {nodes.map((node) => {
        const distance = Math.sqrt(
          Math.pow((mousePos.x - node.x), 2) + 
          Math.pow((mousePos.y - node.y), 2)
        );
        const scale = distance < 20 ? 2 : 1;
        
        return (
          <motion.circle
            key={node.id}
            cx={`${node.x}%`}
            cy={`${node.y}%`}
            r="3"
            fill="white"
            animate={{ 
              scale,
              opacity: distance < 30 ? 1 : 0.5
            }}
            transition={{ duration: 0.3 }}
          />
        );
      })}
    </svg>
  );
};

// REM Stage Component
const REMStage = () => {
  return (
    <div style={{ position: 'absolute', width: '100%', height: '100%' }}>
      {[0, 1, 2, 3, 4].map((index) => (
        <motion.div
          key={index}
          animate={{
            x: [0, 50, -40, 30, 0],
            y: [0, -10, 15, -20, 0],
            opacity: [0, 0.6, 0.8, 0.3, 0]
          }}
          transition={{
            duration: 3,
            delay: index * 0.6,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{
            position: 'absolute',
            width: '40px',
            height: '40px',
            top: '50%',
            left: '50%',
            background: 'radial-gradient(circle, rgba(255, 255, 255, 0.8), transparent)',
            borderRadius: '50%',
            filter: 'blur(20px)',
            transform: 'translate(-50%, -50%)'
          }}
        />
      ))}
    </div>
  );
};

// Sleep Waves Component
const SleepWaves = () => {
  return (
    <div style={{ position: 'absolute', width: '100%', height: '100%' }}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          animate={{
            y: [0, -30, 0],
            scaleY: [1, 1.5, 1]
          }}
          transition={{
            duration: 8,
            delay: index * 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            width: '100%',
            height: '100px',
            background: `linear-gradient(to top, rgba(${99 + index * 20}, ${88 - index * 20}, 238, ${0.4 - index * 0.1}), transparent)`,
            opacity: 1 - index * 0.2
          }}
        />
      ))}
    </div>
  );
};

// Mystical Fog Component
const MysticalFog = ({ intensity }) => {
  return (
    <div style={{ position: 'absolute', width: '100%', height: '100%' }}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          animate={{
            x: ['-50%', '-30%', '-70%', '-50%'],
            y: ['-50%', '-60%', '-40%', '-50%'],
            scale: [1, 1.1, 0.9, 1]
          }}
          transition={{
            duration: 30 + index * 5,
            delay: index * 10,
            repeat: Infinity,
            ease: "linear"
          }}
          style={{
            position: 'absolute',
            width: '200%',
            height: '200%',
            top: '50%',
            left: '50%',
            background: 'radial-gradient(circle at center, rgba(147, 112, 219, 0.3) 0%, transparent 50%)',
            filter: 'blur(40px)',
            opacity: intensity * (0.6 - index * 0.2)
          }}
        />
      ))}
    </div>
  );
};

// Brain Wave Visualizer Component
const BrainWaveVisualizer = ({ stage = 'rem', className = '' }) => {
  const [waveData, setWaveData] = useState([]);
  const animationRef = useRef();

  useEffect(() => {
    const generateWaveData = () => {
      const waves = {
        delta: { frequency: 2, amplitude: 30, color: '#6366f1' },
        theta: { frequency: 4, amplitude: 25, color: '#a855f7' },
        alpha: { frequency: 8, amplitude: 20, color: '#ec4899' },
        beta: { frequency: 16, amplitude: 15, color: '#f59e0b' },
        gamma: { frequency: 32, amplitude: 10, color: '#10b981' }
      };

      const stageWaves = {
        awake: ['beta', 'gamma'],
        n1: ['alpha', 'theta'],
        n2: ['theta', 'delta'],
        n3: ['delta'],
        rem: ['theta', 'beta', 'gamma']
      };

      const activeWaves = stageWaves[stage] || stageWaves.rem;
      const data = [];
      
      activeWaves.forEach((waveType) => {
        const wave = waves[waveType];
        const points = [];
        for (let i = 0; i <= 100; i++) {
          const x = i;
          const y = 50 + wave.amplitude * Math.sin((i / 100) * wave.frequency * Math.PI * 2);
          points.push({ x, y });
        }
        data.push({ type: waveType, points, color: wave.color });
      });
      
      setWaveData(data);
    };

    generateWaveData();
    const interval = setInterval(generateWaveData, 100);
    return () => clearInterval(interval);
  }, [stage]);

  return (
    <svg 
      className={`brain-wave-visualizer ${className}`}
      style={{ 
        width: '100%', 
        height: '200px',
        position: 'absolute',
        bottom: 0,
        left: 0,
        opacity: 0.6
      }}
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
    >
      {waveData.map((wave) => (
        <motion.path
          key={wave.type}
          d={`M ${wave.points.map(p => `${p.x},${p.y}`).join(' L ')}`}
          fill="none"
          stroke={wave.color}
          strokeWidth="0.5"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, ease: "linear" }}
          style={{
            filter: `drop-shadow(0 0 10px ${wave.color})`,
            vectorEffect: 'non-scaling-stroke'
          }}
        />
      ))}
    </svg>
  );
};

// Main Export with all components
export default function DreamWeaverBackground({ 
  preset = 'full',
  children 
}) {
  const [activeEffect, setActiveEffect] = useState('aurora');
  const [sleepStage, setSleepStage] = useState('rem');

  const effects = ['aurora', 'neural', 'rem', 'dream', 'sleep', 'fog'];
  
  // Auto-rotate effects every 30 seconds if preset is 'full'
  useEffect(() => {
    if (preset !== 'full') return;
    
    const interval = setInterval(() => {
      setActiveEffect((prev) => {
        const currentIndex = effects.indexOf(prev);
        return effects[(currentIndex + 1) % effects.length];
      });
    }, 30000);
    
    return () => clearInterval(interval);
  }, [preset]);

  return (
    <div style={{ 
      position: 'relative', 
      width: '100%', 
      height: '100vh',
      overflow: 'hidden',
      background: '#000'
    }}>
      {/* Layer 1: Base Dream Background */}
      <DreamBackground 
        effect={activeEffect}
        intensity={0.8}
        interactive={true}
        poetryEnabled={preset === 'full'}
      />
      
      {/* Layer 2: Brain Waves (only in full preset) */}
      {preset === 'full' && (
        <BrainWaveVisualizer 
          stage={sleepStage}
          className="brain-waves-overlay"
        />
      )}
      
      {/* Layer 3: Content */}
      <div style={{ 
        position: 'relative', 
        zIndex: 10,
        width: '100%',
        height: '100%'
      }}>
        {children}
      </div>

      {/* Controls (only in full preset) */}
      {preset === 'full' && (
        <div style={{
          position: 'fixed',
          bottom: '30px',
          right: '30px',
          zIndex: 1000,
          background: 'rgba(0, 0, 0, 0.6)',
          backdropFilter: 'blur(10px)',
          padding: '20px',
          borderRadius: '15px',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ marginBottom: '15px' }}>
            <h3 style={{ 
              color: 'rgba(255, 255, 255, 0.8)',
              fontSize: '12px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              marginBottom: '10px'
            }}>
              Background Effect
            </h3>
            <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
              {effects.map((effect) => (
                <button
                  key={effect}
                  onClick={() => setActiveEffect(effect)}
                  style={{
                    padding: '5px 10px',
                    background: activeEffect === effect 
                      ? 'linear-gradient(90deg, #00ffcc, #7c3aed)'
                      : 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '15px',
                    color: 'white',
                    fontSize: '11px',
                    cursor: 'pointer',
                    transition: 'all 0.3s'
                  }}
                >
                  {effect}
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <h3 style={{ 
              color: 'rgba(255, 255, 255, 0.8)',
              fontSize: '12px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              marginBottom: '10px'
            }}>
              Sleep Stage
            </h3>
            <div style={{ display: 'flex', gap: '5px' }}>
              {['awake', 'n1', 'n2', 'n3', 'rem'].map((stage) => (
                <button
                  key={stage}
                  onClick={() => setSleepStage(stage)}
                  style={{
                    padding: '5px 10px',
                    background: sleepStage === stage 
                      ? 'linear-gradient(90deg, #00ffcc, #7c3aed)'
                      : 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '15px',
                    color: 'white',
                    fontSize: '11px',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    textTransform: 'uppercase'
                  }}
                >
                  {stage}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
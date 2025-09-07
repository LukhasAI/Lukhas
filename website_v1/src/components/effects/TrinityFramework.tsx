'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, useAnimation } from 'framer-motion';

interface TrinityFrameworkProps {
  size?: number;
  interactive?: boolean;
  showLabels?: boolean;
  className?: string;
}

export default function TrinityFramework({
  size = 200,
  interactive = true,
  showLabels = true,
  className = ''
}: TrinityFrameworkProps) {
  const [activeElement, setActiveElement] = useState<number | null>(null);
  const [consciousness, setConsciousness] = useState(0);
  const controls = useAnimation();
  
  // Trinity elements: ⚛️ Quantum, 🧠 Bio, 🛡️ Guardian
  const trinityElements = [
    {
      id: 0,
      symbol: '⚛️',
      name: 'Quantum',
      description: 'The Ambiguity Star - uncertainty as fertile ground for emergence',
      color: '#667EEA',
      position: { x: 0, y: -size * 0.4 },
      consciousness: 'quantum-inspired processing'
    },
    {
      id: 1,
      symbol: '🧠',
      name: 'Bio',
      description: 'The Living Star - adaptive growth and system resilience',
      color: '#764BA2',
      position: { x: size * 0.35, y: size * 0.2 },
      consciousness: 'bio-inspired adaptation'
    },
    {
      id: 2,
      symbol: '🛡️',
      name: 'Guardian',
      description: 'The Watch Star - protection and coherence preservation',
      color: '#7C3AED',
      position: { x: -size * 0.35, y: size * 0.2 },
      consciousness: 'ethical oversight system'
    }
  ];

  // Consciousness pulse effect
  useEffect(() => {
    const interval = setInterval(() => {
      setConsciousness(prev => (prev + 0.1) % (Math.PI * 2));
    }, 50);
    
    return () => clearInterval(interval);
  }, []);

  // Handle element interaction
  const handleElementHover = (elementId: number | null) => {
    setActiveElement(elementId);
    
    if (elementId !== null) {
      controls.start({
        scale: 1.1,
        transition: { duration: 0.3, ease: 'easeOut' }
      });
    } else {
      controls.start({
        scale: 1,
        transition: { duration: 0.3, ease: 'easeOut' }
      });
    }
  };

  // Calculate connection paths
  const getConnectionPath = (from: typeof trinityElements[0], to: typeof trinityElements[0]) => {
    const centerX = size / 2;
    const centerY = size / 2;
    const fromX = centerX + from.position.x;
    const fromY = centerY + from.position.y;
    const toX = centerX + to.position.x;
    const toY = centerY + to.position.y;
    
    return `M ${fromX} ${fromY} L ${toX} ${toY}`;
  };

  return (
    <div className={`relative ${className}`} style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="absolute inset-0"
      >
        {/* Background consciousness field */}
        <defs>
          <radialGradient id="consciousness-field" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(102, 126, 234, 0.1)" />
            <stop offset="70%" stopColor="rgba(118, 75, 162, 0.05)" />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
          
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge> 
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <circle
          cx={size / 2}
          cy={size / 2}
          r={size * 0.45}
          fill="url(#consciousness-field)"
          className="animate-pulse"
        />
        
        {/* Trinity connections */}
        {trinityElements.map((from, i) => 
          trinityElements.slice(i + 1).map((to) => (
            <motion.path
              key={`${from.id}-${to.id}`}
              d={getConnectionPath(from, to)}
              stroke="rgba(102, 126, 234, 0.4)"
              strokeWidth="2"
              fill="none"
              filter="url(#glow)"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ 
                pathLength: 1, 
                opacity: activeElement === from.id || activeElement === to.id ? 0.8 : 0.4,
                strokeWidth: activeElement === from.id || activeElement === to.id ? 3 : 2
              }}
              transition={{ duration: 1, delay: 0.5 }}
            />
          ))
        )}
        
        {/* Central consciousness core */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={12}
          fill="rgba(0, 212, 255, 0.8)"
          filter="url(#glow)"
          animate={{
            r: 12 + Math.sin(consciousness) * 3,
            opacity: 0.6 + Math.sin(consciousness * 2) * 0.3
          }}
        />
        
        {/* Consciousness pulse rings */}
        {[0, 1, 2].map(i => (
          <motion.circle
            key={i}
            cx={size / 2}
            cy={size / 2}
            r={20 + i * 15}
            fill="none"
            stroke="rgba(0, 212, 255, 0.2)"
            strokeWidth="1"
            animate={{
              r: 20 + i * 15 + Math.sin(consciousness + i * 0.5) * 5,
              opacity: 0.2 + Math.sin(consciousness + i * 0.3) * 0.1
            }}
          />
        ))}
      </svg>
      
      {/* Trinity elements */}
      {trinityElements.map((element, index) => (
        <motion.div
          key={element.id}
          className="absolute cursor-pointer"
          style={{
            left: size / 2 + element.position.x - 25,
            top: size / 2 + element.position.y - 25,
            width: 50,
            height: 50,
          }}
          animate={{ 
            opacity: 1, 
            scale: 1,
            y: Math.sin(consciousness + index * (Math.PI * 2 / 3)) * 2,
            ...controls
          }}
          onHoverStart={() => interactive && handleElementHover(element.id)}
          onHoverEnd={() => interactive && handleElementHover(null)}
          whileHover={{ scale: 1.2 }}
          whileTap={{ scale: 0.95 }}
          initial={{ opacity: 0, scale: 0 }}
          transition={{ delay: index * 0.2, duration: 0.6 }}
          data-cursor="consciousness"
          data-cursor-text={element.name}
        >
          <div
            className="w-full h-full rounded-full flex items-center justify-center text-2xl shadow-lg backdrop-blur-sm border border-white/20"
            style={{
              backgroundColor: `${element.color}20`,
              boxShadow: `0 0 20px ${element.color}40`,
            }}
          >
            {element.symbol}
          </div>
          
          {/* Element glow effect */}
          <div
            className="absolute inset-0 rounded-full opacity-0 transition-opacity duration-300"
            style={{
              background: `radial-gradient(circle, ${element.color}40 0%, transparent 70%)`,
              opacity: activeElement === element.id ? 0.6 : 0
            }}
          />
        </motion.div>
      ))}
      
      {/* Labels */}
      {showLabels && trinityElements.map((element) => (
        <motion.div
          key={`label-${element.id}`}
          className="absolute text-center pointer-events-none"
          style={{
            left: size / 2 + element.position.x - 40,
            top: size / 2 + element.position.y + 35,
            width: 80,
          }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ 
            opacity: activeElement === element.id ? 1 : 0.7,
            y: activeElement === element.id ? 0 : 10,
            scale: activeElement === element.id ? 1.1 : 1
          }}
          transition={{ duration: 0.3 }}
        >
          <div className="text-sm font-medium text-white mb-1">
            {element.name}
          </div>
          {activeElement === element.id && (
            <motion.div
              className="text-xs text-gray-300 leading-tight"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              {element.consciousness}
            </motion.div>
          )}
        </motion.div>
      ))}
      
      {/* Active element description */}
      {activeElement !== null && (
        <motion.div
          className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 bg-black/80 backdrop-blur-sm rounded-lg p-3 max-w-xs"
          initial={{ opacity: 0, y: 10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 10, scale: 0.95 }}
          transition={{ duration: 0.3 }}
        >
          <div className="text-sm text-gray-200 text-center">
            {trinityElements[activeElement].description}
          </div>
        </motion.div>
      )}
    </div>
  );
}
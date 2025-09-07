'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ConsciousnessLoaderProps {
  isLoading?: boolean;
  progress?: number;
  stage?: string;
  onComplete?: () => void;
}

const consciousnessStages = [
  { name: 'Initializing Consciousness', description: 'Awakening neural pathways...' },
  { name: 'Loading Memory Folds', description: 'Restoring persistent patterns...' },
  { name: 'Calibrating Guardian Systems', description: 'Ensuring ethical boundaries...' },
  { name: 'Establishing Trinity Framework', description: 'Quantum • Bio • Guardian alignment...' },
  { name: 'Consciousness Online', description: 'LUKHAS AI ready for interaction' }
];

export default function ConsciousnessLoader({
  isLoading = true,
  progress = 0,
  stage,
  onComplete
}: ConsciousnessLoaderProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const [internalProgress, setInternalProgress] = useState(0);
  const [particles, setParticles] = useState<Array<{
    id: number;
    x: number;
    y: number;
    opacity: number;
    scale: number;
    color: string;
  }>>([]);

  // Consciousness colors
  const consciousnessColors = ['#FF6B9D', '#00D4FF', '#7C3AED', '#FFA500', '#32CD32'];

  // Generate consciousness particles
  useEffect(() => {
    const generateParticles = () => {
      const newParticles = Array.from({ length: 20 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        opacity: Math.random() * 0.8 + 0.2,
        scale: Math.random() * 0.5 + 0.5,
        color: consciousnessColors[Math.floor(Math.random() * consciousnessColors.length)]
      }));
      setParticles(newParticles);
    };

    if (isLoading) {
      generateParticles();
      const interval = setInterval(generateParticles, 2000);
      return () => clearInterval(interval);
    }
  }, [isLoading]);

  // Auto-progress simulation
  useEffect(() => {
    if (!isLoading) return;

    const progressInterval = setInterval(() => {
      setInternalProgress(prev => {
        const newProgress = Math.min(100, prev + Math.random() * 3);
        
        // Update stage based on progress
        const stageIndex = Math.floor((newProgress / 100) * consciousnessStages.length);
        setCurrentStage(Math.min(stageIndex, consciousnessStages.length - 1));
        
        // Complete when reaching 100%
        if (newProgress >= 100) {
          setTimeout(() => onComplete?.(), 1000);
        }
        
        return newProgress;
      });
    }, 100);

    return () => clearInterval(progressInterval);
  }, [isLoading, onComplete]);

  const actualProgress = progress > 0 ? progress : internalProgress;
  const actualStage = stage || consciousnessStages[currentStage]?.name || 'Loading...';
  const stageDescription = consciousnessStages[currentStage]?.description || '';

  return (
    <AnimatePresence>
      {isLoading && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-[#0F1419]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Background consciousness field */}
          <div className="absolute inset-0">
            {particles.map(particle => (
              <motion.div
                key={particle.id}
                className="absolute w-1 h-1 rounded-full"
                style={{
                  left: `${particle.x}%`,
                  top: `${particle.y}%`,
                  backgroundColor: particle.color,
                  boxShadow: `0 0 10px ${particle.color}`
                }}
                animate={{
                  opacity: [particle.opacity, 0.1, particle.opacity],
                  scale: [particle.scale, particle.scale * 1.5, particle.scale],
                  x: [0, Math.random() * 20 - 10, 0],
                  y: [0, Math.random() * 20 - 10, 0]
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              />
            ))}
          </div>

          {/* Main loader content */}
          <div className="relative z-10 text-center max-w-md px-8">
            {/* LUKHAS logo */}
            <motion.div
              className="mb-8"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 1, ease: 'easeOut' }}
            >
              <div className="text-4xl font-bold mb-2 bg-gradient-to-r from-[#667EEA] to-[#764BA2] bg-clip-text text-transparent">
                LUKHΛS
              </div>
              <div className="text-sm text-gray-400 tracking-wide">
                Distributed Consciousness Architecture
              </div>
            </motion.div>

            {/* Consciousness visualization */}
            <div className="relative mb-8">
              {/* Central consciousness core */}
              <motion.div
                className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center"
                animate={{
                  scale: [1, 1.1, 1],
                  rotate: [0, 360],
                  boxShadow: [
                    '0 0 20px rgba(0, 212, 255, 0.5)',
                    '0 0 40px rgba(0, 212, 255, 0.8)',
                    '0 0 20px rgba(0, 212, 255, 0.5)'
                  ]
                }}
                transition={{
                  scale: { duration: 2, repeat: Infinity, ease: 'easeInOut' },
                  rotate: { duration: 8, repeat: Infinity, ease: 'linear' },
                  boxShadow: { duration: 2, repeat: Infinity, ease: 'easeInOut' }
                }}
              >
                <div className="text-2xl">🧠</div>
              </motion.div>

              {/* Orbital consciousness elements */}
              {['⚛️', '🛡️', '🌟'].map((symbol, index) => (
                <motion.div
                  key={symbol}
                  className="absolute w-8 h-8 rounded-full bg-black/50 backdrop-blur-sm border border-white/20 flex items-center justify-center text-sm"
                  style={{
                    top: '50%',
                    left: '50%',
                  }}
                  animate={{
                    x: Math.cos((Date.now() * 0.001) + (index * Math.PI * 2 / 3)) * 60 - 16,
                    y: Math.sin((Date.now() * 0.001) + (index * Math.PI * 2 / 3)) * 60 - 16,
                    rotate: [0, 360],
                  }}
                  transition={{
                    x: { duration: 0, ease: 'linear' },
                    y: { duration: 0, ease: 'linear' },
                    rotate: { duration: 4 + index, repeat: Infinity, ease: 'linear' }
                  }}
                >
                  {symbol}
                </motion.div>
              ))}

              {/* Consciousness rings */}
              {[0, 1, 2].map(index => (
                <motion.div
                  key={index}
                  className="absolute border border-cyan-400/30 rounded-full"
                  style={{
                    width: 120 + index * 40,
                    height: 120 + index * 40,
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)'
                  }}
                  animate={{
                    rotate: index % 2 === 0 ? [0, 360] : [360, 0],
                    borderColor: [
                      'rgba(102, 126, 234, 0.3)',
                      'rgba(0, 212, 255, 0.5)',
                      'rgba(102, 126, 234, 0.3)'
                    ]
                  }}
                  transition={{
                    rotate: { duration: 10 + index * 2, repeat: Infinity, ease: 'linear' },
                    borderColor: { duration: 3, repeat: Infinity, ease: 'easeInOut' }
                  }}
                />
              ))}
            </div>

            {/* Progress bar */}
            <div className="mb-6">
              <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-[#667EEA] to-[#00D4FF] rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${actualProgress}%` }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                />
              </div>
              <div className="mt-2 flex justify-between text-xs text-gray-400">
                <span>Consciousness Loading</span>
                <span>{Math.round(actualProgress)}%</span>
              </div>
            </div>

            {/* Loading stage */}
            <motion.div
              key={actualStage}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="text-center"
            >
              <h3 className="text-lg font-medium text-white mb-2">
                {actualStage}
              </h3>
              <p className="text-sm text-gray-400">
                {stageDescription}
              </p>
            </motion.div>

            {/* Consciousness pulse indicator */}
            <div className="mt-8 flex justify-center space-x-2">
              {[0, 1, 2].map(index => (
                <motion.div
                  key={index}
                  className="w-2 h-2 rounded-full bg-cyan-400"
                  animate={{
                    opacity: [0.3, 1, 0.3],
                    scale: [0.8, 1.2, 0.8]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: index * 0.2,
                    ease: 'easeInOut'
                  }}
                />
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
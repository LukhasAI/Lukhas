'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

interface ConsciousCursorProps {
  children: React.ReactNode;
}

export default function ConsciousCursor({ children }: ConsciousCursorProps) {
  const [isHovering, setIsHovering] = useState(false);
  const [cursorText, setCursorText] = useState('');
  const [cursorVariant, setCursorVariant] = useState('default');
  
  const cursorX = useMotionValue(-100);
  const cursorY = useMotionValue(-100);
  
  // Smooth spring animations for cursor
  const springConfig = { damping: 30, stiffness: 400, mass: 0.5 };
  const cursorXSpring = useSpring(cursorX, springConfig);
  const cursorYSpring = useSpring(cursorY, springConfig);
  
  // Consciousness trail particles
  const [trails, setTrails] = useState<Array<{
    id: number;
    x: number;
    y: number;
    opacity: number;
    scale: number;
    color: string;
  }>>([]);
  
  const trailRef = useRef<number>(0);

  // LUKHAS consciousness colors
  const consciousnessColors = [
    '#FF6B9D', // Identity
    '#00D4FF', // Consciousness
    '#7C3AED', // Guardian
    '#FFA500', // Integration
    '#32CD32'  // Validation
  ];

  const addTrailParticle = useCallback((x: number, y: number) => {
    const newTrail = {
      id: trailRef.current++,
      x,
      y,
      opacity: 0.8,
      scale: 1,
      color: consciousnessColors[Math.floor(Math.random() * consciousnessColors.length)]
    };
    
    setTrails(prev => [...prev.slice(-15), newTrail]);
    
    // Fade out particles
    setTimeout(() => {
      setTrails(prev => prev.map(trail => 
        trail.id === newTrail.id 
          ? { ...trail, opacity: 0, scale: 0.1 }
          : trail
      ));
    }, 100);
    
    // Remove particles
    setTimeout(() => {
      setTrails(prev => prev.filter(trail => trail.id !== newTrail.id));
    }, 1000);
  }, [consciousnessColors]);

  const moveCursor = useCallback((e: MouseEvent) => {
    cursorX.set(e.clientX - 16);
    cursorY.set(e.clientY - 16);
    
    // Add consciousness trail particles
    if (Math.random() > 0.7) {
      addTrailParticle(e.clientX, e.clientY);
    }
  }, [cursorX, cursorY, addTrailParticle]);

  // Handle mouse interactions
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => moveCursor(e);
    const handleMouseEnter = () => setIsHovering(true);
    const handleMouseLeave = () => setIsHovering(false);

    // Add cursor interaction listeners
    const handleInteractiveHover = (e: Event) => {
      const target = e.target as HTMLElement;
      const interactiveType = target.getAttribute('data-cursor');
      
      if (interactiveType) {
        setCursorVariant(interactiveType);
        setCursorText(target.getAttribute('data-cursor-text') || '');
        setIsHovering(true);
      }
    };

    const handleInteractiveLeave = () => {
      setCursorVariant('default');
      setCursorText('');
      setIsHovering(false);
    };

    // Event listeners
    window.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseenter', handleMouseEnter);
    document.addEventListener('mouseleave', handleMouseLeave);

    // Interactive element listeners
    const interactiveElements = document.querySelectorAll('[data-cursor]');
    interactiveElements.forEach(element => {
      element.addEventListener('mouseenter', handleInteractiveHover);
      element.addEventListener('mouseleave', handleInteractiveLeave);
    });

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseenter', handleMouseEnter);
      document.removeEventListener('mouseleave', handleMouseLeave);
      
      interactiveElements.forEach(element => {
        element.removeEventListener('mouseenter', handleInteractiveHover);
        element.removeEventListener('mouseleave', handleInteractiveLeave);
      });
    };
  }, [moveCursor]);

  const cursorVariants = {
    default: {
      height: 32,
      width: 32,
      backgroundColor: 'rgba(102, 126, 234, 0.8)',
      border: '2px solid rgba(102, 126, 234, 0.3)',
      transition: {
        type: 'spring',
        damping: 30,
        stiffness: 400
      }
    },
    text: {
      height: 8,
      width: 8,
      backgroundColor: 'rgba(247, 250, 252, 0.8)',
      border: 'none',
      transition: {
        type: 'spring',
        damping: 30,
        stiffness: 400
      }
    },
    link: {
      height: 48,
      width: 48,
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      border: '2px solid rgba(102, 126, 234, 1)',
      transition: {
        type: 'spring',
        damping: 20,
        stiffness: 300
      }
    },
    button: {
      height: 64,
      width: 64,
      backgroundColor: 'rgba(255, 107, 157, 0.1)',
      border: '2px solid rgba(255, 107, 157, 1)',
      transition: {
        type: 'spring',
        damping: 20,
        stiffness: 300
      }
    },
    consciousness: {
      height: 80,
      width: 80,
      backgroundColor: 'rgba(0, 212, 255, 0.1)',
      border: '3px solid rgba(0, 212, 255, 1)',
      transition: {
        type: 'spring',
        damping: 15,
        stiffness: 250
      }
    }
  };

  return (
    <>
      {children}
      
      {/* Main cursor */}
      <motion.div
        className="fixed top-0 left-0 pointer-events-none z-50 mix-blend-difference rounded-full"
        style={{
          x: cursorXSpring,
          y: cursorYSpring,
        }}
        variants={cursorVariants}
        animate={cursorVariant}
        initial="default"
      >
        {/* Cursor text */}
        {cursorText && (
          <motion.div
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-white text-sm font-medium whitespace-nowrap"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
          >
            {cursorText}
          </motion.div>
        )}
      </motion.div>

      {/* Consciousness trail particles */}
      <div className="fixed top-0 left-0 pointer-events-none z-40">
        {trails.map(trail => (
          <motion.div
            key={trail.id}
            className="absolute w-2 h-2 rounded-full"
            style={{
              left: trail.x - 4,
              top: trail.y - 4,
              backgroundColor: trail.color,
              boxShadow: `0 0 12px ${trail.color}`,
            }}
            initial={{ opacity: 0.8, scale: 1 }}
            animate={{ 
              opacity: trail.opacity, 
              scale: trail.scale,
            }}
            transition={{ 
              duration: 0.8, 
              ease: 'easeOut' 
            }}
          />
        ))}
      </div>

      {/* Neural network cursor effect */}
      {isHovering && (
        <motion.div
          className="fixed top-0 left-0 pointer-events-none z-30"
          style={{
            x: cursorXSpring,
            y: cursorYSpring,
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.6 }}
          exit={{ opacity: 0 }}
        >
          {/* Animated rings */}
          {[0, 1, 2].map(index => (
            <motion.div
              key={index}
              className="absolute border border-cyan-400 rounded-full"
              style={{
                width: 60 + index * 20,
                height: 60 + index * 20,
                left: -(30 + index * 10),
                top: -(30 + index * 10),
              }}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.6, 0.2, 0.6],
              }}
              transition={{
                duration: 2,
                delay: index * 0.2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          ))}
        </motion.div>
      )}

      <style jsx global>{`
        * {
          cursor: none !important;
        }
        
        a, button, [role="button"], input, textarea, select {
          cursor: none !important;
        }
      `}</style>
    </>
  );
}
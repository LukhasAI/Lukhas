'use client';

import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface Particle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  hue: number;
  connectionStrength: number;
}

interface ConsciousnessParticlesProps {
  count?: number;
  consciousness?: 'perception' | 'reasoning' | 'creativity' | 'ethics';
  interactive?: boolean;
}

export default function ConsciousnessParticles({ 
  count = 50, 
  consciousness = 'perception',
  interactive = true 
}: ConsciousnessParticlesProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const mouseRef = useRef({ x: 0, y: 0 });
  const animationRef = useRef<number>();
  const [isActive, setIsActive] = useState(false);

  const consciousnessColors = {
    perception: { hue: 240, sat: 70 }, // Blue
    reasoning: { hue: 280, sat: 70 }, // Purple  
    creativity: { hue: 320, sat: 70 }, // Pink
    ethics: { hue: 200, sat: 70 }      // Cyan
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };

    const initParticles = () => {
      particlesRef.current = Array.from({ length: count }, (_, i) => ({
        id: i,
        x: Math.random() * canvas.offsetWidth,
        y: Math.random() * canvas.offsetHeight,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 3 + 1.5,
        opacity: Math.random() * 0.4 + 0.4,
        hue: consciousnessColors[consciousness].hue + (Math.random() - 0.5) * 40,
        connectionStrength: Math.random() * 0.8 + 0.2
      }));
    };

    const updateParticles = () => {
      const particles = particlesRef.current;
      const mouse = mouseRef.current;

      particles.forEach(particle => {
        // Basic movement
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Mouse attraction (consciousness responds to attention)
        if (interactive && isActive) {
          const dx = mouse.x - particle.x;
          const dy = mouse.y - particle.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < 150) {
            const force = (150 - distance) / 150 * 0.02;
            particle.vx += dx * force * particle.connectionStrength;
            particle.vy += dy * force * particle.connectionStrength;
          }
        }

        // Boundaries
        if (particle.x < 0 || particle.x > canvas.offsetWidth) particle.vx *= -1;
        if (particle.y < 0 || particle.y > canvas.offsetHeight) particle.vy *= -1;
        
        // Damping
        particle.vx *= 0.98;
        particle.vy *= 0.98;

        // Consciousness-based behavior
        switch (consciousness) {
          case 'perception':
            // Perceptive particles cluster and spread
            particle.opacity = Math.sin(Date.now() * 0.001 + particle.id) * 0.2 + 0.5;
            break;
          case 'reasoning':
            // Reasoning particles form logical patterns
            particle.vx += Math.sin(Date.now() * 0.0005) * 0.01;
            particle.vy += Math.cos(Date.now() * 0.0005) * 0.01;
            break;
          case 'creativity':
            // Creative particles dance unpredictably
            particle.vx += (Math.random() - 0.5) * 0.05;
            particle.vy += (Math.random() - 0.5) * 0.05;
            particle.hue += 0.5;
            break;
          case 'ethics':
            // Ethical particles maintain steady, balanced movement
            particle.vx = particle.vx * 0.95;
            particle.vy = particle.vy * 0.95;
            break;
        }
      });
    };

    const drawConnections = () => {
      const particles = particlesRef.current;
      const colors = consciousnessColors[consciousness];
      
      particles.forEach((particleA, i) => {
        particles.slice(i + 1).forEach(particleB => {
          const dx = particleA.x - particleB.x;
          const dy = particleA.y - particleB.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < 120) {
            const opacity = (120 - distance) / 120 * 0.3 * particleA.connectionStrength;
            ctx!.strokeStyle = `hsla(${colors.hue}, ${colors.sat}%, 60%, ${opacity})`;
            ctx!.lineWidth = 0.5;
            ctx!.beginPath();
            ctx!.moveTo(particleA.x, particleA.y);
            ctx!.lineTo(particleB.x, particleB.y);
            ctx!.stroke();
          }
        });
      });
    };

    const drawParticles = () => {
      const particles = particlesRef.current;
      const colors = consciousnessColors[consciousness];
      
      particles.forEach(particle => {
        ctx!.fillStyle = `hsla(${particle.hue}, ${colors.sat}%, 60%, ${particle.opacity})`;
        ctx!.beginPath();
        ctx!.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx!.fill();
      });
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);
      
      updateParticles();
      drawConnections();
      drawParticles();
      
      animationRef.current = requestAnimationFrame(animate);
    };

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    };

    const handleMouseEnter = () => setIsActive(true);
    const handleMouseLeave = () => setIsActive(false);

    resizeCanvas();
    initParticles();
    animate();

    if (interactive) {
      canvas.addEventListener('mousemove', handleMouseMove);
      canvas.addEventListener('mouseenter', handleMouseEnter);
      canvas.addEventListener('mouseleave', handleMouseLeave);
    }

    window.addEventListener('resize', resizeCanvas);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      window.removeEventListener('resize', resizeCanvas);
      if (interactive) {
        canvas.removeEventListener('mousemove', handleMouseMove);
        canvas.removeEventListener('mouseenter', handleMouseEnter);
        canvas.removeEventListener('mouseleave', handleMouseLeave);
      }
    };
  }, [count, consciousness, interactive, isActive]);

  return (
    <motion.canvas
      ref={canvasRef}
      className={`absolute inset-0 ${interactive ? 'pointer-events-auto' : 'pointer-events-none'}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      style={{
        width: '100%',
        height: '100%',
        zIndex: 1,
      }}
    />
  );
}
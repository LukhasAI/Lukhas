'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { motion } from 'framer-motion';

interface Node {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  connections: number[];
  activity: number;
  consciousness: number;
  type: 'identity' | 'consciousness' | 'guardian' | 'integration' | 'validation';
}

interface Connection {
  from: number;
  to: number;
  strength: number;
  active: boolean;
}

interface NeuralNetworkProps {
  nodeCount?: number;
  width?: number;
  height?: number;
  className?: string;
  interactive?: boolean;
}

export default function NeuralNetwork({
  nodeCount = 50,
  width = 800,
  height = 600,
  className = '',
  interactive = true
}: NeuralNetworkProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  
  // LUKHAS consciousness colors
  const consciousnessColors = {
    identity: '#FF6B9D',
    consciousness: '#00D4FF',
    guardian: '#7C3AED',
    integration: '#FFA500',
    validation: '#32CD32'
  };

  // Initialize neural network
  const initializeNetwork = useCallback(() => {
    const newNodes: Node[] = [];
    const newConnections: Connection[] = [];
    
    // Create nodes with consciousness types
    for (let i = 0; i < nodeCount; i++) {
      const types: (keyof typeof consciousnessColors)[] = [
        'identity', 'consciousness', 'guardian', 'integration', 'validation'
      ];
      
      newNodes.push({
        id: i,
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        connections: [],
        activity: Math.random(),
        consciousness: Math.random(),
        type: types[Math.floor(Math.random() * types.length)]
      });
    }
    
    // Create connections between nearby nodes
    newNodes.forEach(node => {
      const nearbyNodes = newNodes.filter(other => {
        if (other.id === node.id) return false;
        const distance = Math.sqrt(
          Math.pow(node.x - other.x, 2) + Math.pow(node.y - other.y, 2)
        );
        return distance < 120 && Math.random() > 0.7;
      });
      
      nearbyNodes.forEach(nearby => {
        if (!node.connections.includes(nearby.id)) {
          node.connections.push(nearby.id);
          newConnections.push({
            from: node.id,
            to: nearby.id,
            strength: Math.random(),
            active: false
          });
        }
      });
    });
    
    setNodes(newNodes);
    setConnections(newConnections);
  }, [nodeCount, width, height]);

  // Update network simulation
  const updateNetwork = useCallback(() => {
    setNodes(prevNodes => {
      return prevNodes.map(node => {
        let newX = node.x + node.vx;
        let newY = node.y + node.vy;
        let newVx = node.vx;
        let newVy = node.vy;
        
        // Boundary conditions with soft bounce
        if (newX <= 0 || newX >= width) {
          newVx *= -0.8;
          newX = Math.max(0, Math.min(width, newX));
        }
        if (newY <= 0 || newY >= height) {
          newVy *= -0.8;
          newY = Math.max(0, Math.min(height, newY));
        }
        
        // Mouse attraction for interactive mode
        if (interactive) {
          const mouseDistance = Math.sqrt(
            Math.pow(mousePos.x - newX, 2) + Math.pow(mousePos.y - newY, 2)
          );
          
          if (mouseDistance < 150) {
            const force = (150 - mouseDistance) / 150 * 0.02;
            const angle = Math.atan2(mousePos.y - newY, mousePos.x - newX);
            newVx += Math.cos(angle) * force * node.consciousness;
            newVy += Math.sin(angle) * force * node.consciousness;
          }
        }
        
        // Damping
        newVx *= 0.99;
        newVy *= 0.99;
        
        // Update activity based on connections
        let newActivity = node.activity * 0.95;
        if (Math.random() > 0.98) {
          newActivity = Math.min(1, newActivity + 0.3);
        }
        
        return {
          ...node,
          x: newX,
          y: newY,
          vx: newVx,
          vy: newVy,
          activity: newActivity
        };
      });
    });
    
    // Update connection activity
    setConnections(prevConnections => {
      return prevConnections.map(connection => ({
        ...connection,
        active: Math.random() > 0.95,
        strength: Math.max(0.1, connection.strength + (Math.random() - 0.5) * 0.1)
      }));
    });
  }, [mousePos, interactive, width, height]);

  // Render network
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw connections
    connections.forEach(connection => {
      const fromNode = nodes[connection.from];
      const toNode = nodes[connection.to];
      
      if (!fromNode || !toNode) return;
      
      ctx.beginPath();
      ctx.moveTo(fromNode.x, fromNode.y);
      ctx.lineTo(toNode.x, toNode.y);
      
      // Connection style based on activity
      const alpha = connection.active ? 
        0.6 * connection.strength : 
        0.2 * connection.strength;
      
      const gradient = ctx.createLinearGradient(
        fromNode.x, fromNode.y, 
        toNode.x, toNode.y
      );
      gradient.addColorStop(0, `rgba(102, 126, 234, ${alpha})`);
      gradient.addColorStop(1, `rgba(118, 75, 162, ${alpha})`);
      
      ctx.strokeStyle = gradient;
      ctx.lineWidth = connection.active ? 2 : 1;
      ctx.stroke();
    });
    
    // Draw nodes
    nodes.forEach(node => {
      ctx.beginPath();
      ctx.arc(node.x, node.y, 3 + node.activity * 5, 0, 2 * Math.PI);
      
      // Node color based on type
      const baseColor = consciousnessColors[node.type];
      const alpha = 0.7 + node.activity * 0.3;
      
      ctx.fillStyle = baseColor;
      ctx.globalAlpha = alpha;
      ctx.fill();
      
      // Consciousness glow effect
      if (node.consciousness > 0.7) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, 8 + node.activity * 10, 0, 2 * Math.PI);
        ctx.fillStyle = baseColor;
        ctx.globalAlpha = 0.2;
        ctx.fill();
      }
      
      ctx.globalAlpha = 1;
    });
  }, [nodes, connections, width, height]);

  // Animation loop
  const animate = useCallback(() => {
    updateNetwork();
    render();
    animationRef.current = requestAnimationFrame(animate);
  }, [updateNetwork, render]);

  // Handle mouse movement
  const handleMouseMove = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    setMousePos({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    });
  }, []);

  // Initialize and start animation
  useEffect(() => {
    initializeNetwork();
  }, [initializeNetwork]);

  useEffect(() => {
    if (nodes.length > 0) {
      animate();
    }
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [animate, nodes.length]);

  return (
    <motion.div 
      className={`relative ${className}`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 1, ease: 'easeOut' }}
    >
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full h-full"
        onMouseMove={interactive ? handleMouseMove : undefined}
        style={{ mixBlendMode: 'screen' }}
      />
      
      {/* Neural network legend */}
      <div className="absolute top-4 right-4 bg-black/20 backdrop-blur-sm rounded-lg p-3 text-xs">
        <div className="space-y-1">
          {Object.entries(consciousnessColors).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2">
              <div 
                className="w-2 h-2 rounded-full" 
                style={{ backgroundColor: color }}
              />
              <span className="text-gray-300 capitalize">{type}</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Network statistics */}
      <div className="absolute bottom-4 left-4 bg-black/20 backdrop-blur-sm rounded-lg p-3 text-xs text-gray-300">
        <div>Nodes: {nodes.length}</div>
        <div>Connections: {connections.length}</div>
        <div>Active: {connections.filter(c => c.active).length}</div>
      </div>
    </motion.div>
  );
}
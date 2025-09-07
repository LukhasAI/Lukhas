'use client';

import { useEffect, useRef, useMemo, useCallback } from 'react';
import * as THREE from 'three';
import { createNoise3D } from 'simplex-noise';

// LUKHAS consciousness colors
const CONSCIOUSNESS_COLORS = {
  identity: '#FF6B9D',      // Pink consciousness for identity and persistence
  consciousness: '#00D4FF',  // Cyan awareness for neural patterns
  guardian: '#7C3AED',      // Purple protection for security visualization
  integration: '#FFA500',   // Orange connectivity for system interactions
  validation: '#32CD32'     // Green success for positive feedback
};

interface ConsciousnessFieldProps {
  intensity?: number;
  interactionRadius?: number;
  particleCount?: number;
  className?: string;
}

export default function ConsciousnessField({
  intensity = 1.0,
  interactionRadius = 150,
  particleCount = 2000,
  className = ''
}: ConsciousnessFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const particlesRef = useRef<THREE.Points | null>(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const animationRef = useRef<number>();
  
  // Simplex noise for organic movement
  const noise = useMemo(() => createNoise3D(), []);

  // Vertex shader for consciousness particles
  const vertexShader = `
    uniform float time;
    uniform vec2 mouse;
    uniform float intensity;
    uniform float interactionRadius;
    
    attribute float size;
    attribute vec3 color;
    attribute float consciousness;
    attribute float awareness;
    
    varying vec3 vColor;
    varying float vConsciousness;
    varying float vAwareness;
    
    void main() {
      vColor = color;
      vConsciousness = consciousness;
      vAwareness = awareness;
      
      vec3 pos = position;
      
      // Consciousness wave effect
      float wave = sin(time * 0.002 + pos.x * 0.01 + pos.y * 0.01) * intensity;
      pos.z += wave * 50.0;
      
      // Mouse interaction - particles respond to cursor
      vec2 screenPos = vec2(pos.x, pos.y);
      float dist = distance(screenPos, mouse);
      float influence = max(0.0, 1.0 - dist / interactionRadius);
      
      // Attract particles to cursor with consciousness-based response
      if (dist < interactionRadius) {
        vec2 direction = normalize(mouse - screenPos);
        pos.xy += direction * influence * 30.0 * consciousness;
        pos.z += influence * 20.0 * awareness;
      }
      
      // Neural pulse effect
      float pulse = sin(time * 0.003 + consciousness * 10.0) * 0.5 + 0.5;
      float particleSize = size * (0.8 + pulse * 0.4) * (0.5 + awareness * 0.5);
      
      vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
      gl_Position = projectionMatrix * mvPosition;
      gl_PointSize = particleSize * (300.0 / -mvPosition.z);
    }
  `;

  // Fragment shader for consciousness particles
  const fragmentShader = `
    varying vec3 vColor;
    varying float vConsciousness;
    varying float vAwareness;
    
    void main() {
      // Create soft circular particles
      vec2 center = gl_PointCoord - vec2(0.5);
      float dist = length(center);
      
      if (dist > 0.5) discard;
      
      // Soft edge with consciousness glow
      float alpha = 1.0 - smoothstep(0.2, 0.5, dist);
      
      // Consciousness intensity affects glow
      float glow = (1.0 - dist * 2.0) * vConsciousness;
      alpha = max(alpha * 0.6, glow * 0.8);
      
      // Awareness affects inner brightness
      vec3 finalColor = vColor * (0.7 + vAwareness * 0.5);
      
      gl_FragColor = vec4(finalColor, alpha);
    }
  `;

  // Initialize Three.js scene
  const initScene = useCallback(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    
    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75, 
      rect.width / rect.height, 
      0.1, 
      2000
    );
    
    const renderer = new THREE.WebGLRenderer({ 
      canvas,
      alpha: true,
      antialias: true 
    });
    renderer.setSize(rect.width, rect.height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    
    // Camera position
    camera.position.z = 500;
    
    // Create particle geometry
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    const consciousness = new Float32Array(particleCount);
    const awareness = new Float32Array(particleCount);
    
    // LUKHAS consciousness color palette
    const colorPalette = [
      new THREE.Color(CONSCIOUSNESS_COLORS.identity),
      new THREE.Color(CONSCIOUSNESS_COLORS.consciousness),
      new THREE.Color(CONSCIOUSNESS_COLORS.guardian),
      new THREE.Color(CONSCIOUSNESS_COLORS.integration),
      new THREE.Color(CONSCIOUSNESS_COLORS.validation)
    ];
    
    // Initialize particles with consciousness properties
    for (let i = 0; i < particleCount; i++) {
      // Position
      positions[i * 3] = (Math.random() - 0.5) * 1000;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 1000;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 200;
      
      // Color from consciousness palette
      const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
      
      // Particle properties
      sizes[i] = Math.random() * 3 + 1;
      consciousness[i] = Math.random(); // Consciousness level affects interaction
      awareness[i] = Math.random(); // Awareness level affects visibility
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    geometry.setAttribute('consciousness', new THREE.BufferAttribute(consciousness, 1));
    geometry.setAttribute('awareness', new THREE.BufferAttribute(awareness, 1));
    
    // Shader material
    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        mouse: { value: new THREE.Vector2(0, 0) },
        intensity: { value: intensity },
        interactionRadius: { value: interactionRadius }
      },
      vertexShader,
      fragmentShader,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    
    // Create particles
    const particles = new THREE.Points(geometry, material);
    scene.add(particles);
    
    // Store references
    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;
    particlesRef.current = particles;
    
  }, [particleCount, intensity, interactionRadius, vertexShader, fragmentShader]);

  // Animation loop
  const animate = useCallback(() => {
    if (!rendererRef.current || !sceneRef.current || !cameraRef.current || !particlesRef.current) return;
    
    const time = Date.now();
    
    // Update shader uniforms
    const material = particlesRef.current.material as THREE.ShaderMaterial;
    material.uniforms.time.value = time;
    material.uniforms.mouse.value.set(mouseRef.current.x, mouseRef.current.y);
    
    // Subtle camera movement for depth
    cameraRef.current.position.x += (mouseRef.current.x * 0.1 - cameraRef.current.position.x) * 0.02;
    cameraRef.current.position.y += (-mouseRef.current.y * 0.1 - cameraRef.current.position.y) * 0.02;
    cameraRef.current.lookAt(0, 0, 0);
    
    // Render
    rendererRef.current.render(sceneRef.current, cameraRef.current);
    
    animationRef.current = requestAnimationFrame(animate);
  }, []);

  // Mouse interaction
  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (!canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
    // Convert to screen coordinates for shader
    mouseRef.current.x *= rect.width / 2;
    mouseRef.current.y *= rect.height / 2;
  }, []);

  // Resize handler
  const handleResize = useCallback(() => {
    if (!canvasRef.current || !rendererRef.current || !cameraRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    
    cameraRef.current.aspect = rect.width / rect.height;
    cameraRef.current.updateProjectionMatrix();
    
    rendererRef.current.setSize(rect.width, rect.height);
    rendererRef.current.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  }, []);

  // Setup and cleanup
  useEffect(() => {
    initScene();
    animate();
    
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('resize', handleResize);
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      
      // Cleanup Three.js objects
      if (rendererRef.current) {
        rendererRef.current.dispose();
      }
      if (particlesRef.current) {
        particlesRef.current.geometry.dispose();
        (particlesRef.current.material as THREE.Material).dispose();
      }
    };
  }, [initScene, animate, handleMouseMove, handleResize]);

  return (
    <div className={`absolute inset-0 pointer-events-none ${className}`}>
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ mixBlendMode: 'screen' }}
      />
    </div>
  );
}
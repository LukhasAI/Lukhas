<file name=1 path=/Users/agi_dev/LOCAL-REPOS/Lukhas/advanced-morphing-visualizer.tsx>
import React, { useMemo, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { generateBaseForm, setGlyphTargetCached } from './enhanced-particle-system';

function MorphingParticles({ quotedText }) {
  const baseForm = useMemo(() => generateBaseForm(), []);
  const meshRef = useRef();

  useEffect(() => {
    if (quotedText) {
      setGlyphTargetCached(quotedText);
    }
  }, [quotedText]);

  useFrame((state, delta) => {
    if (!meshRef.current) return;
    // Animate particles towards glyph target here
    // This is a placeholder for actual morphing logic
    meshRef.current.rotation.y += delta * 0.1;
  });

  return (
    <points ref={meshRef} geometry={baseForm.geometry}>
      <pointsMaterial 
        color="#ffffff" 
        size={0.05} 
        metalness={1} 
        roughness={0} 
        blending={THREE.AdditiveBlending} 
        transparent 
      />
    </points>
  );
}

export default function AdvancedMorphingVisualizer({ quotedText }) {
  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <ambientLight intensity={0.5} />
      <MorphingParticles quotedText={quotedText} />
    </Canvas>
  );
}
</file>

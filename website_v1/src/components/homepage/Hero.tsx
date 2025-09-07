'use client';

import { Button } from '@/components/ui/Button';
import ConsciousnessParticles from '@/components/ui/ConsciousnessParticles';
import { motion, useScroll, useTransform } from 'framer-motion';

export default function Hero() {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 500], [0, -100]);
  const y2 = useTransform(scrollY, [0, 500], [0, -50]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0.8]);

  return (
    <section className="relative min-h-[100vh] flex items-center justify-center bg-[#0A0F1B] overflow-hidden">
      
      {/* Simplified background with better contrast */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0A0F1B] to-[#0A0F1B]" />
      
      <div className="container relative z-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ 
            duration: 1.2, 
            ease: [0.25, 0.1, 0.25, 1]
          }}
        >
          <motion.h1 
            className="text-8xl md:text-9xl font-thin mb-8 text-[var(--text-primary)] leading-[0.9] tracking-tight"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1.5, delay: 0.2 }}
          >
            <motion.span
              className="block"
              initial={{ x: -100, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              LUKHAS
            </motion.span>
            <motion.span 
              className="block bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] bg-clip-text text-transparent"
              initial={{ x: 100, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              AI
            </motion.span>
          </motion.h1>
          
          <motion.p 
            className="text-xl md:text-2xl text-[var(--text-secondary)] mb-12 max-w-4xl mx-auto font-light leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            Distributed cognitive architecture with 692 specialized modules.
            <br className="hidden sm:block" />
            <span className="text-accent font-normal">Agent coordination hub with multi-AI orchestration and consciousness patterns.</span>
          </motion.p>
          
          <motion.div 
            className="flex flex-col sm:flex-row gap-6 justify-center items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.0 }}
          >
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button 
                href="/studio"
                size="lg"
                className="group px-10 py-5 text-lg bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] hover:from-[var(--accent-hover)] hover:to-[var(--gradient-end)] border-0 shadow-2xl shadow-accent/25"
              >
                <span className="flex items-center gap-2">
                  Enter the Consciousness Studio
                  <motion.span
                    className="inline-block"
                    whileHover={{ x: 5 }}
                    transition={{ type: "spring", stiffness: 400, damping: 10 }}
                  >
                    →
                  </motion.span>
                </span>
              </Button>
            </motion.div>
            
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button 
                href="/vision"
                variant="secondary"
                size="lg"
                className="group px-10 py-5 text-lg border-[var(--accent)] text-[var(--accent)] hover:bg-[var(--accent)]/10 backdrop-blur-sm"
              >
                <span className="flex items-center gap-2">
                  Discover the Constellation
                  <motion.span
                    className="inline-block"
                    whileHover={{ rotate: 45 }}
                    transition={{ type: "spring", stiffness: 400, damping: 10 }}
                  >
                    ↗
                  </motion.span>
                </span>
              </Button>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
      
      {/* Decorative elements - minimal for better contrast */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-[var(--accent)]/5 rounded-full blur-3xl" />
      <div className="absolute bottom-20 right-10 w-48 h-48 bg-[var(--gradient-end)]/3 rounded-full blur-3xl" />
    </section>
  );
}
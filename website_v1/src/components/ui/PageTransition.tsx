'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { ReactNode } from 'react';

const pageVariants = {
  initial: {
    opacity: 0,
    y: 20,
    scale: 0.98
  },
  in: {
    opacity: 1,
    y: 0,
    scale: 1
  },
  out: {
    opacity: 0,
    y: -20,
    scale: 1.02
  }
};

const pageTransition = {
  type: 'tween',
  ease: [0.25, 0.1, 0.25, 1], // Custom easing curve
  duration: 0.4
};

const overlayVariants = {
  initial: {
    scaleY: 0,
    transformOrigin: 'top'
  },
  animate: {
    scaleY: 1,
    transformOrigin: 'top'
  },
  exit: {
    scaleY: 0,
    transformOrigin: 'bottom'
  }
};

export default function PageTransition({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="relative overflow-hidden">
      <AnimatePresence mode="wait">
        <motion.div
          key={pathname}
          initial="initial"
          animate="in"
          exit="out"
          variants={pageVariants}
          transition={pageTransition}
          className="min-h-screen"
        >
          {children}
        </motion.div>
      </AnimatePresence>
      
      {/* Consciousness-themed transition overlay - only shows during actual transitions */}
    </div>
  );
}
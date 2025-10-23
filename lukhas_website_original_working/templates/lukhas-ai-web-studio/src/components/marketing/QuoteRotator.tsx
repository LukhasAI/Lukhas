// components/marketing/QuoteRotator.tsx
"use client"

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

type Quote = { 
  id: string; 
  text: string; 
  signedBy?: string; 
  priority?: number; 
  untilTs?: number;
  tags?: string[];
};

interface QuoteRotatorProps {
  quotes: Quote[];
  rotateMs?: number;
  enableCharacterAnimation?: boolean;
}

export default function QuoteRotator({ 
  quotes, 
  rotateMs = 7000,
  enableCharacterAnimation = false 
}: QuoteRotatorProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState('');
  const [isAnimating, setIsAnimating] = useState(false);
  
  // Sort quotes by priority and filter by time constraints
  const sortedQuotes = quotes
    .sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0))
    .filter(q => !q.untilTs || Date.now() < q.untilTs);
  
  const activeQuote = sortedQuotes[currentIndex % sortedQuotes.length] || quotes[0];
  
  // Character-by-character animation for special quotes
  useEffect(() => {
    if (enableCharacterAnimation && activeQuote) {
      setIsAnimating(true);
      setDisplayedText('');
      
      let index = 0;
      const interval = setInterval(() => {
        if (index < activeQuote.text.length) {
          setDisplayedText(activeQuote.text.slice(0, index + 1));
          index++;
        } else {
          clearInterval(interval);
          setIsAnimating(false);
        }
      }, 80);
      
      return () => clearInterval(interval);
    } else {
      setDisplayedText(activeQuote?.text || '');
    }
  }, [activeQuote, enableCharacterAnimation]);

  // Auto-rotate quotes
  useEffect(() => {
    if (!enableCharacterAnimation && sortedQuotes.length > 1) {
      const timer = setInterval(() => {
        setCurrentIndex(prev => prev + 1);
      }, rotateMs);
      return () => clearInterval(timer);
    }
  }, [rotateMs, enableCharacterAnimation, sortedQuotes.length]);

  if (!activeQuote) return null;

  return (
    <div aria-live="polite" className="mx-auto max-w-3xl text-center text-balance">
      <AnimatePresence mode="wait">
        <motion.div
          key={activeQuote.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ 
            duration: enableCharacterAnimation ? 0.8 : 0.5,
            ease: [0.4, 0, 0.2, 1] // easeOutQuart cubic-bezier
          }}
        >
          <p className="text-2xl md:text-3xl lg:text-4xl font-light text-white leading-tight will-change-transform">
            "{displayedText}"
            {enableCharacterAnimation && isAnimating && (
              <motion.span
                className="inline-block w-1 h-8 bg-blue-400 ml-2"
                animate={{ opacity: [1, 0] }}
                transition={{ 
                  duration: 0.8, 
                  repeat: Infinity, 
                  repeatType: 'reverse' 
                }}
              />
            )}
          </p>
          {activeQuote.signedBy && (
            <motion.p 
              className="mt-4 text-lg opacity-70 text-blue-100"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.7 }}
              transition={{ delay: enableCharacterAnimation ? 2 : 0.3 }}
            >
              — {activeQuote.signedBy}
            </motion.p>
          )}
        </motion.div>
      </AnimatePresence>
      
      {/* Progress indicator for multiple quotes */}
      {sortedQuotes.length > 1 && !enableCharacterAnimation && (
        <motion.div 
          className="flex justify-center gap-2 mt-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.5 }}
          transition={{ delay: 1 }}
        >
          {sortedQuotes.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index === currentIndex % sortedQuotes.length
                  ? 'bg-blue-400 scale-125'
                  : 'bg-blue-400/30'
              }`}
            />
          ))}
        </motion.div>
      )}
    </div>
  );
}

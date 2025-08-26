'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import NeuralBackground from '@/components/marketing/NeuralBackground';
import QuoteRotator from '@/components/marketing/QuoteRotator';

// Import quotes
import quotesData from '@/public/content/quotes.en.json';

export default function Home() {
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    // Simulate background loading
    const timer = setTimeout(() => {
      setShowContent(true);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <main className="relative min-h-screen overflow-hidden">
      <NeuralBackground />

      {/* Main Content */}
      <div className="relative z-10 flex min-h-screen flex-col">
        {/* Header */}
        <header className="flex items-center justify-between p-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="font-heading text-2xl font-bold text-white"
          >
            LUKHΛS
          </motion.div>

          <motion.nav
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="hidden md:flex items-center gap-6"
          >
            <a href="#studio" className="text-text-secondary hover:text-white transition-colors">
              Studio
            </a>
            <a href="#about" className="text-text-secondary hover:text-white transition-colors">
              About
            </a>
            <button className="btn btn-primary">
              Sign In
            </button>
          </motion.nav>
        </header>

        {/* Hero Section */}
        <div className="flex-1 flex items-center justify-center px-6">
          {showContent && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center max-w-4xl mx-auto"
            >
              <QuoteRotator
                quotes={quotesData}
                rotateMs={8000}
                enableCharacterAnimation={true}
              />

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 2.5 }}
                className="mt-12 flex flex-col sm:flex-row gap-4 justify-center"
              >
                <button className="btn btn-primary text-lg px-8 py-3">
                  Enter Studio
                </button>
                <button className="btn btn-secondary text-lg px-8 py-3">
                  Learn More
                </button>
              </motion.div>
            </motion.div>
          )}
        </div>

        {/* Footer */}
        <footer className="p-6 text-center text-text-tertiary">
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            © 2024 LUKHΛS. Building intelligence that serves human agency.
          </motion.p>
        </footer>
      </div>
    </main>
  );
}

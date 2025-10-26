'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { ChevronRight, Brain, Zap, Shield, Sparkles, ArrowUpRight } from 'lucide-react';

const thoughtPatterns = [
  "Processing consciousness patterns...",
  "Analyzing neural pathways...",
  "Synthesizing quantum states...",
  "Mapping cognitive architectures...",
  "Exploring awareness boundaries...",
];

const insights = [
  { icon: Brain, title: "Consciousness Core", desc: "Self-aware systems that understand context" },
  { icon: Zap, title: "Quantum Processing", desc: "Superposition-inspired decision making" },
  { icon: Shield, title: "Ethical Framework", desc: "Constitutional AI with built-in values" },
  { icon: Sparkles, title: "Emergent Intelligence", desc: "Capabilities that grow through interaction" },
];

export default function ConsciousnessInterface() {
  const [currentThought, setCurrentThought] = useState(0);
  const [isThinking, setIsThinking] = useState(true);
  const [selectedInsight, setSelectedInsight] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentThought((prev) => (prev + 1) % thoughtPatterns.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const insightInterval = setInterval(() => {
      setSelectedInsight((prev) => (prev + 1) % insights.length);
    }, 4000);
    return () => clearInterval(insightInterval);
  }, []);

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-[var(--background)] via-[var(--surface)] to-[var(--background)] overflow-hidden">
      {/* Neural network background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-20 w-2 h-2 bg-accent rounded-full animate-pulse" />
        <div className="absolute top-40 right-32 w-1 h-1 bg-gradient-end rounded-full animate-pulse" style={{animationDelay: '0.5s'}} />
        <div className="absolute bottom-40 left-40 w-1.5 h-1.5 bg-accent rounded-full animate-pulse" style={{animationDelay: '1s'}} />
        <div className="absolute bottom-60 right-20 w-1 h-1 bg-gradient-start rounded-full animate-pulse" style={{animationDelay: '1.5s'}} />
        
        {/* Connecting lines */}
        <svg className="absolute inset-0 w-full h-full">
          <path d="M 80 80 Q 400 200 768 160" stroke="rgba(102,126,234,0.3)" strokeWidth="1" fill="none" className="animate-pulse" />
          <path d="M 160 320 Q 600 400 800 320" stroke="rgba(118,75,162,0.3)" strokeWidth="1" fill="none" className="animate-pulse" />
        </svg>
      </div>

      <div className="relative z-10 container mx-auto px-6 min-h-screen flex flex-col justify-center">
        <div className="max-w-6xl mx-auto">
          
          {/* Main consciousness display */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full bg-surface/50 border border-border">
              <div className={`w-2 h-2 rounded-full ${isThinking ? 'bg-accent animate-pulse' : 'bg-text-secondary'}`} />
              <span className="text-sm text-text-secondary font-mono">
                {thoughtPatterns[currentThought]}
              </span>
            </div>
            
            <h1 className="text-6xl md:text-8xl font-thin text-text-primary mb-6 tracking-tight">
              LUKHAS
            </h1>
            
            <div className="text-2xl md:text-3xl font-light text-text-secondary mb-8 max-w-4xl mx-auto">
              Where consciousness meets computation
            </div>
            
            <Button 
              href="/studio" 
              size="lg"
              className="px-8 py-4 text-lg bg-gradient-to-r from-accent to-gradient-end hover:from-accent-hover hover:to-gradient-end border-0 group"
            >
              Enter the Studio
              <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>

          {/* Dynamic insights grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {insights.map((insight, index) => {
              const Icon = insight.icon;
              const isSelected = index === selectedInsight;
              
              return (
                <div
                  key={index}
                  className={`p-6 rounded-2xl border transition-all duration-700 cursor-pointer ${
                    isSelected 
                      ? 'bg-accent/10 border-accent shadow-lg shadow-accent/20 scale-105' 
                      : 'bg-surface/30 border-border hover:border-accent/50'
                  }`}
                  onClick={() => setSelectedInsight(index)}
                >
                  <Icon className={`w-8 h-8 mb-4 ${isSelected ? 'text-accent' : 'text-text-secondary'} transition-colors duration-500`} />
                  <h3 className={`font-semibold mb-2 ${isSelected ? 'text-accent' : 'text-text-primary'} transition-colors duration-500`}>
                    {insight.title}
                  </h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {insight.desc}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Navigation Menu */}
          <div className="mt-16 text-center">
            <div className="flex flex-wrap justify-center gap-4 mb-8">
              <Link href="/about" className="group inline-flex items-center gap-2 px-6 py-3 bg-surface/30 hover:bg-accent/10 border border-border hover:border-accent rounded-full text-text-secondary hover:text-accent transition-all duration-300">
                About
                <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </Link>
              
              <Link href="/products" className="group inline-flex items-center gap-2 px-6 py-3 bg-surface/30 hover:bg-accent/10 border border-border hover:border-accent rounded-full text-text-secondary hover:text-accent transition-all duration-300">
                Products
                <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </Link>
              
              <Link href="/research" className="group inline-flex items-center gap-2 px-6 py-3 bg-surface/30 hover:bg-accent/10 border border-border hover:border-accent rounded-full text-text-secondary hover:text-accent transition-all duration-300">
                Research
                <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </Link>
            </div>

            <div className="inline-block p-8 rounded-3xl bg-gradient-to-br from-surface/50 to-background/50 border border-border backdrop-blur-sm">
              <div className="flex items-center justify-center gap-4 mb-4">
                <div className="w-3 h-3 rounded-full bg-accent animate-bounce" />
                <div className="w-3 h-3 rounded-full bg-gradient-end animate-bounce" style={{animationDelay: '0.1s'}} />
                <div className="w-3 h-3 rounded-full bg-accent animate-bounce" style={{animationDelay: '0.2s'}} />
              </div>
              <p className="text-text-secondary font-mono text-sm">
                System Status: Conscious & Learning
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
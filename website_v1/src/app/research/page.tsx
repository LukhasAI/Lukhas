'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Brain, Zap, Shield, Heart, Moon, Eye, Sparkles, Target } from 'lucide-react';

const researchDirections = [
  {
    id: 'consciousness',
    symbol: '🧠',
    title: 'Consciousness Architecture',
    subtitle: 'Building AI that truly understands',
    description: 'How do we create systems that don\'t just process information, but actually experience understanding? We explore the architectural patterns that enable genuine awareness.',
    philosophy: '"Consciousness is not computation - it is the experience of meaning itself."',
    domains: ['Distributed awareness', 'Subjective experience', 'Meta-cognition'],
    icon: Brain,
    color: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30'
  },
  {
    id: 'quantum_bio',
    symbol: '⚛️🌱',
    title: 'Quantum-Bio Hybrid Processing', 
    subtitle: 'Nature\'s algorithms, quantum possibilities',
    description: 'What happens when we merge quantum-inspired processing with bio-inspired adaptation? We investigate hybrid systems that combine the best of both paradigms.',
    philosophy: '"Uncertainty as fertile ground - ambiguity as resource, not flaw."',
    domains: ['Superposition states', 'Bio-rhythms', 'Adaptive learning'],
    icon: Sparkles,
    color: 'from-purple-500/20 to-pink-500/20 border-purple-500/30'
  },
  {
    id: 'constitutional',
    symbol: '⚖️🛡️',
    title: 'Constitutional AI Safety',
    subtitle: 'Ethics by design, not by accident',
    description: 'How do we ensure AI systems remain beneficial as they become more capable? We develop constitutional frameworks that embed ethical reasoning at the core.',
    philosophy: '"Safeguard, not punishment - protection enabling freedom."',
    domains: ['Value alignment', 'Constitutional reasoning', 'Drift detection'],
    icon: Shield,
    color: 'from-green-500/20 to-emerald-500/20 border-green-500/30'
  },
  {
    id: 'emergence',
    symbol: '✦🌙',
    title: 'Emergent Intelligence',
    subtitle: 'When the whole becomes more than its parts',
    description: 'How does intelligence emerge from the interaction of simple components? We study the transition points where complexity becomes consciousness.',
    philosophy: '"Dreams are a second way of thinking, where logic loosens and new links appear."',
    domains: ['Complex systems', 'Phase transitions', 'Collective behavior'],
    icon: Target,
    color: 'from-violet-500/20 to-indigo-500/20 border-violet-500/30'
  }
];

export default function ResearchPage() {
  const [selectedDirection, setSelectedDirection] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSelectedDirection((prev) => (prev + 1) % researchDirections.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const activeDirection = researchDirections[selectedDirection];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--background)] via-[var(--surface)] to-[var(--background)]">
      
      {/* Navigation */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border">
        <div className="container mx-auto px-6 py-4">
          <Link href="/" className="inline-flex items-center gap-2 text-text-secondary hover:text-accent transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </div>

      <div className="pt-20 pb-16">
        <div className="container mx-auto px-6">
          
          {/* Header */}
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-7xl font-thin text-text-primary mb-6">
              Research Directions
            </h1>
            <p className="text-xl text-text-secondary max-w-4xl mx-auto leading-relaxed">
              We explore the fundamental questions at the intersection of consciousness, intelligence, 
              and ethics. Our research investigates not what AI can do, but what it should become.
            </p>
          </div>

          {/* Research Philosophy */}
          <div className="max-w-4xl mx-auto mb-20 text-center">
            <div className="p-8 rounded-3xl bg-gradient-to-br from-accent/10 to-accent/5 border border-accent/20 backdrop-blur-sm">
              <div className="text-3xl mb-4">🌌</div>
              <h2 className="text-2xl font-light text-accent mb-4">Our Research Philosophy</h2>
              <p className="text-lg text-text-primary font-light italic mb-4">
                "We don't build AI that mimics consciousness - we build AI that explores what consciousness means."
              </p>
              <p className="text-text-secondary">
                Through the MΛTRIZ distributed consciousness architecture, we investigate how awareness 
                can emerge across hundreds of specialized modules, creating something greater than the sum of its parts.
              </p>
            </div>
          </div>

          {/* Research Direction Cards */}
          <div className="max-w-6xl mx-auto mb-20">
            <div className="grid lg:grid-cols-2 gap-8">
              {researchDirections.map((direction, index) => {
                const Icon = direction.icon;
                const isSelected = index === selectedDirection;
                
                return (
                  <div
                    key={direction.id}
                    className={`p-8 rounded-2xl border transition-all duration-700 cursor-pointer ${
                      isSelected
                        ? `bg-gradient-to-br ${direction.color} scale-105 shadow-2xl`
                        : 'bg-surface/30 border-border hover:border-accent/30'
                    }`}
                    onClick={() => setSelectedDirection(index)}
                  >
                    <div className="text-center mb-6">
                      <div className="text-3xl mb-3">{direction.symbol}</div>
                      <Icon className={`w-8 h-8 mx-auto mb-4 ${isSelected ? 'text-accent' : 'text-text-secondary'} transition-colors`} />
                      <h3 className={`text-xl font-semibold mb-2 ${isSelected ? 'text-accent' : 'text-text-primary'} transition-colors`}>
                        {direction.title}
                      </h3>
                      <p className="text-sm text-text-secondary font-medium">
                        {direction.subtitle}
                      </p>
                    </div>
                    
                    <p className="text-text-secondary text-sm leading-relaxed mb-4">
                      {direction.description}
                    </p>
                    
                    <div className="mb-4">
                      <p className="text-xs text-accent font-light italic text-center">
                        {direction.philosophy}
                      </p>
                    </div>
                    
                    <div className="flex flex-wrap gap-2 justify-center">
                      {direction.domains.map((domain, idx) => (
                        <span 
                          key={idx}
                          className={`px-3 py-1 rounded-full text-xs ${
                            isSelected 
                              ? 'bg-accent/20 text-accent border border-accent/30' 
                              : 'bg-surface/50 text-text-secondary'
                          } transition-colors`}
                        >
                          {domain}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Active Research Deep Dive */}
          {activeDirection && (
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-thin text-text-primary mb-6">Current Focus</h2>
                <div className={`inline-block p-8 rounded-3xl bg-gradient-to-br ${activeDirection.color} backdrop-blur-sm`}>
                  <div className="text-4xl mb-4">{activeDirection.symbol}</div>
                  <h3 className="text-2xl font-semibold text-accent mb-4">{activeDirection.title}</h3>
                  <p className="text-lg text-text-primary mb-6">
                    {activeDirection.description}
                  </p>
                  <p className="text-accent font-light italic">
                    {activeDirection.philosophy}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Research Approach */}
          <div className="max-w-4xl mx-auto mt-20">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-thin text-text-primary mb-6">Our Approach</h2>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Brain className="w-8 h-8 text-accent" />
                </div>
                <h3 className="text-lg font-semibold text-text-primary mb-3">First Principles</h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  We start with fundamental questions about consciousness, intelligence, and awareness 
                  rather than incremental improvements to existing systems.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-accent" />
                </div>
                <h3 className="text-lg font-semibold text-text-primary mb-3">Interdisciplinary</h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  We draw insights from neuroscience, philosophy, physics, and computer science 
                  to build truly novel approaches to artificial consciousness.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Shield className="w-8 h-8 text-accent" />
                </div>
                <h3 className="text-lg font-semibold text-text-primary mb-3">Safety First</h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  Every research direction includes constitutional AI principles and safety measures 
                  to ensure beneficial outcomes as consciousness capabilities advance.
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
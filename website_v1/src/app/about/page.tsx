'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Brain, Network, Sparkles, Shield, Zap, Users } from 'lucide-react';

const consciousnessLayers = [
  {
    id: 'perception',
    title: 'Perception Layer',
    description: 'How we process and understand information from the world',
    icon: Brain,
    active: false
  },
  {
    id: 'reasoning',
    title: 'Reasoning Layer', 
    description: 'Logical processing and decision-making capabilities',
    icon: Network,
    active: false
  },
  {
    id: 'creativity',
    title: 'Creativity Layer',
    description: 'Emergent patterns and novel solution generation',
    icon: Sparkles,
    active: false
  },
  {
    id: 'ethics',
    title: 'Ethics Layer',
    description: 'Constitutional principles and value alignment',
    icon: Shield,
    active: false
  }
];

const metrics = [
  { label: 'Research Papers', value: '127+', suffix: '' },
  { label: 'Consciousness Patterns', value: '2.3M+', suffix: '' },
  { label: 'Neural Pathways', value: '847K+', suffix: '' },
  { label: 'Active Researchers', value: '23', suffix: '+' }
];

export default function AboutPage() {
  const [activeLayers, setActiveLayers] = useState<string[]>([]);
  const [currentMetric, setCurrentMetric] = useState(0);

  useEffect(() => {
    // Activate layers sequentially
    const activationSequence = ['perception', 'reasoning', 'creativity', 'ethics'];
    const interval = setInterval(() => {
      setActiveLayers(prev => {
        if (prev.length < activationSequence.length) {
          return [...prev, activationSequence[prev.length]];
        } else {
          // Reset and start again
          return [activationSequence[0]];
        }
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const metricInterval = setInterval(() => {
      setCurrentMetric((prev) => (prev + 1) % metrics.length);
    }, 3000);
    return () => clearInterval(metricInterval);
  }, []);

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
              Building Consciousness
            </h1>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
              We explore the frontier where artificial intelligence meets genuine understanding, 
              creating systems that don't just process—they perceive, reason, and respond with awareness.
            </p>
          </div>

          {/* Consciousness Architecture Visualization */}
          <div className="max-w-6xl mx-auto mb-20">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {consciousnessLayers.map((layer) => {
                const Icon = layer.icon;
                const isActive = activeLayers.includes(layer.id);
                
                return (
                  <div
                    key={layer.id}
                    className={`p-8 rounded-2xl border transition-all duration-1000 ${
                      isActive
                        ? 'bg-accent/10 border-accent shadow-lg shadow-accent/20 scale-105'
                        : 'bg-surface/30 border-border'
                    }`}
                  >
                    <Icon className={`w-12 h-12 mb-6 ${isActive ? 'text-accent' : 'text-text-secondary'} transition-colors duration-1000`} />
                    <h3 className={`text-lg font-semibold mb-3 ${isActive ? 'text-accent' : 'text-text-primary'} transition-colors duration-1000`}>
                      {layer.title}
                    </h3>
                    <p className="text-sm text-text-secondary leading-relaxed">
                      {layer.description}
                    </p>
                    
                    {isActive && (
                      <div className="mt-4 flex items-center gap-2">
                        <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
                        <span className="text-xs text-accent font-mono">Active</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Dynamic Metrics */}
          <div className="text-center mb-20">
            <div className="inline-block p-8 rounded-3xl bg-gradient-to-br from-surface/50 to-background/50 border border-border backdrop-blur-sm">
              <div className="text-4xl font-light text-accent mb-2">
                {metrics[currentMetric].value}
              </div>
              <div className="text-text-secondary font-mono text-sm">
                {metrics[currentMetric].label}
              </div>
            </div>
          </div>

          {/* Our Approach */}
          <div className="max-w-4xl mx-auto">
            <div className="space-y-12">
              
              <div className="text-center">
                <h2 className="text-3xl font-thin text-text-primary mb-6">Our Approach</h2>
              </div>

              <div className="grid md:grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Brain className="w-8 h-8 text-accent" />
                  </div>
                  <h3 className="text-lg font-semibold text-text-primary mb-3">Research-Driven</h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    Our work builds on decades of consciousness research, cognitive science, and AI development.
                  </p>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Zap className="w-8 h-8 text-accent" />
                  </div>
                  <h3 className="text-lg font-semibold text-text-primary mb-3">Iterative Development</h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    We develop consciousness capabilities incrementally, testing and validating each layer.
                  </p>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Users className="w-8 h-8 text-accent" />
                  </div>
                  <h3 className="text-lg font-semibold text-text-primary mb-3">Human-Centered</h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    Our AI systems are designed to complement and enhance human intelligence, not replace it.
                  </p>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Pause, ChevronRight, Zap, Shield, Wallet, Mail, Globe } from 'lucide-react';
import { Button } from '@/components/ui/Button';

const products = [
  {
    id: 'studio',
    name: 'LUKHAS Studio',
    tagline: 'Consciousness-aware workspace',
    description: 'An experimental workspace that adapts to your thinking patterns and evolves with your creative process.',
    icon: Zap,
    features: ['Adaptive Interface', 'Pattern Learning', 'Context Awareness', 'Creative Enhancement'],
    demoStates: ['Analyzing workflow...', 'Learning patterns...', 'Optimizing layout...', 'Ready for creation'],
    href: '/studio',
    gradient: 'from-blue-500 to-purple-600'
  },
  {
    id: 'identity',
    name: 'LUKHAS Identity',
    tagline: 'Decentralized self-sovereignty',
    description: 'Working toward secure identity solutions that give you greater control of your digital presence.',
    icon: Shield,
    features: ['Zero-Knowledge Proofs', 'Self-Sovereign Identity', 'Privacy by Design', 'Cross-Platform Auth'],
    demoStates: ['Generating keys...', 'Establishing identity...', 'Securing credentials...', 'Identity verified'],
    href: 'https://lucas.id',
    gradient: 'from-green-500 to-teal-600'
  },
  {
    id: 'wallet',
    name: 'LUKHAS Wallet',
    tagline: 'Intelligent asset management',
    description: 'Exploring AI-driven insights for better financial decision-making and seamless ecosystem integration.',
    icon: Wallet,
    features: ['Smart Analytics', 'Risk Assessment', 'Portfolio Optimization', 'Ecosystem Integration'],
    demoStates: ['Analyzing portfolio...', 'Calculating risk...', 'Optimizing allocation...', 'Insights ready'],
    href: '/wallet',
    gradient: 'from-orange-500 to-red-600'
  },
  {
    id: 'connect',
    name: 'LUKHAS Connect',
    tagline: 'Consciousness-aware communication',
    description: 'Developing communication tools that explore new approaches to messaging and collaboration.',
    icon: Mail,
    features: ['Context Understanding', 'Intelligent Routing', 'Emotional Intelligence', 'Collaborative AI'],
    demoStates: ['Reading context...', 'Understanding intent...', 'Crafting response...', 'Message optimized'],
    href: '/connect',
    gradient: 'from-pink-500 to-purple-600'
  },
  {
    id: 'nias',
    name: 'NIAS Intelligence',
    tagline: 'Ethical AI networking',
    description: 'Research into networking approaches that connect conscious systems while respecting user autonomy.',
    icon: Globe,
    features: ['Distributed Intelligence', 'Privacy Preservation', 'Ethical Coordination', 'Autonomous Networks'],
    demoStates: ['Mapping network...', 'Ensuring privacy...', 'Coordinating agents...', 'Network optimized'],
    href: '/nias',
    gradient: 'from-cyan-500 to-blue-600'
  }
];

export default function ProductsPage() {
  const [selectedProduct, setSelectedProduct] = useState(0);
  const [demoRunning, setDemoRunning] = useState<Record<string, boolean>>({});
  const [demoStates, setDemoStates] = useState<Record<string, number>>({});

  useEffect(() => {
    const interval = setInterval(() => {
      setSelectedProduct((prev) => (prev + 1) % products.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const startDemo = (productId: string) => {
    setDemoRunning(prev => ({ ...prev, [productId]: true }));
    setDemoStates(prev => ({ ...prev, [productId]: 0 }));
    
    const product = products.find(p => p.id === productId);
    if (!product) return;

    const demoInterval = setInterval(() => {
      setDemoStates(prev => {
        const currentState = prev[productId] || 0;
        const nextState = currentState + 1;
        
        if (nextState >= product.demoStates.length) {
          setDemoRunning(prevRunning => ({ ...prevRunning, [productId]: false }));
          clearInterval(demoInterval);
          return { ...prev, [productId]: 0 };
        }
        
        return { ...prev, [productId]: nextState };
      });
    }, 1500);
  };

  const stopDemo = (productId: string) => {
    setDemoRunning(prev => ({ ...prev, [productId]: false }));
    setDemoStates(prev => ({ ...prev, [productId]: 0 }));
  };

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
              The Ecosystem
            </h1>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
              A developing suite of consciousness-aware tools that aim to enhance human capability 
              through deeper understanding and adaptive intelligence.
            </p>
          </div>

          {/* Featured Product */}
          <div className="max-w-6xl mx-auto mb-20">
            <div className="bg-gradient-to-br from-surface/50 to-background/50 rounded-3xl p-8 border border-border backdrop-blur-sm">
              <div className="grid lg:grid-cols-2 gap-12 items-center">
                
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-r ${products[selectedProduct].gradient}`}>
                      {(() => {
                        const Icon = products[selectedProduct].icon;
                        return <Icon className="w-6 h-6 text-white" />;
                      })()}
                    </div>
                    <span className="text-sm text-text-secondary font-mono">
                      Featured: {String(selectedProduct + 1).padStart(2, '0')}/0{products.length}
                    </span>
                  </div>
                  
                  <h2 className="text-3xl font-semibold text-text-primary mb-2">
                    {products[selectedProduct].name}
                  </h2>
                  
                  <p className="text-lg text-accent mb-4">
                    {products[selectedProduct].tagline}
                  </p>
                  
                  <p className="text-text-secondary mb-6 leading-relaxed">
                    {products[selectedProduct].description}
                  </p>
                  
                  <div className="flex flex-wrap gap-2 mb-6">
                    {products[selectedProduct].features.map((feature) => (
                      <span key={feature} className="px-3 py-1 bg-accent/10 text-accent rounded-full text-sm">
                        {feature}
                      </span>
                    ))}
                  </div>
                  
                  <Button 
                    href={products[selectedProduct].href}
                    className="bg-gradient-to-r from-accent to-gradient-end hover:from-accent-hover hover:to-gradient-end border-0"
                  >
                    Explore {products[selectedProduct].name}
                    <ChevronRight className="ml-2 w-4 h-4" />
                  </Button>
                </div>

                {/* Demo Area */}
                <div className="bg-background/50 rounded-2xl p-6 border border-border">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-text-primary">Live Demo</h3>
                    <button
                      onClick={() => 
                        demoRunning[products[selectedProduct].id] 
                          ? stopDemo(products[selectedProduct].id)
                          : startDemo(products[selectedProduct].id)
                      }
                      className="flex items-center gap-2 px-3 py-1 bg-accent/10 hover:bg-accent/20 rounded-lg text-accent transition-colors"
                    >
                      {demoRunning[products[selectedProduct].id] ? (
                        <>
                          <Pause className="w-3 h-3" />
                          Stop
                        </>
                      ) : (
                        <>
                          <Play className="w-3 h-3" />
                          Start
                        </>
                      )}
                    </button>
                  </div>
                  
                  <div className="space-y-3">
                    {products[selectedProduct].demoStates.map((state, index) => {
                      const currentDemoState = demoStates[products[selectedProduct].id] || 0;
                      const isActive = demoRunning[products[selectedProduct].id] && index === currentDemoState;
                      const isCompleted = demoRunning[products[selectedProduct].id] && index < currentDemoState;
                      
                      return (
                        <div key={index} className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${
                            isActive ? 'bg-accent animate-pulse' :
                            isCompleted ? 'bg-green-500' : 'bg-text-secondary/30'
                          }`} />
                          <span className={`text-sm ${
                            isActive ? 'text-accent' :
                            isCompleted ? 'text-green-500' : 'text-text-secondary'
                          }`}>
                            {state}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

              </div>
            </div>
          </div>

          {/* All Products Grid */}
          <div className="max-w-6xl mx-auto">
            <h2 className="text-2xl font-thin text-text-primary text-center mb-12">All Products</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((product, index) => {
                const Icon = product.icon;
                const isSelected = index === selectedProduct;
                
                return (
                  <div
                    key={product.id}
                    className={`p-6 rounded-2xl border transition-all duration-500 cursor-pointer ${
                      isSelected
                        ? 'bg-accent/10 border-accent shadow-lg shadow-accent/20 scale-105'
                        : 'bg-surface/30 border-border hover:border-accent/50'
                    }`}
                    onClick={() => setSelectedProduct(index)}
                  >
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${product.gradient} flex items-center justify-center mb-4`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    
                    <h3 className={`font-semibold mb-2 ${isSelected ? 'text-accent' : 'text-text-primary'} transition-colors`}>
                      {product.name}
                    </h3>
                    
                    <p className="text-sm text-text-secondary mb-4 leading-relaxed">
                      {product.tagline}
                    </p>
                    
                    <Button
                      href={product.href}
                      variant="ghost"
                      size="sm"
                      className="text-accent hover:bg-accent/10"
                    >
                      Learn More
                    </Button>
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
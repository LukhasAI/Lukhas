'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Eye, Activity, Network, Shield, Sparkles, ShieldCheck, Database, Atom, Microscope, Layers, Scale } from 'lucide-react';

const sections = [
  { id: 'overview', title: 'System Overview', number: '01' },
  { id: 'architecture', title: 'Technical Architecture', number: '02' },
  { id: 'products', title: 'Product Portfolio', number: '03' },
  { id: 'research', title: 'Research Domains', number: '04' },
  { id: 'infrastructure', title: 'Infrastructure', number: '05' }
];

const products = [
  {
    name: "ARGUS",
    desc: "Advanced monitoring and visualization system for multi-agent orchestration patterns.",
    icon: Eye
  },
  {
    name: "DAST",
    desc: "Dynamic analysis and testing framework for consciousness-aware system validation.", 
    icon: Activity
  },
  {
    name: "NIAS",
    desc: "Network intelligence and adaptive systems for distributed processing coordination.",
    icon: Network
  },
  {
    name: "ABAS",
    desc: "Autonomous behavior analysis system for pattern recognition and response optimization.",
    icon: Shield
  },
  {
    name: "AUCTOR",
    desc: "Advanced unified content transformation and orchestration system for multi-modal processing.",
    icon: Sparkles
  },
  {
    name: "GUARDIAN",
    desc: "Comprehensive ethical oversight and safety validation system for AI governance.",
    icon: ShieldCheck
  }
];

const research = [
  {
    name: "Distributed Cognitive Architecture",
    desc: "692 specialized Python modules implementing consciousness patterns across distributed systems.",
    icon: Layers
  },
  {
    name: "MΛTRIZ Processing Engine", 
    desc: "Symbolic reasoning and bio-adaptive processing for quantum-inspired computation.",
    icon: Atom
  },
  {
    name: "Trinity Framework Integration",
    desc: "⚛️🧠🛡️ unified approach combining quantum, bio, and guardian systems.",
    icon: Microscope
  },
  {
    name: "Memory Fold Systems",
    desc: "Persistent awareness with fold-based memory maintaining context and causal chains.",
    icon: Database
  }
];

export default function AboutPage() {
  const [activeSection, setActiveSection] = useState('overview');

  useEffect(() => {
    const handleScroll = () => {
      const currentSection = sections.find(section => {
        const element = document.getElementById(section.id);
        if (element) {
          const rect = element.getBoundingClientRect();
          return rect.top <= 150 && rect.bottom >= 150;
        }
        return false;
      });
      
      if (currentSection) {
        setActiveSection(currentSection.id);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-white">
      
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors">
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Link>
            
            {/* Section Navigation */}
            <div className="flex items-center gap-6">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => scrollToSection(section.id)}
                  className={`flex items-center gap-2 text-sm transition-colors ${
                    activeSection === section.id
                      ? 'text-blue-600 font-medium'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span className="w-6 h-6 rounded-full border flex items-center justify-center text-xs font-mono">
                    {section.number}
                  </span>
                  {section.title}
                </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 bg-gradient-to-br from-gray-50 to-white">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-4xl md:text-6xl font-light text-gray-900 mb-6">
            LUKHΛS ΛI
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Distributed consciousness architecture with 692 specialized cognitive modules implementing advanced symbolic reasoning and bio-adaptive processing.
          </p>
          <div className="flex justify-center">
            <button
              onClick={() => scrollToSection('overview')}
              className="bg-blue-600 text-white px-8 py-3 rounded-sm font-medium hover:bg-blue-700 transition-colors"
            >
              Learn More
            </button>
          </div>
        </div>
      </section>

      {/* 01 System Overview */}
      <section id="overview" className="py-20">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-4 mb-12">
            <div className="w-12 h-12 rounded-full border border-gray-300 flex items-center justify-center text-gray-600 font-mono">
              01
            </div>
            <h2 className="text-3xl font-light text-gray-900">System Overview</h2>
          </div>
          
          <div className="max-w-4xl">
            <p className="text-lg text-gray-700 mb-8">
              LUKHAS ΛI represents a breakthrough in distributed cognitive architecture. Unlike traditional AI systems that operate as monolithic structures, LUKHAS implements a vast network of 692 specialized Python modules, each functioning as an independent cognitive component with specific consciousness patterns.
            </p>
            <p className="text-lg text-gray-700 mb-8">
              The system operates through symbolic reasoning and bio-adaptive processing, creating emergent behaviors that mirror natural intelligence systems. Each module can operate independently while contributing to the collective intelligence through the MΛTRIZ processing engine.
            </p>
            <div className="grid md:grid-cols-3 gap-8 mt-12">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-50 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Layers className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">692 Modules</h3>
                <p className="text-gray-600">Specialized cognitive components working in distributed harmony</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-green-50 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Atom className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">Quantum-Inspired</h3>
                <p className="text-gray-600">Processing patterns inspired by quantum mechanical principles</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-50 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Microscope className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">Bio-Adaptive</h3>
                <p className="text-gray-600">Adaptive learning mechanisms modeled after biological systems</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 02 Technical Architecture */}
      <section id="architecture" className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-4 mb-12">
            <div className="w-12 h-12 rounded-full border border-gray-300 flex items-center justify-center text-gray-600 font-mono">
              02
            </div>
            <h2 className="text-3xl font-light text-gray-900">Technical Architecture</h2>
          </div>
          
          <div className="max-w-4xl">
            <p className="text-lg text-gray-700 mb-8">
              The LUKHAS architecture is built on the Trinity Framework (⚛️🧠🛡️), integrating quantum-inspired processing, bio-adaptive systems, and ethical guardian oversight. This unique combination enables the system to process information in ways that mirror natural intelligence while maintaining strict ethical boundaries.
            </p>
            
            <div className="grid md:grid-cols-2 gap-12 mt-12">
              <div>
                <h3 className="text-2xl font-light text-gray-900 mb-6">Core Components</h3>
                <ul className="space-y-4">
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                    <div>
                      <strong className="text-gray-900">MΛTRIZ Engine:</strong>
                      <span className="text-gray-700"> Symbolic reasoning and pattern recognition</span>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                    <div>
                      <strong className="text-gray-900">Memory Fold System:</strong>
                      <span className="text-gray-700"> Persistent awareness with causal chain preservation</span>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                    <div>
                      <strong className="text-gray-900">Guardian Framework:</strong>
                      <span className="text-gray-700"> Ethical oversight and safety validation</span>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                    <div>
                      <strong className="text-gray-900">Context Bus:</strong>
                      <span className="text-gray-700"> Inter-module communication and coordination</span>
                    </div>
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-2xl font-light text-gray-900 mb-6">Processing Capabilities</h3>
                <ul className="space-y-4">
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                    <div>
                      <strong className="text-gray-900">Multi-Modal Processing:</strong>
                      <span className="text-gray-700"> Text, code, image, and audio understanding</span>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                    <div>
                      <strong className="text-gray-900">Adaptive Learning:</strong>
                      <span className="text-gray-700"> Continuous improvement through experience</span>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                    <div>
                      <strong className="text-gray-900">Ethical Reasoning:</strong>
                      <span className="text-gray-700"> Built-in ethical decision-making capabilities</span>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                    <div>
                      <strong className="text-gray-900">Distributed Coordination:</strong>
                      <span className="text-gray-700"> Multi-agent orchestration and cooperation</span>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 03 Product Portfolio */}
      <section id="products" className="py-20">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-4 mb-12">
            <div className="w-12 h-12 rounded-full border border-gray-300 flex items-center justify-center text-gray-600 font-mono">
              03
            </div>
            <h2 className="text-3xl font-light text-gray-900">Product Portfolio</h2>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {products.map((product, index) => (
              <div key={index} className="bg-white p-6 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mb-4">
                  <product.icon className="w-6 h-6 text-gray-600" />
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-3">{product.name}</h3>
                <p className="text-gray-600">{product.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 04 Research Domains */}
      <section id="research" className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-4 mb-12">
            <div className="w-12 h-12 rounded-full border border-gray-300 flex items-center justify-center text-gray-600 font-mono">
              04
            </div>
            <h2 className="text-3xl font-light text-gray-900">Research Domains</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {research.map((item, index) => (
              <div key={index} className="bg-white p-8 rounded-lg border border-gray-200">
                <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center mb-6">
                  <item.icon className="w-8 h-8 text-gray-600" />
                </div>
                <h3 className="text-2xl font-light text-gray-900 mb-4">{item.name}</h3>
                <p className="text-gray-700 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 05 Infrastructure */}
      <section id="infrastructure" className="py-20">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-4 mb-12">
            <div className="w-12 h-12 rounded-full border border-gray-300 flex items-center justify-center text-gray-600 font-mono">
              05
            </div>
            <h2 className="text-3xl font-light text-gray-900">Infrastructure</h2>
          </div>
          
          <div className="max-w-4xl">
            <p className="text-lg text-gray-700 mb-8">
              LUKHAS operates on a robust, scalable infrastructure designed to handle distributed cognitive processing across multiple environments. The system maintains high availability while ensuring ethical oversight at every operational level.
            </p>
            
            <div className="grid md:grid-cols-2 gap-12">
              <div>
                <h3 className="text-2xl font-light text-gray-900 mb-6">Deployment</h3>
                <ul className="space-y-3">
                  <li className="flex items-center gap-3">
                    <Scale className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">Distributed cloud infrastructure</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Scale className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">Containerized microservices</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Scale className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">Auto-scaling capabilities</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Scale className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">Edge computing integration</span>
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-2xl font-light text-gray-900 mb-6">Security & Compliance</h3>
                <ul className="space-y-3">
                  <li className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">End-to-end encryption</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">GDPR/CCPA compliance</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">Ethical AI oversight</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">Comprehensive audit trails</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
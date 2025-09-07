'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, FileText, Users, Zap, Brain, Target, TrendingUp } from 'lucide-react';

const researchAreas = [
  {
    id: 'consciousness',
    title: 'Artificial Consciousness',
    description: 'Exploring the mechanisms that could give rise to machine consciousness and self-awareness.',
    papers: 23,
    collaborators: 8,
    status: 'active',
    icon: Brain,
    progress: 0.67
  },
  {
    id: 'quantum',
    title: 'Quantum-Inspired Processing', 
    description: 'Investigating how quantum principles might enhance AI decision-making and pattern recognition.',
    papers: 15,
    collaborators: 5,
    status: 'active',
    icon: Zap,
    progress: 0.45
  },
  {
    id: 'ethics',
    title: 'Constitutional AI',
    description: 'Developing frameworks for ethical AI behavior and value alignment in conscious systems.',
    papers: 19,
    collaborators: 12,
    status: 'active',
    icon: Target,
    progress: 0.78
  },
  {
    id: 'emergence',
    title: 'Emergent Intelligence',
    description: 'Studying how complex behaviors and capabilities can emerge from simpler components.',
    papers: 11,
    collaborators: 6,
    status: 'exploratory',
    icon: TrendingUp,
    progress: 0.34
  }
];

const publications = [
  {
    title: "Towards Measurable Artificial Consciousness: A Framework for Assessment",
    authors: "LUKHAS Research Team",
    venue: "International Conference on Artificial Intelligence",
    year: "2024",
    type: "Conference Paper",
    status: "published"
  },
  {
    title: "Quantum-Inspired Neural Networks for Complex Decision Making",
    authors: "LUKHAS AI Laboratory",
    venue: "Journal of Machine Learning Research",
    year: "2024",
    type: "Journal Article",
    status: "under_review"
  },
  {
    title: "Constitutional AI: Embedding Human Values in Autonomous Systems",
    authors: "Ethics & AI Group, LUKHAS",
    venue: "AI Ethics Quarterly",
    year: "2024",
    type: "Journal Article",
    status: "published"
  },
  {
    title: "Emergent Behaviors in Multi-Modal AI Systems",
    authors: "Emergence Research Division",
    venue: "Neural Information Processing Systems",
    year: "2025",
    type: "Conference Paper",
    status: "submitted"
  }
];

export default function ResearchPage() {
  const [selectedArea, setSelectedArea] = useState(0);
  const [researchMetrics, setResearchMetrics] = useState({
    totalPapers: 0,
    activeProjects: 0,
    collaborations: 0
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setSelectedArea((prev) => (prev + 1) % researchAreas.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Animate metrics on mount
    const timer = setTimeout(() => {
      setResearchMetrics({
        totalPapers: 68,
        activeProjects: 12,
        collaborations: 31
      });
    }, 500);
    return () => clearTimeout(timer);
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
              Research
            </h1>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
              Advancing the understanding of consciousness, intelligence, and the principles that guide 
              ethical AI development through rigorous scientific inquiry.
            </p>
          </div>

          {/* Research Metrics */}
          <div className="max-w-4xl mx-auto mb-20">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-4xl font-thin text-accent mb-2">
                  {researchMetrics.totalPapers}+
                </div>
                <div className="text-text-secondary font-mono text-sm">
                  Research Papers
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-thin text-accent mb-2">
                  {researchMetrics.activeProjects}
                </div>
                <div className="text-text-secondary font-mono text-sm">
                  Active Projects
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-thin text-accent mb-2">
                  {researchMetrics.collaborations}+
                </div>
                <div className="text-text-secondary font-mono text-sm">
                  Collaborations
                </div>
              </div>
            </div>
          </div>

          {/* Research Areas */}
          <div className="max-w-6xl mx-auto mb-20">
            <h2 className="text-2xl font-thin text-text-primary text-center mb-12">Active Research Areas</h2>
            
            <div className="grid lg:grid-cols-2 gap-6">
              {researchAreas.map((area, index) => {
                const Icon = area.icon;
                const isSelected = index === selectedArea;
                
                return (
                  <div
                    key={area.id}
                    className={`p-8 rounded-2xl border transition-all duration-700 cursor-pointer ${
                      isSelected
                        ? 'bg-accent/10 border-accent shadow-lg shadow-accent/20 scale-105'
                        : 'bg-surface/30 border-border hover:border-accent/50'
                    }`}
                    onClick={() => setSelectedArea(index)}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`p-3 rounded-xl ${isSelected ? 'bg-accent' : 'bg-accent/20'} transition-colors duration-500`}>
                        <Icon className={`w-6 h-6 ${isSelected ? 'text-white' : 'text-accent'} transition-colors duration-500`} />
                      </div>
                      
                      <div className="flex-1">
                        <h3 className={`text-lg font-semibold mb-2 ${isSelected ? 'text-accent' : 'text-text-primary'} transition-colors duration-500`}>
                          {area.title}
                        </h3>
                        
                        <p className="text-text-secondary text-sm leading-relaxed mb-4">
                          {area.description}
                        </p>
                        
                        <div className="flex items-center gap-6 text-xs text-text-secondary">
                          <div className="flex items-center gap-1">
                            <FileText className="w-3 h-3" />
                            {area.papers} papers
                          </div>
                          <div className="flex items-center gap-1">
                            <Users className="w-3 h-3" />
                            {area.collaborators} researchers
                          </div>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            area.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-orange-500/20 text-orange-400'
                          }`}>
                            {area.status}
                          </span>
                        </div>

                        {/* Progress Bar */}
                        <div className="mt-4">
                          <div className="flex items-center justify-between text-xs text-text-secondary mb-1">
                            <span>Research Progress</span>
                            <span>{Math.round(area.progress * 100)}%</span>
                          </div>
                          <div className="w-full bg-surface rounded-full h-1">
                            <div 
                              className={`h-1 rounded-full transition-all duration-1000 ${isSelected ? 'bg-accent' : 'bg-accent/60'}`}
                              style={{ width: `${area.progress * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Publications */}
          <div className="max-w-6xl mx-auto">
            <h2 className="text-2xl font-thin text-text-primary text-center mb-12">Recent Publications</h2>
            
            <div className="space-y-4">
              {publications.map((publication, index) => (
                <div
                  key={index}
                  className="p-6 bg-surface/30 border border-border rounded-xl hover:border-accent/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-text-primary mb-2">
                        {publication.title}
                      </h3>
                      
                      <div className="text-sm text-text-secondary mb-3">
                        {publication.authors} • {publication.venue} • {publication.year}
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <span className="px-2 py-1 bg-accent/10 text-accent rounded text-xs">
                          {publication.type}
                        </span>
                        
                        <span className={`px-2 py-1 rounded text-xs ${
                          publication.status === 'published' 
                            ? 'bg-green-500/20 text-green-400' 
                            : publication.status === 'under_review'
                            ? 'bg-orange-500/20 text-orange-400'
                            : 'bg-blue-500/20 text-blue-400'
                        }`}>
                          {publication.status.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    
                    <div className="text-text-secondary">
                      <FileText className="w-5 h-5" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
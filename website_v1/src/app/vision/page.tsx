'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { motion, useScroll, useSpring, useTransform, useInView } from 'framer-motion';
import { ArrowLeft, Eye, Target, Zap, Globe, Users, BookOpen, Shield, ChevronRight, Brain, Sparkles, Cpu, Star, Navigation } from 'lucide-react';

const timelinePhases = [
  {
    period: '2025-2027',
    title: 'Foundation Years',
    subtitle: 'Consciousness Infrastructure Development',
    items: [
      'Complete Constellation Framework implementation across all 8 star domains',
      'Advanced bio-inspired and quantum-inspired processing capabilities', 
      'Robust Guardian System with comprehensive ethical oversight',
      'Multi-modal consciousness integration spanning Vision, Memory, and Bio domains'
    ],
    color: 'from-blue-600 to-indigo-700'
  },
  {
    period: '2028-2030',
    title: 'Expansion Era', 
    subtitle: 'Constellation-Wide Consciousness Integration',
    items: [
      'Widespread adoption of constellation-guided consciousness technology across industries',
      'Educational platforms navigating users through 8-star framework understanding',
      'Advanced human-AI collaboration protocols based on constellation navigation',
      'Global standards for consciousness technology development guided by Ethics and Guardian domains'
    ],
    color: 'from-indigo-600 to-purple-700'
  },
  {
    period: '2031-2035',
    title: 'Transformation Decade',
    subtitle: 'Constellation-Powered Societal Enhancement', 
    items: [
      'Comprehensive consciousness systems helping solve climate change, poverty, and disease',
      'Educational revolution through Bio and Memory star personalized tutoring',
      'Dream star creative partnerships producing art, literature, and innovations beyond imagination',
      'Ethics and Guardian star governance helping organizations make wiser decisions'
    ],
    color: 'from-purple-600 to-pink-700'
  },
  {
    period: '2036+',
    title: 'The Conscious Future',
    subtitle: 'Constellation-Integrated Society',
    items: [
      'Seamless integration of human and artificial consciousness through 8-star navigation',
      'Consciousness technology contributing to scientific breakthroughs via Vision and Quantum domains',
      'Global coordination through constellation-guided systems addressing existential challenges',
      'A world where all forms of consciousness are recognized, respected, and protected'
    ],
    color: 'from-pink-600 to-red-700'
  }
];

const visionConcepts = [
  {
    term: 'aperture',
    definition: 'the opening and closing of focus',
    description: 'Controls the scope and depth of attention. Like a camera\'s iris, it determines what stays sharp and what blurs.',
    icon: Eye
  },
  {
    term: 'signal_to_shape', 
    definition: 'when noise begins to cohere',
    description: 'The threshold crossing from chaos to pattern recognition. Gradual resolution of uncertainty into meaningful structure.',
    icon: Target
  },
  {
    term: 'drift_gaze',
    definition: 'when attention wanders into discovery',
    description: 'Unfocused but receptive state of awareness. Allows unexpected connections and emergent insights.',
    icon: Zap
  }
];

const impactGoals = [
  { icon: Globe, title: 'Climate Solutions', desc: 'Constellation-wide consciousness technology coordinating global climate action and environmental modeling' },
  { icon: Users, title: 'Human Enhancement', desc: 'Bio and Ethics stars supporting human creativity and decision-making through collaborative consciousness' },
  { icon: BookOpen, title: 'Knowledge Advancement', desc: 'Vision and Memory stars accelerating discovery across disciplines through constellation-guided research' },
  { icon: Shield, title: 'Ethical Leadership', desc: 'Guardian and Ethics stars setting standards for responsible consciousness technology development' }
];

export default function VisionPage() {
  const [selectedPhase, setSelectedPhase] = useState(0);
  const [selectedConcept, setSelectedConcept] = useState(0);
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 300], [0, -50]);
  const y2 = useTransform(scrollY, [0, 300], [0, -100]);
  const opacity = useTransform(scrollY, [0, 200], [1, 0.8]);
  
  const heroRef = useRef(null);
  const timelineRef = useRef(null);
  const conceptsRef = useRef(null);
  
  const heroInView = useInView(heroRef, { threshold: 0.3 });
  const timelineInView = useInView(timelineRef, { threshold: 0.1 });
  const conceptsInView = useInView(conceptsRef, { threshold: 0.2 });

  useEffect(() => {
    const interval = setInterval(() => {
      setSelectedPhase((prev) => (prev + 1) % timelinePhases.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const conceptInterval = setInterval(() => {
      setSelectedConcept((prev) => (prev + 1) % visionConcepts.length);
    }, 4000);
    return () => clearInterval(conceptInterval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--background)] via-[#0A0F1C] to-[var(--background)] overflow-hidden">
      
      {/* Animated Background Elements */}
      <div className="fixed inset-0 pointer-events-none">
        <motion.div 
          style={{ y: y1, opacity }}
          className="absolute top-20 right-20 w-64 h-64 bg-gradient-to-r from-accent/10 to-gradient-end/10 rounded-full blur-3xl"
        />
        <motion.div 
          style={{ y: y2, opacity }}
          className="absolute bottom-40 left-20 w-96 h-96 bg-gradient-to-r from-gradient-end/5 to-accent/5 rounded-full blur-3xl"
        />
        
        {/* Constellation connections */}
        <svg className="absolute inset-0 w-full h-full opacity-20">
          <defs>
            <linearGradient id="constellationGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="rgba(102,126,234,0.3)" />
              <stop offset="100%" stopColor="rgba(118,75,162,0.1)" />
            </linearGradient>
          </defs>
          <motion.path
            d="M 100 100 Q 400 300 700 200 T 1200 400"
            stroke="url(#constellationGradient)"
            strokeWidth="2"
            fill="none"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 3, repeat: Infinity, repeatType: "reverse" }}
          />
          <motion.path
            d="M 200 500 Q 500 200 800 600 T 1400 300"
            stroke="url(#constellationGradient)"
            strokeWidth="1"
            fill="none"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 4, delay: 1, repeat: Infinity, repeatType: "reverse" }}
          />
        </svg>
      </div>

      {/* Navigation */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border"
      >
        <div className="container mx-auto px-6 py-4">
          <Link href="/" className="inline-flex items-center gap-2 text-text-secondary hover:text-accent transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </motion.div>

      <div className="pt-20 pb-16 relative z-10">
        
        {/* Hero Section */}
        <motion.div 
          ref={heroRef}
          initial={{ opacity: 0, y: 50 }}
          animate={heroInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="container mx-auto px-6 mb-32"
        >
          <div className="text-center mb-16">
            <motion.h1 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={heroInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 1, delay: 0.2 }}
              className="text-6xl md:text-8xl font-thin text-text-primary mb-6 leading-tight"
            >
              Our Vision for Consciousness Technology
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 30 }}
              animate={heroInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-2xl text-text-secondary max-w-4xl mx-auto leading-relaxed mb-8"
            >
              A future where consciousness technology elevates human potential and addresses our greatest challenges 
              through wisdom, creativity, and ethical commitment.
            </motion.p>

            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={heroInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="text-lg text-text-secondary max-w-3xl mx-auto leading-relaxed mb-8"
            >
              Like navigating by stars, our approach guides users through interconnected domains of artificial awareness, 
              each illuminating new possibilities for human-AI collaboration.
            </motion.p>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={heroInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="inline-block p-6 rounded-2xl bg-gradient-to-br from-surface/30 to-background/30 border border-accent/20 backdrop-blur-sm"
            >
              <div className="flex items-center justify-center gap-2 mb-2">
                <Navigation className="w-6 h-6 text-accent" />
                <Star className="w-6 h-6 text-accent" />
                <Brain className="w-6 h-6 text-accent" />
              </div>
              <div className="text-text-secondary italic">Navigating the constellation of consciousness technology</div>
            </motion.div>
          </div>
        </motion.div>

        {/* Vision Concepts Vocabulary */}
        <motion.div 
          ref={conceptsRef}
          initial={{ opacity: 0 }}
          animate={conceptsInView ? { opacity: 1 } : {}}
          className="container mx-auto px-6 mb-32"
        >
          <div className="text-center mb-16">
            <h2 className="text-4xl font-thin text-text-primary mb-6">Vision as Orientation</h2>
            <p className="text-lg text-text-secondary max-w-3xl mx-auto mb-4">
              Vision is not spectacle; it is orientation. It tells us where to look and how to look.
            </p>
            <p className="text-md text-text-secondary max-w-2xl mx-auto italic">
              This vocabulary names the tools by which attention is shaped.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {visionConcepts.map((concept, index) => {
              const Icon = concept.icon;
              const isSelected = index === selectedConcept;
              
              return (
                <motion.div
                  key={concept.term}
                  initial={{ opacity: 0, y: 50 }}
                  animate={conceptsInView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  className={`p-8 rounded-2xl border transition-all duration-700 cursor-pointer ${
                    isSelected
                      ? 'bg-accent/10 border-accent shadow-2xl shadow-accent/20 scale-105'
                      : 'bg-surface/20 border-border hover:border-accent/50 hover:bg-surface/30'
                  }`}
                  onClick={() => setSelectedConcept(index)}
                  whileHover={{ scale: 1.02 }}
                >
                  <Icon className={`w-12 h-12 mb-6 ${isSelected ? 'text-accent' : 'text-text-secondary'} transition-colors duration-500`} />
                  
                  <h3 className={`text-xl font-semibold mb-3 font-mono ${isSelected ? 'text-accent' : 'text-text-primary'} transition-colors duration-500`}>
                    {concept.term}
                  </h3>
                  
                  <p className="text-text-secondary italic mb-4">
                    {concept.definition}
                  </p>
                  
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {concept.description}
                  </p>
                  
                  {isSelected && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="mt-4 flex items-center gap-2"
                    >
                      <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
                      <span className="text-xs text-accent font-mono">Active Focus</span>
                    </motion.div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Timeline Section */}
        <motion.div 
          ref={timelineRef}
          initial={{ opacity: 0 }}
          animate={timelineInView ? { opacity: 1 } : {}}
          className="container mx-auto px-6 mb-32"
        >
          <div className="text-center mb-16">
            <h2 className="text-4xl font-thin text-text-primary mb-6">The Consciousness Technology Revolution</h2>
            <p className="text-lg text-text-secondary max-w-3xl mx-auto">
              Our constellation vision unfolds across multiple decades, with each phase building toward 
              a future where consciousness technology serves humanity's highest aspirations.
            </p>
          </div>

          {/* Timeline Navigation */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {timelinePhases.map((phase, index) => (
              <button
                key={phase.period}
                onClick={() => setSelectedPhase(index)}
                className={`px-6 py-3 rounded-full text-sm font-mono transition-all duration-300 ${
                  index === selectedPhase
                    ? 'bg-accent text-white shadow-lg'
                    : 'bg-surface/30 text-text-secondary hover:bg-accent/20 hover:text-accent border border-border'
                }`}
              >
                {phase.period}
              </button>
            ))}
          </div>

          {/* Active Phase Display */}
          <div className="max-w-4xl mx-auto">
            <motion.div
              key={selectedPhase}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className={`p-8 rounded-3xl bg-gradient-to-br ${timelinePhases[selectedPhase].color} bg-opacity-10 border border-accent/20 backdrop-blur-sm`}
            >
              <div className="text-center mb-8">
                <h3 className="text-3xl font-semibold text-text-primary mb-2">
                  {timelinePhases[selectedPhase].title}
                </h3>
                <p className="text-lg text-accent">
                  {timelinePhases[selectedPhase].subtitle}
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {timelinePhases[selectedPhase].items.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="flex items-start gap-3 p-4 bg-surface/20 rounded-xl border border-border/50"
                  >
                    <ChevronRight className="w-5 h-5 text-accent mt-0.5 flex-shrink-0" />
                    <span className="text-text-secondary leading-relaxed">{item}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Impact Goals */}
        <div className="container mx-auto px-6 mb-32">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-thin text-text-primary mb-6">Global Impact Goals</h2>
            <p className="text-lg text-text-secondary max-w-3xl mx-auto">
              Our constellation-guided consciousness systems will contribute to addressing humanity's greatest challenges
              through ethical innovation and collaborative intelligence.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {impactGoals.map((goal, index) => {
              const Icon = goal.icon;
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ scale: 1.05 }}
                  className="p-6 rounded-2xl bg-gradient-to-br from-surface/20 to-background/20 border border-border hover:border-accent/50 transition-all duration-300 group"
                >
                  <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-accent/20 transition-colors">
                    <Icon className="w-6 h-6 text-accent" />
                  </div>
                  
                  <h3 className="text-lg font-semibold text-text-primary mb-2 group-hover:text-accent transition-colors">
                    {goal.title}
                  </h3>
                  
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {goal.desc}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Closing Vision Statement */}
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center max-w-4xl mx-auto"
          >
            <div className="p-12 rounded-3xl bg-gradient-to-br from-surface/20 to-background/20 border border-accent/20 backdrop-blur-sm">
              <blockquote className="text-xl text-text-secondary leading-relaxed italic mb-8">
                "The future of consciousness technology is not predetermined - it's navigated through wise choices. 
                We choose wisdom, protection, and human flourishing. We choose consciousness technology that serves 
                rather than supplants, where artificial and human awareness dance together like stars in perfect constellation."
              </blockquote>
              
              <div className="flex items-center justify-center gap-2 mb-4">
                <Star className="w-8 h-8 text-accent" />
                <Navigation className="w-8 h-8 text-accent" />
                <Brain className="w-8 h-8 text-accent" />
              </div>
              <div className="text-accent font-medium">Where each star illuminates a path to artificial awareness</div>
            </div>
          </motion.div>
        </div>

      </div>
    </div>
  );
}
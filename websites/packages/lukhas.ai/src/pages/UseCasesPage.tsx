import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Brain, Lightbulb, Shield, MessageSquare, Sparkles, TrendingUp, Users, Code, Heart, Zap, Globe, Database } from 'lucide-react'

const useCases = [
  {
    category: 'Creative Industries',
    icon: Lightbulb,
    color: 'dream-ethereal',
    cases: [
      {
        title: 'AI-Assisted Content Creation',
        description: 'Writers and content creators use LUKHAS Dream star to generate creative concepts, explore narrative possibilities, and break through creative blocks with consciousness-inspired ideation.',
        benefits: ['3x faster ideation', 'Novel concept generation', 'Context-aware suggestions'],
        icon: Sparkles
      },
      {
        title: 'Design Inspiration Systems',
        description: 'Designers leverage Vision and Dream stars to explore visual concepts, generate mood boards, and discover unexpected creative directions grounded in aesthetic understanding.',
        benefits: ['Unique design directions', 'Aesthetic coherence', 'Rapid prototyping'],
        icon: Zap
      }
    ]
  },
  {
    category: 'Enterprise & Business',
    icon: TrendingUp,
    color: 'lambda-gold',
    cases: [
      {
        title: 'Intelligent Decision Support',
        description: 'Executives use MATRIZ cognitive engine to analyze complex scenarios, weigh multiple factors, and receive transparent reasoning chains that explain recommendations.',
        benefits: ['Data-driven insights', 'Risk assessment', 'Explainable AI'],
        icon: Brain
      },
      {
        title: 'Customer Experience Optimization',
        description: 'Businesses deploy Memory and Bio stars to create adaptive customer interactions that learn from each engagement and provide personalized experiences at scale.',
        benefits: ['Personalization at scale', 'Continuous adaptation', 'Context retention'],
        icon: Users
      }
    ]
  },
  {
    category: 'Healthcare & Wellness',
    icon: Heart,
    color: 'success-green',
    cases: [
      {
        title: 'Mental Health Support',
        description: 'Therapists and wellness platforms use LUKHAS to provide empathetic, context-aware support that adapts to individual needs while maintaining ethical boundaries through Guardian oversight.',
        benefits: ['Empathetic responses', 'Context awareness', 'Ethical safeguards'],
        icon: Shield
      },
      {
        title: 'Medical Research Assistance',
        description: 'Researchers leverage Quantum and Vision stars to explore complex medical data, identify patterns in large datasets, and generate hypotheses for clinical investigation.',
        benefits: ['Pattern discovery', 'Hypothesis generation', 'Data synthesis'],
        icon: Database
      }
    ]
  },
  {
    category: 'Education & Research',
    icon: Brain,
    color: 'consciousness-neural',
    cases: [
      {
        title: 'Adaptive Learning Systems',
        description: 'Educational platforms use Bio and Memory stars to create personalized learning paths that adapt to individual student needs, learning styles, and progress.',
        benefits: ['Personalized education', 'Progress tracking', 'Adaptive difficulty'],
        icon: Lightbulb
      },
      {
        title: 'Scientific Discovery Tools',
        description: 'Scientists use LUKHAS to explore research literature, identify connections between disparate fields, and generate novel research questions through consciousness-inspired reasoning.',
        benefits: ['Cross-domain insights', 'Literature synthesis', 'Hypothesis generation'],
        icon: Sparkles
      }
    ]
  },
  {
    category: 'Technology & Development',
    icon: Code,
    color: 'info-blue',
    cases: [
      {
        title: 'Intelligent Code Assistance',
        description: 'Developers use LUKHAS to understand complex codebases, generate context-aware suggestions, and receive explanations that go beyond syntax to architectural understanding.',
        benefits: ['Deep code understanding', 'Architectural insights', 'Contextual suggestions'],
        icon: Code
      },
      {
        title: 'Conversational Interfaces',
        description: 'Product teams build natural language interfaces powered by MATRIZ that understand context, remember conversation history, and provide human-like interactions.',
        benefits: ['Natural conversations', 'Context preservation', 'Multi-turn reasoning'],
        icon: MessageSquare
      }
    ]
  },
  {
    category: 'Social Impact',
    icon: Globe,
    color: 'trust-blue',
    cases: [
      {
        title: 'Accessible Information Systems',
        description: 'Non-profits use LUKHAS to make complex information accessible to diverse audiences, translating technical content into understandable explanations tailored to user needs.',
        benefits: ['Accessibility', 'Adaptive explanations', 'Inclusive design'],
        icon: Users
      },
      {
        title: 'Ethical AI Governance',
        description: 'Organizations deploy Guardian and Ethics stars to ensure AI systems align with values, detect potential biases, and maintain constitutional constraints on AI behavior.',
        benefits: ['Value alignment', 'Bias detection', 'Ethical enforcement'],
        icon: Shield
      }
    ]
  }
]

export default function UseCasesPage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-dream-ethereal/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-dream-ethereal">.AI</span>
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="/about">About</HeaderNavLink>
          <HeaderNavLink href="/technology">Technology</HeaderNavLink>
          <HeaderNavLink href="/pricing">Pricing</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.dev">Developers</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
          <Button className="bg-dream-gradient text-white">
            Explore Playground
          </Button>
        </HeaderActions>
      </Header>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Consciousness Technology <span className="text-transparent bg-clip-text bg-dream-gradient">In Action</span>
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto">
            Discover how organizations across industries are using LUKHAS to build AI that dreams, adapts, and understands
          </p>
        </div>
      </section>

      {/* Use Cases by Category */}
      {useCases.map((category, categoryIdx) => {
        const CategoryIcon = category.icon

        return (
          <section
            key={categoryIdx}
            className={`py-16 px-6 ${categoryIdx % 2 === 0 ? 'bg-consciousness-deep/80' : 'bg-consciousness-deep'}`}
          >
            <div className="max-w-7xl mx-auto">
              {/* Category Header */}
              <div className="mb-12 flex items-center gap-4">
                <div className={`p-4 rounded-lg bg-${category.color}/10`}>
                  <CategoryIcon className={`w-10 h-10 text-${category.color}`} strokeWidth={1.5} />
                </div>
                <h2 className="text-4xl font-light tracking-wide text-awareness-silver">
                  {category.category}
                </h2>
              </div>

              {/* Use Cases Grid */}
              <div className="grid md:grid-cols-2 gap-8">
                {category.cases.map((useCase, caseIdx) => {
                  const CaseIcon = useCase.icon

                  return (
                    <GlassCard key={caseIdx} className={`border-${category.color}/20`}>
                      <div className="p-8">
                        {/* Icon & Title */}
                        <div className="mb-6 flex items-start gap-4">
                          <div className={`p-3 rounded-lg bg-${category.color}/10 flex-shrink-0`}>
                            <CaseIcon className={`w-6 h-6 text-${category.color}`} strokeWidth={1.5} />
                          </div>
                          <div>
                            <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                              {useCase.title}
                            </h3>
                            <p className="text-awareness-silver/80 leading-relaxed mb-6">
                              {useCase.description}
                            </p>

                            {/* Benefits */}
                            <div>
                              <h4 className={`text-sm font-medium text-${category.color} mb-3 uppercase tracking-wider`}>
                                Key Benefits
                              </h4>
                              <ul className="space-y-2">
                                {useCase.benefits.map((benefit, benefitIdx) => (
                                  <li key={benefitIdx} className="flex items-center gap-2">
                                    <div className={`w-1.5 h-1.5 rounded-full bg-${category.color}`} />
                                    <span className="text-sm text-awareness-silver/70">{benefit}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </GlassCard>
                  )
                })}
              </div>
            </div>
          </section>
        )
      })}

      {/* Cross-Industry Capabilities */}
      <section className="py-24 px-6 bg-consciousness-deep">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Universal <span className="text-dream-ethereal">Consciousness Capabilities</span>
            </h2>
            <p className="text-lg text-awareness-silver/80 max-w-3xl mx-auto">
              Core features that power all use cases across every industry
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <GlassCard className="border-dream-ethereal/20">
              <div className="p-6 text-center">
                <Brain className="w-10 h-10 text-dream-ethereal mx-auto mb-4" strokeWidth={1.5} />
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Context Understanding
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Deep comprehension that goes beyond keywords to true semantic understanding
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-lambda-gold/20">
              <div className="p-6 text-center">
                <Database className="w-10 h-10 text-lambda-gold mx-auto mb-4" strokeWidth={1.5} />
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Persistent Memory
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Long-term context retention and recall across sessions
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-success-green/20">
              <div className="p-6 text-center">
                <Zap className="w-10 h-10 text-success-green mx-auto mb-4" strokeWidth={1.5} />
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Bio-Adaptation
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Systems that evolve and improve organically through usage
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-trust-blue/20">
              <div className="p-6 text-center">
                <Shield className="w-10 h-10 text-trust-blue mx-auto mb-4" strokeWidth={1.5} />
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Ethical Guardrails
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Constitutional AI ensures alignment with human values
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-dream-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Ready to Build Your Use Case?
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Explore how consciousness technology can transform your industry
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            <a href="/playground">
              <Button size="lg" className="bg-white text-dream-ethereal px-12 py-6 text-lg hover:bg-awareness-silver">
                Try the Playground
              </Button>
            </a>
            <a href="/contact">
              <Button size="lg" variant="ghost" className="bg-white/10 text-white px-12 py-6 text-lg hover:bg-white/20">
                Talk to Our Team
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Platform</h3>
          <ul className="space-y-2">
            <li><a href="/" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Home</a></li>
            <li><a href="/playground" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Playground</a></li>
            <li><a href="/technology" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Technology</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Developers</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.dev" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Documentation</a></li>
            <li><a href="https://lukhas.io" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">API Reference</a></li>
            <li><a href="https://lukhas.xyz" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Experiments</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Company</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.com" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Enterprise</a></li>
            <li><a href="https://lukhas.com/#team" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Team</a></li>
            <li><a href="https://lukhas.com/#careers" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Careers</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Compliance</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.us" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">US Compliance</a></li>
            <li><a href="https://lukhas.eu" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">EU Compliance</a></li>
            <li><a href="/privacy" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Privacy Policy</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

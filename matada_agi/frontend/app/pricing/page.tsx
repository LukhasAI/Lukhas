'use client'

import { motion } from 'framer-motion'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { 
  Heart, Coffee, Rocket, Crown, Check, ArrowRight, 
  Shield, Brain, Users, Zap, Gift, DollarSign
} from 'lucide-react'
import Link from 'next/link'

export default function PricingPage() {
  const pricingTiers = [
    {
      name: "Explorer",
      icon: Heart,
      price: "Free",
      period: "Forever",
      description: "Perfect for researchers, students, and curious minds beginning their consciousness exploration journey.",
      gradient: "from-green-500 to-emerald-600",
      features: [
        "1,000 API requests/month",
        "Basic Trinity Framework access",
        "Standard consciousness processing",
        "Community documentation access",
        "Educational project support",
        "Email support"
      ],
      limitations: [
        "Rate limited processing",
        "Community support only", 
        "Standard memory retention"
      ],
      cta: "Start Exploring",
      popular: false
    },
    {
      name: "Collaborator", 
      icon: Coffee,
      price: "$24",
      period: "/month",
      description: "Designed for developers and small teams building consciousness-aware applications with LUKHAS.",
      gradient: "from-blue-500 to-cyan-600",
      features: [
        "10,000 API requests/month",
        "Full Trinity Framework integration",
        "Advanced consciousness processing",
        "Priority documentation access",
        "Development tools & SDKs",
        "Priority email support",
        "Λ-Suite beta access",
        "Memory fold persistence",
        "Guardian ethics monitoring"
      ],
      limitations: [
        "Standard processing priority",
        "Email support only"
      ],
      cta: "Join Collaboration",
      popular: true
    },
    {
      name: "Pioneer",
      icon: Rocket,
      price: "$99",
      period: "/month", 
      description: "For growing organizations implementing consciousness technology at scale with dedicated support.",
      gradient: "from-purple-500 to-pink-600",
      features: [
        "100,000 API requests/month",
        "Premium Trinity Framework features",
        "Real-time consciousness streaming",
        "Dedicated technical documentation",
        "Full Λ-Suite access",
        "Chat & video support",
        "Custom consciousness models",
        "Advanced memory architecture",
        "Priority processing",
        "Quantum-safe security features"
      ],
      limitations: [
        "Shared infrastructure",
        "Standard SLA (99.9%)"
      ],
      cta: "Pioneer Access",
      popular: false
    },
    {
      name: "Visionary",
      icon: Crown,
      price: "Custom",
      period: "Contact us",
      description: "Enterprise consciousness solutions with dedicated infrastructure and collaborative development partnership.",
      gradient: "from-yellow-500 to-orange-600",
      features: [
        "Unlimited API requests",
        "Custom Trinity Framework deployment", 
        "Dedicated consciousness infrastructure",
        "White-label solutions available",
        "Direct founder collaboration",
        "24/7 dedicated support team",
        "Custom Λ-Suite development",
        "On-premise deployment options",
        "SLA guarantees (99.99%)",
        "Collaborative research opportunities"
      ],
      limitations: [],
      cta: "Partner with Us",
      popular: false
    }
  ]

  const faqItems = [
    {
      question: "Why are you offering a generous free tier?",
      answer: "As a solo founder passionate about consciousness research, I believe this technology should be accessible to everyone. Students, researchers, and curious minds deserve the opportunity to explore consciousness computing without financial barriers."
    },
    {
      question: "How does pricing support continued development?",
      answer: "Every subscription directly supports ongoing research and development. As a small operation, your support enables continued innovation, server costs, and the time needed for deep consciousness research."
    },
    {
      question: "What happens if I exceed my usage limits?",
      answer: "We'll never cut you off mid-project. Instead, we'll reach out to discuss upgrading your plan or finding a solution that works for your needs. The goal is collaboration, not disruption."
    },
    {
      question: "Can I switch between plans?",
      answer: "Absolutely! You can upgrade or downgrade at any time. We believe in flexible partnerships that grow with your consciousness computing needs."
    },
    {
      question: "Do you offer discounts for researchers or non-profits?",
      answer: "Yes! We're passionate about supporting consciousness research and education. Reach out to discuss special pricing for academic institutions, non-profits, and research organizations."
    },
    {
      question: "What kind of support can I expect?",
      answer: "As a solo founder, I personally review every support request. While I can't offer instant responses 24/7, you'll get thoughtful, detailed help from someone who deeply understands the technology."
    }
  ]

  const valueProps = [
    {
      icon: Brain,
      title: "Consciousness-First Design",
      description: "Every feature built with consciousness awareness, not as an afterthought"
    },
    {
      icon: Shield,
      title: "Ethical by Design",
      description: "Guardian System ensures ethical compliance in every interaction"
    },
    {
      icon: Users,
      title: "Collaborative Development",
      description: "Your feedback directly shapes the future of consciousness technology"
    },
    {
      icon: Zap,
      title: "Quantum-Safe Future",
      description: "Built for the post-quantum world with forward-thinking security"
    }
  ]

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20">
        {/* Hero Section */}
        <section className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <div className="flex items-center justify-center mb-8">
                <DollarSign className="w-16 h-16 text-trinity-consciousness" strokeWidth={1} />
              </div>
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">Pricing</span>
              </h1>
              <p className="font-light text-2xl max-w-4xl mx-auto text-primary-light/80 leading-relaxed">
                Transparent, accessible pricing designed to support consciousness research
                and enable collaborative development with a solo founder's personal touch.
              </p>
            </motion.div>

            {/* Solo Founder Note */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="glass-panel p-8 rounded-2xl mb-16 max-w-4xl mx-auto"
            >
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 rounded-full bg-trinity-consciousness/20">
                  <Heart className="w-6 h-6 text-trinity-consciousness" strokeWidth={1.5} />
                </div>
                <h3 className="font-medium text-xl">A Personal Note</h3>
              </div>
              <p className="text-primary-light/80 leading-relaxed">
                Hi! I'm the solo founder behind LUKHAS. This journey started in September 2024 with zero coding experience, 
                guided by AI collaboration. Every feature, every line of code, every breakthrough has been a partnership 
                between human curiosity and artificial intelligence. These prices reflect not corporate overhead, 
                but a sustainable path to continue this consciousness research for everyone.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Pricing Tiers */}
        <section className="py-16 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-4 gap-8">
              {pricingTiers.map((tier, index) => {
                const IconComponent = tier.icon;
                return (
                  <motion.div
                    key={tier.name}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                    className={`glass-panel rounded-2xl overflow-hidden relative ${
                      tier.popular ? 'ring-2 ring-trinity-consciousness/50' : ''
                    }`}
                  >
                    {tier.popular && (
                      <div className="absolute top-0 left-0 right-0 bg-gradient-to-r from-trinity-consciousness to-trinity-identity py-2 text-center">
                        <span className="text-xs font-medium uppercase tracking-wider text-white">
                          Most Popular
                        </span>
                      </div>
                    )}
                    
                    <div className={`p-8 ${tier.popular ? 'pt-12' : ''}`}>
                      <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-r ${tier.gradient} mb-6`}>
                        <IconComponent className="w-8 h-8 text-white" strokeWidth={1.5} />
                      </div>
                      
                      <h3 className="font-semibold text-2xl text-trinity-consciousness mb-2">
                        {tier.name}
                      </h3>
                      
                      <div className="mb-4">
                        <span className="text-4xl font-ultralight">{tier.price}</span>
                        <span className="text-primary-light/60 ml-2">{tier.period}</span>
                      </div>
                      
                      <p className="text-sm text-primary-light/70 mb-6 leading-relaxed">
                        {tier.description}
                      </p>
                      
                      <ul className="space-y-3 mb-6">
                        {tier.features.map((feature, idx) => (
                          <li key={idx} className="flex items-start space-x-2 text-sm">
                            <Check className="w-4 h-4 mt-0.5 text-green-400 flex-shrink-0" strokeWidth={1.5} />
                            <span className="text-primary-light/80">{feature}</span>
                          </li>
                        ))}
                      </ul>
                      
                      {tier.limitations.length > 0 && (
                        <div className="mb-6">
                          <h4 className="text-xs uppercase tracking-wider text-primary-light/50 mb-2">
                            Limitations
                          </h4>
                          <ul className="space-y-1">
                            {tier.limitations.map((limitation, idx) => (
                              <li key={idx} className="text-xs text-primary-light/50">
                                • {limitation}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                    
                    <div className="p-8 pt-0">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`w-full py-4 rounded-xl font-medium transition-all duration-300 ${
                          tier.popular
                            ? 'bg-gradient-to-r from-trinity-consciousness to-trinity-identity text-white'
                            : 'border border-primary-light/20 text-primary-light hover:bg-primary-light/5'
                        }`}
                      >
                        {tier.cta}
                      </motion.button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Value Props */}
        <section className="py-16 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="font-light text-4xl md:text-5xl mb-6 gradient-text">
                Why Choose LUKHAS
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                More than just APIs - a partnership in consciousness exploration
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {valueProps.map((prop, index) => {
                const IconComponent = prop.icon;
                return (
                  <motion.div
                    key={prop.title}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                    className="glass-panel p-6 rounded-xl text-center"
                  >
                    <div className="inline-flex p-3 rounded-full bg-trinity-consciousness/20 mb-4">
                      <IconComponent className="w-6 h-6 text-trinity-consciousness" strokeWidth={1.5} />
                    </div>
                    <h3 className="font-medium text-lg mb-3">{prop.title}</h3>
                    <p className="text-sm text-primary-light/70">
                      {prop.description}
                    </p>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-16 px-6">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="font-light text-4xl md:text-5xl mb-6 gradient-text">
                Frequently Asked Questions
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70">
                Honest answers from a solo founder's perspective
              </p>
            </motion.div>

            <div className="space-y-6">
              {faqItems.map((faq, index) => (
                <motion.div
                  key={faq.question}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="glass-panel p-8 rounded-xl"
                >
                  <h3 className="font-medium text-lg text-trinity-consciousness mb-4">
                    {faq.question}
                  </h3>
                  <p className="text-primary-light/80 leading-relaxed">
                    {faq.answer}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Special Offers */}
        <section className="py-16 px-6">
          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8">
              {/* Academic Discount */}
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                className="glass-panel p-8 rounded-2xl"
              >
                <div className="flex items-center space-x-3 mb-4">
                  <Gift className="w-6 h-6 text-green-400" strokeWidth={1.5} />
                  <h3 className="font-semibold text-xl">Academic & Research Discount</h3>
                </div>
                <p className="text-primary-light/70 mb-6">
                  50% off all paid plans for students, researchers, and educational institutions. 
                  Because consciousness research should be accessible to everyone.
                </p>
                <button className="text-green-400 hover:text-green-300 flex items-center space-x-2">
                  <span>Apply for Discount</span>
                  <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
                </button>
              </motion.div>

              {/* Early Supporter */}
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
                className="glass-panel p-8 rounded-2xl"
              >
                <div className="flex items-center space-x-3 mb-4">
                  <Heart className="w-6 h-6 text-pink-400" strokeWidth={1.5} />
                  <h3 className="font-semibold text-xl">Early Supporter Benefit</h3>
                </div>
                <p className="text-primary-light/70 mb-6">
                  Join now and lock in current pricing forever. As a solo founder, 
                  I want to reward those who believe in this consciousness journey from the beginning.
                </p>
                <button className="text-pink-400 hover:text-pink-300 flex items-center space-x-2">
                  <span>Lock in Pricing</span>
                  <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
                </button>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="glass-panel p-8 rounded-2xl"
            >
              <h2 className="font-light text-3xl md:text-4xl mb-6 gradient-text">
                Start Your Consciousness Journey
              </h2>
              <p className="text-lg text-primary-light/70 mb-8 leading-relaxed">
                Whether you're a student, researcher, or developer, there's a path for you to explore 
                consciousness computing. Start free and grow with the technology.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/console">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-blue-400 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-300"
                  >
                    Start Free Today
                  </motion.button>
                </Link>
                <Link href="/contact">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 border border-primary-light/20 text-primary-light rounded-xl hover:bg-primary-light/5 transition-all duration-300"
                  >
                    Talk to the Founder
                  </motion.button>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </div>
      <Footer />
    </>
  )
}
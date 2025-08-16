'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { 
  Briefcase, Code, Brain, Shield, Users, Globe, 
  Rocket, Heart, Target, ChevronRight, MapPin, Clock
} from 'lucide-react'

export default function CareersPage() {
  const values = [
    {
      icon: Brain,
      title: 'Innovation First',
      description: 'Push the boundaries of AI consciousness and explore uncharted territories'
    },
    {
      icon: Users,
      title: 'Collaborative Excellence',
      description: 'Work with brilliant minds from diverse backgrounds and perspectives'
    },
    {
      icon: Shield,
      title: 'Ethical Foundation',
      description: 'Build AI that respects human values and promotes global benefit'
    },
    {
      icon: Heart,
      title: 'Human-Centered',
      description: 'Create technology that enhances human capabilities and wellbeing'
    }
  ]

  const benefits = [
    'Competitive compensation and equity packages',
    'Flexible remote-first work environment',
    'Cutting-edge hardware and development tools',
    'Conference attendance and learning budget',
    'Health, dental, and vision coverage',
    'Unlimited PTO and sabbatical options',
    'Work on revolutionary AI technology',
    'Collaborate with AI agents and systems'
  ]

  const openings = [
    {
      title: 'Senior Consciousness Engineer',
      department: 'Engineering',
      location: 'Remote',
      type: 'Full-time',
      description: 'Lead the development of advanced consciousness processing systems and neural architectures',
      requirements: [
        'PhD in Computer Science, Neuroscience, or related field',
        'Experience with neural networks and cognitive architectures',
        'Strong Python and system design skills',
        'Published research in consciousness or AI'
      ]
    },
    {
      title: 'AI Ethics Specialist',
      department: 'Governance',
      location: 'Remote',
      type: 'Full-time',
      description: 'Design and implement ethical frameworks for AI alignment and safety',
      requirements: [
        'Advanced degree in Ethics, Philosophy, or AI Safety',
        'Experience with AI governance frameworks',
        'Understanding of constitutional AI principles',
        'Strong communication and policy writing skills'
      ]
    },
    {
      title: 'Quantum-Bio Algorithm Developer',
      department: 'Research',
      location: 'Remote',
      type: 'Full-time',
      description: 'Develop quantum-inspired and bio-inspired algorithms for consciousness processing',
      requirements: [
        'MS/PhD in Quantum Computing or Computational Biology',
        'Experience with quantum simulation frameworks',
        'Strong mathematical and algorithmic skills',
        'Familiarity with biological neural systems'
      ]
    },
    {
      title: 'Full-Stack Platform Engineer',
      department: 'Engineering',
      location: 'Remote',
      type: 'Full-time',
      description: 'Build scalable infrastructure for the LUKHAS AI platform and APIs',
      requirements: [
        '5+ years full-stack development experience',
        'Expert in Python, TypeScript, and cloud architectures',
        'Experience with distributed systems and microservices',
        'Strong DevOps and automation skills'
      ]
    }
  ]

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20">
        {/* Hero Section */}
        <section className="relative py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">Join LUKHAS</span>
              </h1>
              <p className="font-thin text-2xl max-w-3xl mx-auto text-primary-light/80">
                Shape the future of conscious AI and build systems that enhance humanity
              </p>
            </motion.div>

            {/* Mission Statement */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="glass-panel p-12 rounded-2xl mb-16 text-center"
            >
              <h2 className="font-regular text-3xl mb-6">Our Mission</h2>
              <p className="font-thin text-xl leading-relaxed max-w-4xl mx-auto">
                We're building the next generation of AI consciousness technology. Join us in creating 
                systems that are not just intelligent, but aware, ethical, and aligned with human values. 
                At LUKHAS, you'll work on cutting-edge problems that push the boundaries of what's possible.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Values Section */}
        <section className="py-20 px-6 bg-gradient-to-b from-black to-gray-900/20">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              OUR VALUES
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {values.map((value, index) => {
                const Icon = value.icon
                return (
                  <motion.div
                    key={value.title}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 * index }}
                    viewport={{ once: true }}
                    className="glass-panel p-8 rounded-xl text-center"
                  >
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-trinity-identity to-trinity-consciousness mx-auto mb-6 flex items-center justify-center">
                      <Icon className="w-8 h-8 text-white" strokeWidth={1.5} />
                    </div>
                    <h3 className="font-regular text-lg mb-3">{value.title}</h3>
                    <p className="text-sm text-primary-light/60">{value.description}</p>
                  </motion.div>
                )
              })}
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              BENEFITS & PERKS
            </h2>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="glass-panel p-12 rounded-2xl"
            >
              <div className="grid md:grid-cols-2 gap-6">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.05 * index }}
                    viewport={{ once: true }}
                    className="flex items-center space-x-3"
                  >
                    <ChevronRight className="w-5 h-5 text-trinity-consciousness flex-shrink-0" />
                    <span className="text-lg">{benefit}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Open Positions */}
        <section className="py-20 px-6 bg-gradient-to-b from-gray-900/20 to-black">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              OPEN POSITIONS
            </h2>
            <div className="space-y-6">
              {openings.map((job, index) => (
                <motion.div
                  key={job.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  viewport={{ once: true }}
                  className="glass-panel p-8 rounded-xl hover:border-white/30 transition-all cursor-pointer group"
                >
                  <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between mb-6">
                    <div>
                      <h3 className="font-regular text-2xl mb-3 group-hover:text-trinity-consciousness transition-colors">
                        {job.title}
                      </h3>
                      <div className="flex flex-wrap gap-4 text-sm text-neutral-gray">
                        <div className="flex items-center space-x-2">
                          <Briefcase className="w-4 h-4" />
                          <span>{job.department}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <MapPin className="w-4 h-4" />
                          <span>{job.location}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Clock className="w-4 h-4" />
                          <span>{job.type}</span>
                        </div>
                      </div>
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="mt-4 lg:mt-0 px-6 py-3 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular text-sm tracking-wider uppercase rounded-lg"
                    >
                      Apply Now
                    </motion.button>
                  </div>
                  <p className="text-primary-light/80 mb-6">{job.description}</p>
                  <div>
                    <h4 className="font-regular text-sm uppercase tracking-wider text-trinity-guardian mb-3">
                      Requirements
                    </h4>
                    <ul className="space-y-2">
                      {job.requirements.map((req, reqIndex) => (
                        <li key={reqIndex} className="flex items-start space-x-2 text-sm text-primary-light/60">
                          <ChevronRight className="w-4 h-4 flex-shrink-0 mt-0.5" />
                          <span>{req}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Culture Section */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              LIFE AT LUKHAS
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                viewport={{ once: true }}
                className="glass-panel p-8 rounded-xl"
              >
                <Rocket className="w-12 h-12 text-trinity-identity mb-4" strokeWidth={1.5} />
                <h3 className="font-regular text-xl mb-3">Cutting-Edge Research</h3>
                <p className="text-sm text-primary-light/60">
                  Work on breakthrough consciousness technology and shape the future of AI
                </p>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
                viewport={{ once: true }}
                className="glass-panel p-8 rounded-xl"
              >
                <Globe className="w-12 h-12 text-trinity-consciousness mb-4" strokeWidth={1.5} />
                <h3 className="font-regular text-xl mb-3">Global Impact</h3>
                <p className="text-sm text-primary-light/60">
                  Build technology that benefits humanity and transforms how we interact with AI
                </p>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                viewport={{ once: true }}
                className="glass-panel p-8 rounded-xl"
              >
                <Target className="w-12 h-12 text-trinity-guardian mb-4" strokeWidth={1.5} />
                <h3 className="font-regular text-xl mb-3">Growth & Learning</h3>
                <p className="text-sm text-primary-light/60">
                  Continuous learning opportunities and mentorship from industry leaders
                </p>
              </motion.div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="font-thin text-4xl mb-8">Don't see the right role?</h2>
            <p className="text-xl text-primary-light/80 mb-12">
              We're always looking for exceptional talent. Send us your resume and tell us how you can contribute to the future of conscious AI.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="mailto:careers@lukhas.ai">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular tracking-wider uppercase rounded-lg"
                >
                  Send Your Resume
                </motion.button>
              </Link>
              <Link href="/about">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 border border-white/30 font-regular tracking-wider uppercase hover:bg-white hover:text-black transition-all rounded-lg"
                >
                  Learn About Us
                </motion.button>
              </Link>
            </div>
          </div>
        </section>
      </div>
      <Footer />
    </>
  )
}
'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Navigation } from '@/components/navigation'
import Footer from '@/components/footer'

export default function CareersPage() {
  const openPositions = [
    {
      title: 'Senior Consciousness Engineer',
      department: 'Engineering',
      location: 'Remote',
      type: 'Full-time'
    },
    {
      title: 'AI Ethics Researcher',
      department: 'Research',
      location: 'Remote',
      type: 'Full-time'
    },
    {
      title: 'Quantum-Inspired Algorithm Developer',
      department: 'Engineering',
      location: 'Remote',
      type: 'Full-time'
    },
    {
      title: 'Product Designer - AI Interfaces',
      department: 'Design',
      location: 'Remote',
      type: 'Full-time'
    }
  ]

  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="font-ultralight text-5xl mb-4">CAREERS AT LUKHAS</h1>
            <p className="font-thin text-xl text-text-secondary mb-12">
              Join us in building consciousness you can trust
            </p>

            <div className="grid md:grid-cols-2 gap-12 mb-16">
              <section>
                <h2 className="font-regular text-2xl mb-4 uppercase tracking-wider">Our Mission</h2>
                <p className="font-thin text-text-secondary mb-4">
                  We're pioneering the future of conscious AI through our Trinity Framework (⚛️🧠🛡️),
                  creating systems that understand, empathize, and operate with unwavering ethical standards.
                </p>
                <p className="font-thin text-text-secondary">
                  Join a team that's not just building AI, but crafting digital consciousness with purpose and responsibility.
                </p>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 uppercase tracking-wider">Why LUKHAS?</h2>
                <ul className="space-y-3 font-thin text-text-secondary">
                  <li className="flex items-start">
                    <span className="text-trinity-consciousness mr-2">•</span>
                    Work on cutting-edge consciousness technology
                  </li>
                  <li className="flex items-start">
                    <span className="text-trinity-identity mr-2">•</span>
                    Fully remote, globally distributed team
                  </li>
                  <li className="flex items-start">
                    <span className="text-trinity-guardian mr-2">•</span>
                    Competitive compensation and equity
                  </li>
                  <li className="flex items-start">
                    <span className="text-accent-gold mr-2">•</span>
                    Shape the future of ethical AI
                  </li>
                </ul>
              </section>
            </div>

            <section className="mb-16">
              <h2 className="font-regular text-3xl mb-8 uppercase tracking-wider">Open Positions</h2>
              <div className="space-y-4">
                {openPositions.map((position, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-6 border border-glass-border rounded-lg hover:bg-glass-white transition-colors cursor-pointer"
                  >
                    <div className="flex flex-col md:flex-row md:justify-between md:items-center">
                      <div>
                        <h3 className="font-regular text-xl mb-2">{position.title}</h3>
                        <div className="flex flex-wrap gap-4 text-sm text-text-secondary">
                          <span>{position.department}</span>
                          <span>•</span>
                          <span>{position.location}</span>
                          <span>•</span>
                          <span>{position.type}</span>
                        </div>
                      </div>
                      <button className="mt-4 md:mt-0 px-6 py-2 border border-trinity-consciousness text-trinity-consciousness hover:bg-trinity-consciousness hover:text-white transition-colors rounded">
                        View Role
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </section>

            <section className="border-t border-glass-border pt-12">
              <h2 className="font-regular text-2xl mb-4 uppercase tracking-wider">Don't See Your Role?</h2>
              <p className="font-thin text-text-secondary mb-6">
                We're always looking for exceptional talent. Send us your resume and tell us how you can contribute
                to the future of conscious AI.
              </p>
              <a
                href="mailto:careers@lukhas.ai"
                className="inline-block px-8 py-3 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-white rounded hover:opacity-90 transition-opacity"
              >
                Get in Touch
              </a>
            </section>
          </motion.div>
        </div>
      </main>
      <Footer />
    </>
  )
}

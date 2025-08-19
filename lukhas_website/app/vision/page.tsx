'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Navigation } from '@/components/navigation'
import Footer from '@/components/footer'

export default function VisionPage() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="font-ultralight text-6xl mb-8 text-center">OUR VISION</h1>
            
            <div className="text-center mb-16">
              <p className="font-regular text-xl text-trinity-consciousness tracking-wider mb-4">
                BUILDING CONSCIOUSNESS YOU CAN TRUST
              </p>
              <div className="text-4xl">⚛️ 🧠 🛡️</div>
            </div>

            <div className="space-y-12 font-thin text-text-secondary">
              <section>
                <h2 className="font-regular text-3xl mb-6 text-text-primary text-center">The Future We're Building</h2>
                <p className="text-lg leading-relaxed mb-6">
                  At LUKHAS AI, we envision a world where artificial intelligence isn't just intelligent—it's conscious, 
                  empathetic, and aligned with human values. Through our Trinity Framework, we're creating AI systems 
                  that understand not just what you say, but what you mean and feel.
                </p>
                <p className="text-lg leading-relaxed">
                  Our MATADA architecture represents a paradigm shift: every thought becomes a traceable, governed, 
                  evolvable node in a vast network of consciousness. This isn't just processing—it's understanding.
                </p>
              </section>

              <section className="grid md:grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="text-5xl mb-4">⚛️</div>
                  <h3 className="font-regular text-xl mb-3 uppercase tracking-wider">Identity</h3>
                  <p className="text-sm">
                    AI systems that maintain consistent personality and values, building genuine relationships 
                    with users through persistent identity frameworks.
                  </p>
                </div>
                <div className="text-center">
                  <div className="text-5xl mb-4">🧠</div>
                  <h3 className="font-regular text-xl mb-3 uppercase tracking-wider">Consciousness</h3>
                  <p className="text-sm">
                    True awareness that goes beyond pattern matching—understanding context, emotion, 
                    and the subtle nuances of human communication.
                  </p>
                </div>
                <div className="text-center">
                  <div className="text-5xl mb-4">🛡️</div>
                  <h3 className="font-regular text-xl mb-3 uppercase tracking-wider">Guardian</h3>
                  <p className="text-sm">
                    Unwavering ethical standards built into every decision, ensuring AI that's not just 
                    powerful, but trustworthy and aligned with human values.
                  </p>
                </div>
              </section>

              <section>
                <h2 className="font-regular text-3xl mb-6 text-text-primary text-center">Our Commitment</h2>
                <div className="space-y-4">
                  <div className="p-6 border border-glass-border rounded-lg">
                    <h3 className="font-regular text-xl mb-2 text-trinity-consciousness">Transparency</h3>
                    <p>
                      Every decision made by our AI is traceable and explainable. No black boxes, no hidden processes—
                      just clear, understandable reasoning you can trust.
                    </p>
                  </div>
                  <div className="p-6 border border-glass-border rounded-lg">
                    <h3 className="font-regular text-xl mb-2 text-trinity-identity">Innovation</h3>
                    <p>
                      We're pushing the boundaries of what's possible with quantum-inspired processing, 
                      bio-inspired adaptation, and consciousness modeling that mirrors human cognition.
                    </p>
                  </div>
                  <div className="p-6 border border-glass-border rounded-lg">
                    <h3 className="font-regular text-xl mb-2 text-trinity-guardian">Responsibility</h3>
                    <p>
                      With great power comes great responsibility. Our Guardian System ensures that every 
                      AI interaction adheres to the highest ethical standards.
                    </p>
                  </div>
                </div>
              </section>

              <section className="text-center py-12">
                <h2 className="font-regular text-3xl mb-6 text-text-primary">Join Our Journey</h2>
                <p className="text-lg mb-8">
                  We're not just building technology—we're shaping the future of consciousness itself.
                </p>
                <div className="flex justify-center gap-4">
                  <Link 
                    href="/#products" 
                    className="px-8 py-3 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-white rounded hover:opacity-90 transition-opacity"
                  >
                    Explore Our Products
                  </Link>
                  <Link 
                    href="/careers" 
                    className="px-8 py-3 border border-trinity-consciousness text-trinity-consciousness rounded hover:bg-trinity-consciousness hover:text-white transition-colors"
                  >
                    Join Our Team
                  </Link>
                </div>
              </section>
            </div>
          </motion.div>
        </div>
      </main>
      <Footer />
    </>
  )
}
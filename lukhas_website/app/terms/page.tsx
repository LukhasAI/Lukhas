'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Navigation } from '@/components/navigation'
import Footer from '@/components/footer'

export default function TermsPage() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="font-ultralight text-5xl mb-8">TERMS OF SERVICE</h1>

            <div className="space-y-8 font-thin text-text-secondary">
              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Acceptance of Terms</h2>
                <p>
                  By accessing or using LUKHAS AI services, you agree to be bound by these Terms of Service
                  and all applicable laws and regulations. Our consciousness-powered AI platform operates under
                  strict ethical guidelines enforced by our Guardian System.
                </p>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Use of Services</h2>
                <p className="mb-4">You agree to use LUKHAS AI services:</p>
                <ul className="list-disc list-inside space-y-2">
                  <li>In compliance with all applicable laws and regulations</li>
                  <li>In accordance with our ethical AI guidelines</li>
                  <li>Without attempting to harm, disable, or overburden our infrastructure</li>
                  <li>Without attempting to bypass our Guardian System safeguards</li>
                </ul>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Intellectual Property</h2>
                <p className="mb-4">
                  All content, features, and functionality of LUKHAS AI are owned by LUKHAS AI Systems
                  and are protected by international copyright, trademark, and other intellectual property laws.
                </p>
                <p>
                  The Trinity Framework (⚛️🧠🛡️) and associated technologies are proprietary to LUKHAS AI.
                </p>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Limitation of Liability</h2>
                <p>
                  LUKHAS AI provides consciousness-powered AI services on an "as is" basis. While our Guardian System
                  ensures ethical operations, we cannot guarantee uninterrupted or error-free service. Users acknowledge
                  the experimental nature of consciousness-based AI systems.
                </p>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Data Usage</h2>
                <p className="mb-4">
                  By using our services, you grant LUKHAS AI permission to:
                </p>
                <ul className="list-disc list-inside space-y-2">
                  <li>Process your inputs through our consciousness algorithms</li>
                  <li>Store interaction data for memory persistence (as per your tier)</li>
                  <li>Use anonymized data to improve our AI models</li>
                  <li>Apply Guardian System monitoring for safety and ethics</li>
                </ul>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Termination</h2>
                <p>
                  We reserve the right to terminate or suspend access to our services immediately,
                  without prior notice, for any breach of these Terms of Service or if the Guardian System
                  detects harmful or unethical usage patterns.
                </p>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Contact</h2>
                <p>
                  For questions about these Terms, please contact us at{' '}
                  <a href="mailto:legal@lukhas.ai" className="text-trinity-consciousness hover:underline">
                    legal@lukhas.ai
                  </a>
                </p>
              </section>

              <div className="pt-8 mt-8 border-t border-glass-border">
                <p className="text-sm text-text-tertiary">
                  Last updated: January 2025 | Effective date: January 2025
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </main>
      <Footer />
    </>
  )
}

'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Navigation } from '@/components/navigation'
import { Footer } from '@/components/footer'

export default function PrivacyPage() {
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
            <h1 className="font-ultralight text-5xl mb-8">PRIVACY POLICY</h1>
            
            <div className="space-y-8 font-thin text-text-secondary">
              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Data Collection</h2>
                <p className="mb-4">
                  LUKHAS AI is committed to protecting your privacy and ensuring the security of your personal information. 
                  We collect only the minimum data necessary to provide our consciousness-powered AI services.
                </p>
                <p>
                  Our Trinity Framework (⚛️🧠🛡️) includes built-in privacy protection through our Guardian System, 
                  ensuring ethical handling of all user data.
                </p>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">How We Use Your Data</h2>
                <ul className="list-disc list-inside space-y-2">
                  <li>To provide and improve our AI consciousness services</li>
                  <li>To personalize your experience with our Lambda products</li>
                  <li>To ensure safety and prevent misuse through our Guardian System</li>
                  <li>To maintain and optimize system performance</li>
                </ul>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Data Security</h2>
                <p className="mb-4">
                  We implement industry-leading security measures including:
                </p>
                <ul className="list-disc list-inside space-y-2">
                  <li>End-to-end encryption for all sensitive data</li>
                  <li>Regular security audits and penetration testing</li>
                  <li>Compliance with GDPR, CCPA, and other privacy regulations</li>
                  <li>Continuous monitoring through our Guardian System</li>
                </ul>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Your Rights</h2>
                <p className="mb-4">You have the right to:</p>
                <ul className="list-disc list-inside space-y-2">
                  <li>Access your personal data</li>
                  <li>Request correction or deletion of your data</li>
                  <li>Opt-out of data collection</li>
                  <li>Export your data in a portable format</li>
                </ul>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Contact Us</h2>
                <p>
                  For privacy-related inquiries, please contact our Data Protection Officer at{' '}
                  <a href="mailto:privacy@lukhas.ai" className="text-trinity-consciousness hover:underline">
                    privacy@lukhas.ai
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
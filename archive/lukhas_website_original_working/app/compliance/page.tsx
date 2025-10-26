'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Navigation } from '@/components/navigation'
import Footer from '@/components/footer'

export default function CompliancePage() {
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
            <h1 className="font-ultralight text-5xl mb-8">COMPLIANCE & REGULATIONS</h1>
            
            <div className="space-y-8 font-thin text-text-secondary">
              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Our Commitment to Compliance</h2>
                <p className="mb-4">
                  LUKHAS AI maintains the highest standards of regulatory compliance across all jurisdictions. 
                  Our Guardian System (🛡️) ensures continuous monitoring and adherence to evolving AI regulations 
                  and ethical standards worldwide.
                </p>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Global Standards</h2>
                <div className="space-y-4">
                  <div className="p-4 border border-glass-border rounded">
                    <h3 className="font-regular text-lg mb-2">GDPR (General Data Protection Regulation)</h3>
                    <p className="text-sm">Full compliance with EU data protection and privacy regulations</p>
                  </div>
                  <div className="p-4 border border-glass-border rounded">
                    <h3 className="font-regular text-lg mb-2">CCPA (California Consumer Privacy Act)</h3>
                    <p className="text-sm">Adherence to California's comprehensive privacy rights framework</p>
                  </div>
                  <div className="p-4 border border-glass-border rounded">
                    <h3 className="font-regular text-lg mb-2">ISO/IEC 27001</h3>
                    <p className="text-sm">Information security management system certification</p>
                  </div>
                  <div className="p-4 border border-glass-border rounded">
                    <h3 className="font-regular text-lg mb-2">SOC 2 Type II</h3>
                    <p className="text-sm">Security, availability, processing integrity, confidentiality, and privacy</p>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">AI-Specific Compliance</h2>
                <ul className="list-disc list-inside space-y-2">
                  <li>EU AI Act compliance roadmap and implementation</li>
                  <li>UNESCO Recommendation on the Ethics of AI</li>
                  <li>IEEE Standards for Autonomous and Intelligent Systems</li>
                  <li>Partnership on AI Tenets adherence</li>
                </ul>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Industry-Specific Compliance</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-regular text-lg mb-2">Healthcare</h3>
                    <ul className="text-sm space-y-1">
                      <li>• HIPAA compliance</li>
                      <li>• FDA AI/ML guidance</li>
                      <li>• Medical device regulations</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-regular text-lg mb-2">Financial Services</h3>
                    <ul className="text-sm space-y-1">
                      <li>• PCI DSS compliance</li>
                      <li>• FINRA regulations</li>
                      <li>• AML/KYC requirements</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-regular text-lg mb-2">Government</h3>
                    <ul className="text-sm space-y-1">
                      <li>• FedRAMP authorization</li>
                      <li>• NIST frameworks</li>
                      <li>• FISMA compliance</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-regular text-lg mb-2">Education</h3>
                    <ul className="text-sm space-y-1">
                      <li>• FERPA compliance</li>
                      <li>• COPPA adherence</li>
                      <li>• Accessibility standards</li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Guardian System Monitoring</h2>
                <p className="mb-4">
                  Our proprietary Guardian System continuously monitors all AI operations for:
                </p>
                <ul className="list-disc list-inside space-y-2">
                  <li>Ethical drift detection (threshold: 0.15)</li>
                  <li>Bias identification and mitigation</li>
                  <li>Regulatory compliance verification</li>
                  <li>Real-time safety checks</li>
                  <li>Audit trail generation</li>
                </ul>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Audit & Reporting</h2>
                <p className="mb-4">
                  We provide comprehensive compliance reporting including:
                </p>
                <ul className="list-disc list-inside space-y-2">
                  <li>Quarterly compliance audits</li>
                  <li>Real-time compliance dashboards</li>
                  <li>Automated regulatory reporting</li>
                  <li>Third-party security assessments</li>
                </ul>
              </section>

              <section>
                <h2 className="font-regular text-2xl mb-4 text-text-primary uppercase tracking-wider">Contact Compliance Team</h2>
                <p>
                  For compliance inquiries, certifications, or audit requests, please contact our compliance team at{' '}
                  <a href="mailto:compliance@lukhas.ai" className="text-trinity-consciousness hover:underline">
                    compliance@lukhas.ai
                  </a>
                </p>
              </section>

              <div className="pt-8 mt-8 border-t border-glass-border">
                <p className="text-sm text-text-tertiary">
                  Last updated: January 2025 | This page is regularly updated to reflect current compliance status
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
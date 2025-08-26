'use client'

import { motion } from 'framer-motion'

export function AgentArchitecture() {
  return (
    <section className="relative py-32 px-6">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <p className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-4">
            MULTI-AGENT ARCHITECTURE
          </p>
          <h2 className="font-light text-display">
            25 Specialized AI Agents
          </h2>
        </motion.div>

        <div className="glass rounded-3xl p-12">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <h3 className="font-regular text-lg uppercase mb-4">TIER 1 - GENERALS</h3>
              <p className="font-light text-text-secondary">3 Trinity Commanders</p>
            </div>
            <div className="text-center">
              <h3 className="font-regular text-lg uppercase mb-4">TIER 2 - COLONELS</h3>
              <p className="font-light text-text-secondary">8 Domain Experts</p>
            </div>
            <div className="text-center">
              <h3 className="font-regular text-lg uppercase mb-4">TIER 3 - MAJORS</h3>
              <p className="font-light text-text-secondary">4 Development Leads</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

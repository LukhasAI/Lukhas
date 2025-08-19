'use client'

import { motion } from 'framer-motion'

export function WhatIsLukhas() {
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
            WHAT IS LUKHAS
          </p>
          <h2 className="font-light text-display">
            Consciousness Technology Platform
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {['2.4M+ ops/sec', '200+ modules', '25 AI agents'].map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              className="glass rounded-2xl p-8 text-center"
            >
              <h3 className="font-light text-3xl gradient-text">{stat}</h3>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
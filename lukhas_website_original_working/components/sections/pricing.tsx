'use client'

import { motion } from 'framer-motion'

const tiers = [
  { name: 'STARTER', price: '$50-299', features: ['Single product', 'Basic features', 'Community support'] },
  { name: 'PROFESSIONAL', price: '$999', features: ['3 products bundle', 'Advanced features', 'Priority support'] },
  { name: 'ENTERPRISE', price: '$5,000', features: ['All products', 'Custom integration', 'Dedicated support'] },
]

export function PricingCalculator() {
  return (
    <section id="pricing" className="relative py-32 px-6">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <p className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-4">
            PRICING
          </p>
          <h2 className="font-light text-display">
            Choose Your Tier
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {tiers.map((tier, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              className="glass rounded-3xl p-8"
            >
              <h3 className="font-regular text-xl uppercase mb-2">{tier.name}</h3>
              <p className="font-light text-3xl gradient-text mb-6">{tier.price}</p>
              <ul className="space-y-3">
                {tier.features.map((feature, j) => (
                  <li key={j} className="font-light text-text-secondary">
                    • {feature}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
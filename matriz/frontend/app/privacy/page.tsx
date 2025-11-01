'use client'

import { motion } from 'framer-motion'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Shield } from 'lucide-react'

export default function PrivacyPage() {
  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-2xl mx-auto px-6"
        >
          <Shield className="w-16 h-16 mx-auto mb-8 text-trinity-guardian" />
          <h1 className="font-ultralight text-5xl md:text-6xl mb-6">
            <span className="gradient-text">Privacy Policy</span>
          </h1>
          <p className="font-thin text-xl text-primary-light/80 mb-8">
            Your privacy is protected by our Guardian framework. Full policy coming soon.
          </p>
        </motion.div>
      </div>
      <Footer />
    </>
  )
}

'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Mail, Phone, MapPin, MessageCircle, Send, Clock } from 'lucide-react'

export default function ContactPage() {
  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20">
        <section className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">Contact Us</span>
              </h1>
              <p className="font-thin text-2xl max-w-3xl mx-auto text-primary-light/80">
                Get in touch with the LUKHAS team
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-12">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                <h2 className="font-regular text-3xl mb-8">Get In Touch</h2>
                <div className="space-y-6">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 rounded-lg bg-trinity-consciousness/10">
                      <Mail className="w-6 h-6 text-trinity-consciousness" />
                    </div>
                    <div>
                      <h3 className="font-regular text-lg mb-2">Email</h3>
                      <p className="text-primary-light/60">hello@lukhas.ai</p>
                      <p className="text-primary-light/60">support@lukhas.ai</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="p-3 rounded-lg bg-trinity-identity/10">
                      <MessageCircle className="w-6 h-6 text-trinity-identity" />
                    </div>
                    <div>
                      <h3 className="font-regular text-lg mb-2">Community</h3>
                      <p className="text-primary-light/60">Join our Discord community</p>
                      <p className="text-primary-light/60">Follow us on social media</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="p-3 rounded-lg bg-trinity-guardian/10">
                      <Clock className="w-6 h-6 text-trinity-guardian" />
                    </div>
                    <div>
                      <h3 className="font-regular text-lg mb-2">Response Time</h3>
                      <p className="text-primary-light/60">We typically respond within 24 hours</p>
                      <p className="text-primary-light/60">Enterprise customers: 4-hour SLA</p>
                    </div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                <div className="glass-panel p-8 rounded-2xl">
                  <h3 className="font-regular text-2xl mb-6">Quick Contact</h3>
                  <form className="space-y-6">
                    <div>
                      <input
                        type="text"
                        placeholder="Your Name"
                        className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                      />
                    </div>
                    <div>
                      <input
                        type="email"
                        placeholder="Your Email"
                        className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                      />
                    </div>
                    <div>
                      <select className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors">
                        <option>General Inquiry</option>
                        <option>Technical Support</option>
                        <option>Partnership</option>
                        <option>Press & Media</option>
                        <option>Careers</option>
                      </select>
                    </div>
                    <div>
                      <textarea
                        rows={4}
                        placeholder="Your Message"
                        className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors resize-none"
                      />
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="w-full px-6 py-3 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular tracking-wider uppercase rounded-lg flex items-center justify-center space-x-2"
                    >
                      <Send className="w-5 h-5" />
                      <span>Send Message</span>
                    </motion.button>
                  </form>
                </div>
              </motion.div>
            </div>
          </div>
        </section>
      </div>
      <Footer />
    </>
  )
}
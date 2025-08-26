'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import {
  ArrowLeft, User, Mail, Phone, MapPin, FileText,
  Upload, Send, CheckCircle, Briefcase, Calendar
} from 'lucide-react'

export default function CareerApplicationPage() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    location: '',
    position: '',
    experience: '',
    coverLetter: '',
    resumeFile: null as File | null,
    availableStart: '',
    expectedSalary: '',
    linkedin: '',
    github: '',
    portfolio: ''
  })

  const [submitted, setSubmitted] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setFormData(prev => ({ ...prev, resumeFile: file }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Here you would typically send the form data to your backend
    setSubmitted(true)
  }

  const positions = [
    'Senior Consciousness Engineer',
    'AI Ethics Specialist',
    'Quantum-Bio Algorithm Developer',
    'Full-Stack Platform Engineer',
    'DevOps Engineer',
    'Product Manager',
    'UI/UX Designer',
    'Technical Writer',
    'Other - Please specify in cover letter'
  ]

  if (submitted) {
    return (
      <>
        <Navigation />
        <div className="min-h-screen bg-black text-white pt-20 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className="max-w-md mx-auto text-center px-6"
          >
            <div className="glass-panel p-12 rounded-2xl">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-trinity-identity to-trinity-consciousness mx-auto mb-6 flex items-center justify-center">
                <CheckCircle className="w-10 h-10 text-white" strokeWidth={1.5} />
              </div>
              <h1 className="font-regular text-2xl mb-4">Application Submitted!</h1>
              <p className="text-primary-light/80 mb-8">
                Thank you for your interest in joining LUKHAS. We'll review your application and get back to you within 5-7 business days.
              </p>
              <div className="space-y-4">
                <Link href="/careers">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-full px-6 py-3 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular tracking-wider uppercase rounded-lg"
                  >
                    View More Positions
                  </motion.button>
                </Link>
                <Link href="/">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-full px-6 py-3 border border-white/30 font-regular tracking-wider uppercase hover:bg-white hover:text-black transition-all rounded-lg"
                  >
                    Back to Home
                  </motion.button>
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
        <Footer />
      </>
    )
  }

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20">
        {/* Header */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <Link href="/careers" className="inline-flex items-center space-x-2 mb-8 text-trinity-consciousness hover:opacity-80 transition-opacity">
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm uppercase tracking-wider">Back to Careers</span>
              </Link>

              <h1 className="font-ultralight text-5xl md:text-6xl mb-6">
                <span className="gradient-text">Join Our Team</span>
              </h1>
              <p className="font-thin text-xl text-primary-light/80 max-w-2xl">
                Ready to shape the future of conscious AI? Submit your application and become part of our mission.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Application Form */}
        <section className="pb-20 px-6">
          <div className="max-w-4xl mx-auto">
            <motion.form
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              onSubmit={handleSubmit}
              className="glass-panel p-8 rounded-2xl"
            >
              {/* Personal Information */}
              <div className="mb-8">
                <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-6">
                  Personal Information
                </h2>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="firstName" className="block text-sm font-regular mb-2">
                      First Name *
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-gray" />
                      <input
                        type="text"
                        id="firstName"
                        name="firstName"
                        required
                        value={formData.firstName}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                        placeholder="Enter your first name"
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="lastName" className="block text-sm font-regular mb-2">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      id="lastName"
                      name="lastName"
                      required
                      value={formData.lastName}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                      placeholder="Enter your last name"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6 mt-6">
                  <div>
                    <label htmlFor="email" className="block text-sm font-regular mb-2">
                      Email Address *
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-gray" />
                      <input
                        type="email"
                        id="email"
                        name="email"
                        required
                        value={formData.email}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                        placeholder="your.email@example.com"
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="phone" className="block text-sm font-regular mb-2">
                      Phone Number
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-gray" />
                      <input
                        type="tel"
                        id="phone"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                        placeholder="+1 (555) 123-4567"
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <label htmlFor="location" className="block text-sm font-regular mb-2">
                    Location
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-gray" />
                    <input
                      type="text"
                      id="location"
                      name="location"
                      value={formData.location}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                      placeholder="City, State/Country"
                    />
                  </div>
                </div>
              </div>

              {/* Position Information */}
              <div className="mb-8">
                <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-6">
                  Position & Experience
                </h2>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="position" className="block text-sm font-regular mb-2">
                      Position Applied For *
                    </label>
                    <div className="relative">
                      <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-gray" />
                      <select
                        id="position"
                        name="position"
                        required
                        value={formData.position}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors appearance-none"
                      >
                        <option value="">Select a position</option>
                        {positions.map((pos) => (
                          <option key={pos} value={pos}>{pos}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div>
                    <label htmlFor="experience" className="block text-sm font-regular mb-2">
                      Years of Experience
                    </label>
                    <select
                      id="experience"
                      name="experience"
                      value={formData.experience}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors appearance-none"
                    >
                      <option value="">Select experience level</option>
                      <option value="0-1">0-1 years</option>
                      <option value="2-3">2-3 years</option>
                      <option value="4-5">4-5 years</option>
                      <option value="6-10">6-10 years</option>
                      <option value="10+">10+ years</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Additional Information */}
              <div className="mb-8">
                <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-6">
                  Additional Information
                </h2>
                <div className="grid md:grid-cols-3 gap-6 mb-6">
                  <div>
                    <label htmlFor="availableStart" className="block text-sm font-regular mb-2">
                      Available Start Date
                    </label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-gray" />
                      <input
                        type="date"
                        id="availableStart"
                        name="availableStart"
                        value={formData.availableStart}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="linkedin" className="block text-sm font-regular mb-2">
                      LinkedIn Profile
                    </label>
                    <input
                      type="url"
                      id="linkedin"
                      name="linkedin"
                      value={formData.linkedin}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                      placeholder="https://linkedin.com/in/yourprofile"
                    />
                  </div>
                  <div>
                    <label htmlFor="github" className="block text-sm font-regular mb-2">
                      GitHub Profile
                    </label>
                    <input
                      type="url"
                      id="github"
                      name="github"
                      value={formData.github}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors"
                      placeholder="https://github.com/yourusername"
                    />
                  </div>
                </div>
              </div>

              {/* Resume Upload */}
              <div className="mb-8">
                <label htmlFor="resume" className="block text-sm font-regular mb-2">
                  Resume/CV *
                </label>
                <div className="border-2 border-dashed border-white/20 rounded-lg p-6 text-center hover:border-trinity-consciousness transition-colors">
                  <input
                    type="file"
                    id="resume"
                    name="resume"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileChange}
                    className="hidden"
                    required
                  />
                  <label htmlFor="resume" className="cursor-pointer">
                    <Upload className="w-8 h-8 mx-auto mb-4 text-neutral-gray" />
                    <p className="text-sm text-primary-light/80">
                      {formData.resumeFile ? formData.resumeFile.name : 'Click to upload your resume'}
                    </p>
                    <p className="text-xs text-neutral-gray mt-2">PDF, DOC, or DOCX (max 5MB)</p>
                  </label>
                </div>
              </div>

              {/* Cover Letter */}
              <div className="mb-8">
                <label htmlFor="coverLetter" className="block text-sm font-regular mb-2">
                  Cover Letter *
                </label>
                <div className="relative">
                  <FileText className="absolute left-3 top-3 w-5 h-5 text-neutral-gray" />
                  <textarea
                    id="coverLetter"
                    name="coverLetter"
                    required
                    rows={6}
                    value={formData.coverLetter}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 bg-black/50 border border-white/10 rounded-lg focus:outline-none focus:border-trinity-consciousness transition-colors resize-none"
                    placeholder="Tell us why you're interested in this position and what makes you a great fit for LUKHAS..."
                  />
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex flex-col sm:flex-row gap-4 justify-end">
                <Link href="/careers">
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 border border-white/30 font-regular tracking-wider uppercase hover:bg-white hover:text-black transition-all rounded-lg"
                  >
                    Cancel
                  </motion.button>
                </Link>
                <motion.button
                  type="submit"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular tracking-wider uppercase rounded-lg flex items-center space-x-2"
                >
                  <Send className="w-5 h-5" />
                  <span>Submit Application</span>
                </motion.button>
              </div>
            </motion.form>
          </div>
        </section>
      </div>
      <Footer />
    </>
  )
}

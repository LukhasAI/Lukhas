'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Mail, Lock, Eye, EyeOff, Github } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'

interface LukhasIDModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function LukhasIDModal({ isOpen, onClose }: LukhasIDModalProps) {
  const [isSignUp, setIsSignUp] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)

  const { login, register } = useAuth()

  // Clear form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        email: '',
        username: '',
        password: '',
        confirmPassword: ''
      })
      setErrors({})
      setIsLoading(false)
    }
  }, [isOpen])

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format'
    }

    // Username validation (for sign up)
    if (isSignUp && !formData.username) {
      newErrors.username = 'Username is required'
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (isSignUp && formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    }

    // Confirm password validation (for sign up)
    if (isSignUp && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setIsLoading(true)

    try {
      if (isSignUp) {
        await register({ email: formData.email, password: formData.password, username: formData.username })
      } else {
        await login({ email: formData.email, password: formData.password, rememberMe })
      }
      onClose()
    } catch (error) {
      setErrors({ general: error instanceof Error ? error.message : 'Authentication failed' })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSocialLogin = (provider: string) => {
    // Mock social login for now
    console.log(`Social login with ${provider}`)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-panel rounded-2xl p-8 w-full max-w-md relative"
            >
              {/* Close Button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/10 transition-colors"
              >
                <X size={20} />
              </button>

              {/* LUKHAS Branding */}
              <div className="text-center mb-8">
                <motion.h1
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="font-ultralight text-4xl mb-2"
                >
                  LUKHAS
                </motion.h1>
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="font-thin text-sm tracking-[0.3em] uppercase text-neutral-gray"
                >
                  {isSignUp ? 'Create Your ID' : 'Authenticate'}
                </motion.p>
              </div>

              {/* Trinity Framework Symbols */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="flex justify-center space-x-6 mb-8"
              >
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 rounded-full bg-trinity-identity/20 flex items-center justify-center mb-2 trinity-identity-glow">
                    <span className="text-xl">⚛️</span>
                  </div>
                  <span className="text-xs font-thin text-trinity-identity">Identity</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 rounded-full bg-trinity-consciousness/20 flex items-center justify-center mb-2 trinity-consciousness-glow">
                    <span className="text-xl">🧠</span>
                  </div>
                  <span className="text-xs font-thin text-trinity-consciousness">Consciousness</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 rounded-full bg-trinity-guardian/20 flex items-center justify-center mb-2 trinity-guardian-glow">
                    <span className="text-xl">🛡️</span>
                  </div>
                  <span className="text-xs font-thin text-trinity-guardian">Guardian</span>
                </div>
              </motion.div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* General Error */}
                {errors.general && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-red-400 text-sm text-center"
                  >
                    {errors.general}
                  </motion.div>
                )}

                {/* Email Field */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                  className="space-y-2"
                >
                  <label className="font-thin text-sm text-neutral-gray">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-gray" size={16} />
                    <input
                      id="lukhas-id-email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      autoComplete="email"
                      className={`w-full bg-white/5 border rounded-lg pl-10 pr-4 py-3 font-thin text-sm focus:outline-none focus:ring-2 transition-all ${
                        errors.email
                          ? 'border-red-400 focus:ring-red-400/50'
                          : 'border-white/20 focus:ring-trinity-consciousness/50'
                      }`}
                      placeholder="your@email.com"
                    />
                  </div>
                  {errors.email && (
                    <p className="text-red-400 text-xs">{errors.email}</p>
                  )}
                </motion.div>

                {/* Username Field (Sign Up Only) */}
                {isSignUp && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                    className="space-y-2"
                  >
                    <label className="font-thin text-sm text-neutral-gray">Username</label>
                    <input
                      id="lukhas-id-username"
                      name="username"
                      type="text"
                      value={formData.username}
                      onChange={(e) => handleInputChange('username', e.target.value)}
                      autoComplete="username"
                      className={`w-full bg-white/5 border rounded-lg px-4 py-3 font-thin text-sm focus:outline-none focus:ring-2 transition-all ${
                        errors.username
                          ? 'border-red-400 focus:ring-red-400/50'
                          : 'border-white/20 focus:ring-trinity-consciousness/50'
                      }`}
                      placeholder="yourusername"
                    />
                    {errors.username && (
                      <p className="text-red-400 text-xs">{errors.username}</p>
                    )}
                  </motion.div>
                )}

                {/* Password Field */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 }}
                  className="space-y-2"
                >
                  <label className="font-thin text-sm text-neutral-gray">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-gray" size={16} />
                    <input
                      id="lukhas-id-password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      autoComplete="new-password"
                      className={`w-full bg-white/5 border rounded-lg pl-10 pr-12 py-3 font-thin text-sm focus:outline-none focus:ring-2 transition-all ${
                        errors.password
                          ? 'border-red-400 focus:ring-red-400/50'
                          : 'border-white/20 focus:ring-trinity-consciousness/50'
                      }`}
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-gray hover:text-primary-light transition-colors"
                    >
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {errors.password && (
                    <p className="text-red-400 text-xs">{errors.password}</p>
                  )}
                </motion.div>

                {/* Confirm Password Field (Sign Up Only) */}
                {isSignUp && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7 }}
                    className="space-y-2"
                  >
                    <label className="font-thin text-sm text-neutral-gray">Confirm Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-gray" size={16} />
                      <input
                        id="lukhas-id-confirm-password"
                        name="confirmPassword"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.confirmPassword}
                        onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                        autoComplete="new-password"
                        className={`w-full bg-white/5 border rounded-lg pl-10 pr-4 py-3 font-thin text-sm focus:outline-none focus:ring-2 transition-all ${
                          errors.confirmPassword
                            ? 'border-red-400 focus:ring-red-400/50'
                            : 'border-white/20 focus:ring-trinity-consciousness/50'
                        }`}
                        placeholder="••••••••"
                      />
                    </div>
                    {errors.confirmPassword && (
                      <p className="text-red-400 text-xs">{errors.confirmPassword}</p>
                    )}
                  </motion.div>
                )}

                {/* Remember Me (Login Only) */}
                {!isSignUp && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7 }}
                    className="flex items-center space-x-2"
                  >
                    <input
                      type="checkbox"
                      id="rememberMe"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="rounded border-white/20 bg-white/5 text-trinity-consciousness focus:ring-trinity-consciousness/50"
                    />
                    <label htmlFor="rememberMe" className="font-thin text-sm">
                      Remember me
                    </label>
                  </motion.div>
                )}

                {/* Submit Button */}
                <motion.button
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 }}
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-trinity-identity to-trinity-consciousness hover:from-trinity-consciousness hover:to-trinity-guardian text-primary-dark font-regular text-sm tracking-[0.1em] uppercase py-3 rounded-lg transition-all duration-300 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-4 h-4 border-2 border-primary-dark/20 border-t-primary-dark rounded-full animate-spin" />
                      <span>Processing...</span>
                    </div>
                  ) : (
                    isSignUp ? 'Create LUKHAS ID' : 'Authenticate'
                  )}
                </motion.button>
              </form>

              {/* Social Login */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 }}
                className="mt-8"
              >
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-white/20" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-primary-dark text-neutral-gray font-thin">
                      or continue with
                    </span>
                  </div>
                </div>

                <div className="mt-6 flex space-x-4">
                  <button
                    type="button"
                    onClick={() => handleSocialLogin('github')}
                    className="flex-1 flex items-center justify-center space-x-2 bg-white/5 hover:bg-white/10 border border-white/20 rounded-lg py-3 transition-colors"
                  >
                    <Github size={16} />
                    <span className="font-thin text-sm">GitHub</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleSocialLogin('google')}
                    className="flex-1 flex items-center justify-center space-x-2 bg-white/5 hover:bg-white/10 border border-white/20 rounded-lg py-3 transition-colors"
                  >
                    <div className="w-4 h-4 bg-gradient-to-r from-red-500 to-yellow-500 rounded-full" />
                    <span className="font-thin text-sm">Google</span>
                  </button>
                </div>
              </motion.div>

              {/* Toggle Sign Up/Login */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.0 }}
                className="mt-8 text-center"
              >
                <p className="font-thin text-sm text-neutral-gray">
                  {isSignUp ? 'Already have a LUKHAS ID?' : "Don't have a LUKHAS ID?"}{' '}
                  <button
                    type="button"
                    onClick={() => setIsSignUp(!isSignUp)}
                    className="text-trinity-consciousness hover:text-trinity-identity transition-colors"
                  >
                    {isSignUp ? 'Sign In' : 'Create One'}
                  </button>
                </p>
              </motion.div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

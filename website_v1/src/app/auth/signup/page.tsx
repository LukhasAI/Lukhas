'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardTitle } from '@/components/ui/Card';
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight,
  Github,
  Chrome,
  Shield,
  User,
  CheckCircle,
  Sparkles
} from 'lucide-react';
import Link from 'next/link';

export default function SignupPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [agreeToTerms, setAgreeToTerms] = useState(false);

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Basic validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      setIsLoading(false);
      return;
    }

    if (!agreeToTerms) {
      setError('Please agree to the Terms of Service and Privacy Policy');
      setIsLoading(false);
      return;
    }

    // TODO: Implement real registration
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      // Simulate successful registration
      window.location.href = '/auth/welcome';
    } catch (err) {
      setError('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialSignup = (provider: string) => {
    // TODO: Implement social signup
    console.log(`Sign up with ${provider}`);
  };

  const passwordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const getStrengthColor = (strength: number) => {
    if (strength < 2) return 'bg-red-500';
    if (strength < 4) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStrengthText = (strength: number) => {
    if (strength < 2) return 'Weak';
    if (strength < 4) return 'Medium';
    return 'Strong';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--background)] via-[#0A0F1C] to-[var(--background)] flex items-center justify-center p-4">
      
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 right-1/4 w-64 h-64 bg-[var(--accent)]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-[var(--gradient-end)]/3 rounded-full blur-3xl" />
      </div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 w-full max-w-md"
      >
        <Card className="p-8 bg-[var(--surface)]/80 backdrop-blur-xl border-[var(--border)]">
          
          {/* Header */}
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-3 mb-6 group">
              <div className="w-10 h-10 bg-gradient-to-br from-[var(--gradient-start)] to-[var(--gradient-end)] rounded-xl flex items-center justify-center">
                <motion.div
                  className="text-white font-bold"
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                >
                  Λ
                </motion.div>
              </div>
              <div className="text-left">
                <div className="text-xl text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors" style={{ fontFamily: 'Helvetica Neue, -apple-system, BlinkMacSystemFont, sans-serif', fontWeight: 100 }}>
                  LUKHΛS ΛI
                </div>
                <div className="text-xs text-[var(--text-secondary)] -mt-1">
                  Consciousness Technology
                </div>
              </div>
            </Link>
            
            <CardTitle className="text-2xl font-semibold text-[var(--text-primary)] mb-2">
              Join the Consciousness Revolution
            </CardTitle>
            <p className="text-[var(--text-secondary)]">
              Create your account and unlock AI that truly understands
            </p>
          </div>

          {/* Benefits */}
          <div className="mb-6 p-4 bg-gradient-to-r from-[var(--accent)]/10 to-[var(--gradient-end)]/10 border border-[var(--accent)]/20 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={16} className="text-[var(--accent)]" />
              <span className="text-sm font-medium text-[var(--text-primary)]">What you'll get:</span>
            </div>
            <ul className="text-xs text-[var(--text-secondary)] space-y-1">
              <li className="flex items-center gap-2">
                <CheckCircle size={12} className="text-green-400" />
                Full access to LUKHAS Studio
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle size={12} className="text-green-400" />
                Consciousness-aware AI workspace
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle size={12} className="text-green-400" />
                Advanced identity protection
              </li>
            </ul>
          </div>

          {/* Social Signup Options */}
          <div className="grid grid-cols-2 gap-3 mb-6">
            <Button
              variant="secondary"
              className="gap-2"
              onClick={() => handleSocialSignup('github')}
            >
              <Github size={16} />
              GitHub
            </Button>
            <Button
              variant="secondary"
              className="gap-2"
              onClick={() => handleSocialSignup('google')}
            >
              <Chrome size={16} />
              Google
            </Button>
          </div>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[var(--border)]" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-[var(--surface)] text-[var(--text-secondary)]">
                or create with email
              </span>
            </div>
          </div>

          {/* Signup Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="name" className="text-sm font-medium text-[var(--text-primary)]">
                Full Name
              </label>
              <div className="relative">
                <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]" />
                <input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-[var(--background)]/50 border border-[var(--border)] rounded-lg focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20 transition-all text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]"
                  placeholder="Your full name"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-[var(--text-primary)]">
                Email Address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]" />
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-[var(--background)]/50 border border-[var(--border)] rounded-lg focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20 transition-all text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]"
                  placeholder="your@email.com"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-[var(--text-primary)]">
                Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  className="w-full pl-10 pr-12 py-3 bg-[var(--background)]/50 border border-[var(--border)] rounded-lg focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20 transition-all text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]"
                  placeholder="Choose a strong password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              
              {/* Password Strength */}
              {formData.password && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1 bg-[var(--border)] rounded-full overflow-hidden">
                      <div 
                        className={`h-full transition-all duration-300 ${getStrengthColor(passwordStrength(formData.password))}`}
                        style={{ width: `${(passwordStrength(formData.password) / 5) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-[var(--text-secondary)]">
                      {getStrengthText(passwordStrength(formData.password))}
                    </span>
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="text-sm font-medium text-[var(--text-primary)]">
                Confirm Password
              </label>
              <div className="relative">
                <Shield size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]" />
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={(e) => handleChange('confirmPassword', e.target.value)}
                  className="w-full pl-10 pr-12 py-3 bg-[var(--background)]/50 border border-[var(--border)] rounded-lg focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20 transition-all text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]"
                  placeholder="Confirm your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                >
                  {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm"
              >
                {error}
              </motion.div>
            )}

            <div className="flex items-start gap-3 text-sm">
              <input
                id="terms"
                type="checkbox"
                checked={agreeToTerms}
                onChange={(e) => setAgreeToTerms(e.target.checked)}
                className="w-4 h-4 mt-0.5 rounded border-[var(--border)] bg-[var(--background)] checked:bg-[var(--accent)] checked:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20"
              />
              <label htmlFor="terms" className="text-[var(--text-secondary)] leading-relaxed">
                I agree to the{' '}
                <Link href="/legal/terms" className="text-[var(--accent)] hover:text-[var(--accent-hover)] transition-colors">
                  Terms of Service
                </Link>
                {' '}and{' '}
                <Link href="/legal/privacy" className="text-[var(--accent)] hover:text-[var(--accent-hover)] transition-colors">
                  Privacy Policy
                </Link>
              </label>
            </div>

            <Button
              type="submit"
              size="lg"
              className="w-full gap-2 bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] hover:from-[var(--accent-hover)] hover:to-[var(--gradient-end)]"
              disabled={isLoading}
            >
              {isLoading ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                />
              ) : (
                <ArrowRight size={16} />
              )}
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>

          {/* Footer */}
          <div className="text-center mt-6 pt-4 border-t border-[var(--border)]">
            <p className="text-[var(--text-secondary)] text-sm">
              Already have an account?{' '}
              <Link href="/auth/login" className="text-[var(--accent)] hover:text-[var(--accent-hover)] transition-colors font-medium">
                Sign in instead
              </Link>
            </p>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
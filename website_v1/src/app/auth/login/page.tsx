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
  Zap
} from 'lucide-react';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const { authService } = await import('@/lib/auth');
      
      const authResponse = await authService.login({
        email,
        password,
        ipAddress: 'client',
        userAgent: navigator.userAgent,
      });

      if (authResponse.user) {
        // Successful login
        window.location.href = '/studio';
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (provider: string) => {
    // TODO: Implement social login
    console.log(`Login with ${provider}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--background)] via-[#0A0F1C] to-[var(--background)] flex items-center justify-center p-4">
      
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-[var(--accent)]/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[var(--gradient-end)]/3 rounded-full blur-3xl" />
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
              </div>
            </Link>
            
            <CardTitle className="text-2xl font-semibold text-[var(--text-primary)] mb-2">
              Welcome Back
            </CardTitle>
            <p className="text-[var(--text-secondary)]">
              Sign in to access your consciousness-aware workspace
            </p>
          </div>

          {/* Social Login Options */}
          <div className="grid grid-cols-2 gap-3 mb-6">
            <Button
              variant="secondary"
              className="gap-2"
              onClick={() => handleSocialLogin('github')}
            >
              <Github size={16} />
              GitHub
            </Button>
            <Button
              variant="secondary"
              className="gap-2"
              onClick={() => handleSocialLogin('google')}
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
                or continue with email
              </span>
            </div>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-[var(--text-primary)]">
                Email Address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-[var(--background)]/50 border border-[var(--border)] rounded-lg focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20 transition-all text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]"
                  placeholder="demo@lukhas.ai"
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
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-12 py-3 bg-[var(--background)]/50 border border-[var(--border)] rounded-lg focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20 transition-all text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]"
                  placeholder="consciousness"
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

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-[var(--border)] bg-[var(--background)] checked:bg-[var(--accent)] checked:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20"
                />
                <span className="text-[var(--text-secondary)]">Remember me</span>
              </label>
              <Link href="/auth/forgot-password" className="text-[var(--accent)] hover:text-[var(--accent-hover)] transition-colors">
                Forgot password?
              </Link>
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
              {isLoading ? 'Signing In...' : 'Sign In'}
            </Button>
          </form>

          {/* Demo Info */}
          <div className="mt-6 p-4 bg-[var(--accent)]/10 border border-[var(--accent)]/20 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Zap size={16} className="text-[var(--accent)]" />
              <span className="text-sm font-medium text-[var(--text-primary)]">Demo Access</span>
            </div>
            <div className="text-xs text-[var(--text-secondary)] space-y-1">
              <div>Email: <code className="text-[var(--accent)]">demo@lukhas.ai</code></div>
              <div>Password: <code className="text-[var(--accent)]">consciousness</code></div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-6 pt-4 border-t border-[var(--border)]">
            <p className="text-[var(--text-secondary)] text-sm">
              Don't have an account?{' '}
              <Link href="/auth/signup" className="text-[var(--accent)] hover:text-[var(--accent-hover)] transition-colors font-medium">
                Sign up for free
              </Link>
            </p>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
import { Canvas } from '@react-three/fiber'
import { MorphingParticles } from '@lukhas/ui'
import { Button, GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement authentication
    console.log('Login attempt:', { email, password })
  }

  return (
    <div className="min-h-screen bg-consciousness-deep flex items-center justify-center px-6 relative overflow-hidden">
      {/* Background Particle Cloud */}
      <div className="absolute inset-0 z-0 opacity-30">
        <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
          <MorphingParticles
            shape="identity"
            color="#9333EA"
            rotationSpeed={0.3}
            particleCount={2048}
            baseParticleSize={4.0}
          />
        </Canvas>
      </div>

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-block">
            <h1 className="text-4xl font-light tracking-[0.15em] text-awareness-silver mb-2">
              LUKHAS<span className="text-security-purple">.ID</span>
            </h1>
          </Link>
          <p className="text-awareness-silver/70 tracking-wide">
            Sign in to your consciousness signature
          </p>
        </div>

        <GlassCard className="p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-awareness-silver/90 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-consciousness-deep/50 border border-security-purple/30 rounded-lg
                         text-awareness-silver placeholder-awareness-silver/40
                         focus:outline-none focus:ring-2 focus:ring-security-purple focus:border-transparent
                         transition-all"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-awareness-silver/90 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 bg-consciousness-deep/50 border border-security-purple/30 rounded-lg
                         text-awareness-silver placeholder-awareness-silver/40
                         focus:outline-none focus:ring-2 focus:ring-security-purple focus:border-transparent
                         transition-all"
                placeholder="••••••••"
              />
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-awareness-silver/80 cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-security-purple/30 bg-consciousness-deep/50
                           text-security-purple focus:ring-security-purple focus:ring-2"
                />
                <span>Remember this device</span>
              </label>
              <a href="#" className="text-security-purple hover:text-security-trust transition-colors">
                Forgot password?
              </a>
            </div>

            <Button
              type="submit"
              className="w-full bg-security-gradient text-white py-3 text-lg"
            >
              Sign In
            </Button>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-awareness-silver/20"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-consciousness-deep/80 text-awareness-silver/60">
                  Or continue with
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Button
                type="button"
                variant="outline"
                className="border-security-purple/30 hover:border-security-purple hover:bg-security-purple/10"
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                </svg>
                Passkey
              </Button>
              <Button
                type="button"
                variant="outline"
                className="border-security-purple/30 hover:border-security-purple hover:bg-security-purple/10"
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.8 10.2c-.1-.1-.2-.2-.3-.2-.7-.4-1.5-.6-2.3-.6-1.3 0-2.5.5-3.4 1.4-.9.9-1.4 2.1-1.4 3.4 0 1.3.5 2.5 1.4 3.4.9.9 2.1 1.4 3.4 1.4.8 0 1.6-.2 2.3-.6.1-.1.2-.1.3-.2v.8c0 .6-.4 1-1 1h-4c-.6 0-1-.4-1-1v-8c0-.6.4-1 1-1h4c.6 0 1 .4 1 1v.3z"/>
                </svg>
                Biometric
              </Button>
            </div>
          </form>

          <div className="mt-6 pt-6 border-t border-awareness-silver/10 text-center">
            <p className="text-awareness-silver/70">
              Don't have a ΛiD?{' '}
              <Link to="/register" className="text-security-purple hover:text-security-trust transition-colors font-medium">
                Create one now
              </Link>
            </p>
          </div>
        </GlassCard>

        {/* Trust Indicators */}
        <div className="mt-8 flex justify-center gap-6 text-xs text-awareness-silver/50">
          <span className="flex items-center gap-1">
            <span className="inline-block w-2 h-2 bg-verified-green rounded-full"></span>
            SOC 2 Target
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-2 h-2 bg-verified-green rounded-full"></span>
            Zero-Knowledge
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-2 h-2 bg-verified-green rounded-full"></span>
            End-to-End Encrypted
          </span>
        </div>
      </div>
    </div>
  )
}

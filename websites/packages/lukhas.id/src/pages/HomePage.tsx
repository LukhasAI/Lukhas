import { Canvas } from '@react-three/fiber'
import { MorphingParticles } from '@lukhas/ui'
import { Button, GlassCard, Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer } from '@lukhas/ui'
import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-security-purple/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-security-purple">.ID</span>
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="#security">Security</HeaderNavLink>
          <HeaderNavLink href="#privacy">Privacy</HeaderNavLink>
          <HeaderNavLink href="#enterprise">Enterprise</HeaderNavLink>
          <HeaderNavLink href="#developers">Developers</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <Link to="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link to="/register">
            <Button className="bg-security-gradient text-white">
              Create ΛiD
            </Button>
          </Link>
        </HeaderActions>
      </Header>

      {/* Hero Section with Identity Particle Cloud */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* WebGL Particle Background */}
        <div className="absolute inset-0 z-0">
          <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
            <MorphingParticles
              shape="identity"
              color="#9333EA"
              rotationSpeed={0.4}
              particleCount={4096}
              baseParticleSize={5.0}
            />
          </Canvas>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 text-center px-6 max-w-5xl mx-auto">
          <h1 className="text-6xl md:text-8xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            YOUR CONSCIOUSNESS
            <br />
            <span className="text-transparent bg-clip-text bg-security-gradient">
              SIGNATURE
            </span>
          </h1>

          <p className="text-xl md:text-2xl font-light tracking-wide mb-4 text-awareness-silver/80 max-w-3xl mx-auto">
            Unique, Secure, Sovereign
          </p>

          <p className="text-lg md:text-xl font-light tracking-wide mb-12 text-awareness-silver/60 max-w-3xl mx-auto">
            ΛiD is your unique consciousness signature in the LUKHAS ecosystem—secure,
            private, and entirely yours.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            <Link to="/register">
              <Button size="lg" className="bg-security-gradient text-white px-8 py-6 text-lg">
                Create Your ΛiD
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="px-8 py-6 text-lg border-security-purple text-security-purple">
                Sign In
              </Button>
            </Link>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap justify-center gap-6 text-sm text-awareness-silver/60 tracking-wide">
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-verified-green rounded-full"></span>
              Trusted by Fortune 500
            </span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-verified-green rounded-full"></span>
              SOC 2 Type II
            </span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-verified-green rounded-full"></span>
              ISO 27001
            </span>
          </div>
        </div>
      </section>

      {/* What is ΛiD? */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              What is <span className="text-security-purple">ΛiD</span>?
            </h2>
            <p className="text-xl text-awareness-silver/80 max-w-3xl mx-auto">
              ΛiD (Lambda ID) is your unified identity for the LUKHAS consciousness ecosystem.
              One identity, infinite possibilities.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <GlassCard>
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">🔐</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Zero-Knowledge Architecture
                </h3>
                <p className="text-awareness-silver/70">
                  Privacy-first design with end-to-end encryption. We can't see your data.
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">⚛️</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Consciousness Signature
                </h3>
                <p className="text-awareness-silver/70">
                  Your unique identity pattern—not just credentials, but authentic self-expression.
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">🌐</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Single Sign-On
                </h3>
                <p className="text-awareness-silver/70">
                  One identity across the entire LUKHAS universe. Sign in once, access everything.
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Security Features */}
      <section id="security" className="py-24 px-6 bg-gradient-to-b from-consciousness-deep/80 to-consciousness-deep">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Enterprise-Grade <span className="text-security-purple">Security</span>
            </h2>
            <p className="text-xl text-awareness-silver/80 max-w-3xl mx-auto">
              The same security Fortune 500 companies trust
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <GlassCard>
              <div className="p-8">
                <h3 className="text-2xl font-light tracking-wide mb-4 text-security-purple flex items-center gap-3">
                  <span className="text-3xl">🔑</span>
                  Multi-Factor Authentication
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  WebAuthn/FIDO2 passwordless authentication with hardware security keys,
                  biometric options, and backup codes.
                </p>
                <ul className="space-y-2 text-awareness-silver/70">
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>Passkey support (Face ID, Touch ID, Windows Hello)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>Hardware security keys (YubiKey, Titan)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>Time-based one-time passwords (TOTP)</span>
                  </li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <h3 className="text-2xl font-light tracking-wide mb-4 text-security-purple flex items-center gap-3">
                  <span className="text-3xl">🛡️</span>
                  Guardian Protection
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Constitutional AI continuously monitors for anomalies and protects
                  your identity 24/7.
                </p>
                <ul className="space-y-2 text-awareness-silver/70">
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>Real-time threat detection and prevention</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>Behavioral biometric anomaly detection</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>Automatic account recovery protection</span>
                  </li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <h3 className="text-2xl font-light tracking-wide mb-4 text-security-purple flex items-center gap-3">
                  <span className="text-3xl">🔒</span>
                  End-to-End Encryption
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  All identity data encrypted at rest and in transit with industry-leading
                  algorithms.
                </p>
                <ul className="space-y-2 text-awareness-silver/70">
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>AES-256-GCM encryption for data at rest</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>TLS 1.3 for data in transit</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>Quantum-resistant cryptography ready</span>
                  </li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <h3 className="text-2xl font-light tracking-wide mb-4 text-security-purple flex items-center gap-3">
                  <span className="text-3xl">📊</span>
                  Compliance & Audits
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Regular third-party security audits and compliance with global privacy
                  regulations.
                </p>
                <ul className="space-y-2 text-awareness-silver/70">
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>SOC 2 Type II certified</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>ISO 27001 compliant</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-verified-green mt-1">✓</span>
                    <span>GDPR & CCPA compliant</span>
                  </li>
                </ul>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-security-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Ready to Create Your ΛiD?
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Join thousands who trust ΛiD for secure, private identity management
          </p>
          <Link to="/register">
            <Button size="lg" className="bg-white text-security-purple px-12 py-6 text-lg hover:bg-awareness-silver">
              Create Free ΛiD
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Product</h3>
          <ul className="space-y-2">
            <li><a href="#security" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">Security</a></li>
            <li><a href="#privacy" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">Privacy</a></li>
            <li><a href="#features" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">Features</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">For Developers</h3>
          <ul className="space-y-2">
            <li><a href="#developers" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">API Docs</a></li>
            <li><a href="#integration" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">Integration</a></li>
            <li><a href="#sdk" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">SDK</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Company</h3>
          <ul className="space-y-2">
            <li><a href="#about" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">About</a></li>
            <li><a href="#trust" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">Trust Center</a></li>
            <li><a href="#contact" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">Contact</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Legal</h3>
          <ul className="space-y-2">
            <li><a href="#privacy-policy" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">Privacy Policy</a></li>
            <li><a href="#terms" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">Terms of Service</a></li>
            <li><a href="#compliance" className="text-sm text-awareness-silver/70 hover:text-security-purple transition-colors">Compliance</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

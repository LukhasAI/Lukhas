import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Cookie, Shield, Settings, CheckCircle, XCircle } from 'lucide-react'

export default function CookiePolicyPage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-trust-blue/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-trust-blue">.EU</span>
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="/about">About</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.dev">Developers</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.com">Enterprise</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
        </HeaderActions>
      </Header>

      <section className="pt-32 pb-16 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="mb-6 flex justify-center">
            <Cookie className="w-16 h-16 text-trust-blue animate-pulse" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Cookie Policy
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-3xl mx-auto mb-4">
            How we use cookies and similar tracking technologies
          </p>
          <p className="text-sm text-awareness-silver/60">
            Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
      </section>

      <section className="py-8 px-6">
        <div className="max-w-5xl mx-auto space-y-8">

          <GlassCard className="border-trust-blue/30">
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">What Are Cookies?</h2>
              <p className="text-awareness-silver/80 leading-relaxed">
                Cookies are small text files stored on your device when you visit our website. They help us provide a better
                user experience by remembering your preferences and analyzing how you use our Services.
              </p>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <CheckCircle className="w-6 h-6 text-trust-blue" />
                Essential Cookies
              </h2>
              <p className="text-awareness-silver/80 leading-relaxed mb-4">
                These cookies are necessary for the website to function and cannot be disabled. They include:
              </p>
              <ul className="space-y-3 text-awareness-silver/80">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                  <div>
                    <strong className="text-awareness-silver">Authentication:</strong> Remember your login session via ΛiD
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                  <div>
                    <strong className="text-awareness-silver">Security:</strong> Protect against CSRF attacks and fraud
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                  <div>
                    <strong className="text-awareness-silver">Session Management:</strong> Maintain your preferences during a session
                  </div>
                </li>
              </ul>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <Settings className="w-6 h-6 text-trust-blue" />
                Performance & Analytics Cookies
              </h2>
              <p className="text-awareness-silver/80 leading-relaxed mb-4">
                These cookies help us understand how visitors use our Services (with your consent):
              </p>
              <ul className="space-y-3 text-awareness-silver/80">
                <li className="flex items-start gap-3">
                  <Settings className="w-5 h-5 text-trust-blue flex-shrink-0 mt-1" />
                  <div>
                    <strong className="text-awareness-silver">Usage Analytics:</strong> Track page views, feature usage, and navigation patterns
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <Settings className="w-5 h-5 text-trust-blue flex-shrink-0 mt-1" />
                  <div>
                    <strong className="text-awareness-silver">Performance Monitoring:</strong> Measure load times and optimize experience
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <Settings className="w-5 h-5 text-trust-blue flex-shrink-0 mt-1" />
                  <div>
                    <strong className="text-awareness-silver">Error Tracking:</strong> Identify and fix technical issues
                  </div>
                </li>
              </ul>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                Functional Cookies
              </h2>
              <p className="text-awareness-silver/80 leading-relaxed mb-4">
                These cookies enhance functionality and personalization (optional):
              </p>
              <ul className="space-y-3 text-awareness-silver/80">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-lambda-gold flex-shrink-0 mt-1" />
                  <div>
                    <strong className="text-awareness-silver">Language Preferences:</strong> Remember your language selection
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-lambda-gold flex-shrink-0 mt-1" />
                  <div>
                    <strong className="text-awareness-silver">Theme Settings:</strong> Save dark/light mode preferences
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-lambda-gold flex-shrink-0 mt-1" />
                  <div>
                    <strong className="text-awareness-silver">UI Customization:</strong> Remember dashboard layouts and settings
                  </div>
                </li>
              </ul>
            </div>
          </GlassCard>

          <GlassCard className="border-warning-amber/20">
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <XCircle className="w-6 h-6 text-warning-amber" />
                What We DON'T Do
              </h2>
              <ul className="space-y-3 text-awareness-silver/80">
                <li className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                  <div>We do not use advertising or marketing cookies</div>
                </li>
                <li className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                  <div>We do not sell cookie data to third parties</div>
                </li>
                <li className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                  <div>We do not track you across other websites</div>
                </li>
                <li className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                  <div>We do not use cookies for behavioral profiling without consent</div>
                </li>
              </ul>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <Settings className="w-6 h-6 text-trust-blue" />
                Managing Cookie Preferences
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  You have control over cookie settings:
                </p>
                <ul className="space-y-2 list-disc list-inside ml-4">
                  <li>Use our Cookie Preferences Center (available in account settings)</li>
                  <li>Configure your browser to block or delete cookies</li>
                  <li>Opt out of analytics cookies while keeping essential ones</li>
                  <li>Clear cookies at any time through browser settings</li>
                </ul>
                <p className="leading-relaxed mt-4">
                  Note: Blocking essential cookies may impact functionality.
                </p>
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                Third-Party Services
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  We use the following third-party services that may set cookies:
                </p>
                <ul className="space-y-3">
                  <li>
                    <strong className="text-awareness-silver">Analytics:</strong> Google Analytics (anonymized IP)
                  </li>
                  <li>
                    <strong className="text-awareness-silver">Infrastructure:</strong> Cloudflare (security and performance)
                  </li>
                  <li>
                    <strong className="text-awareness-silver">Authentication:</strong> ΛiD authentication service
                  </li>
                </ul>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="border-trust-blue/30">
            <div className="p-8 text-center">
              <h2 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                Questions About Cookies?
              </h2>
              <p className="text-awareness-silver/80 mb-6">
                Contact us for cookie-related inquiries
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <a href="mailto:privacy@lukhas.eu">
                  <Button className="bg-trust-blue text-white">
                    Email: privacy@lukhas.eu
                  </Button>
                </a>
                <a href="/contact">
                  <Button variant="ghost" className="border border-trust-blue/30 text-awareness-silver">
                    Contact Form
                  </Button>
                </a>
              </div>
            </div>
          </GlassCard>

        </div>
      </section>

      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Legal</h3>
          <ul className="space-y-2">
            <li><a href="/privacy" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Privacy Policy</a></li>
            <li><a href="/terms" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Terms of Service</a></li>
            <li><a href="/cookies" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Cookie Policy</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Platform</h3>
          <ul className="space-y-2">
            <li><a href="/" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Home</a></li>
            <li><a href="/about" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">About</a></li>
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Contact</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Ecosystem</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.dev" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Developers</a></li>
            <li><a href="https://lukhas.store" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">App Store</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

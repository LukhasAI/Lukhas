import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Shield, Eye, Lock, Database, UserX, FileText, CheckCircle } from 'lucide-react'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-developer-teal/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-developer-teal">.DEV</span>
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
          <Button className="bg-developer-teal text-white">
            Explore Playground
          </Button>
        </HeaderActions>
      </Header>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="mb-6 flex justify-center">
            <Shield className="w-16 h-16 text-developer-teal animate-pulse" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Privacy Policy
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-3xl mx-auto mb-4">
            How we protect your data and respect your privacy
          </p>
          <p className="text-sm text-awareness-silver/60">
            Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
      </section>

      {/* Quick Summary */}
      <section className="py-8 px-6">
        <div className="max-w-5xl mx-auto">
          <GlassCard className="border-developer-teal/30">
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-developer-teal flex items-center gap-3">
                <Eye className="w-6 h-6" />
                Privacy at a Glance
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                  <p className="text-awareness-silver/80">We collect only what's necessary for service operation</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                  <p className="text-awareness-silver/80">Your data is encrypted in transit and at rest</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                  <p className="text-awareness-silver/80">We never sell your personal information</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                  <p className="text-awareness-silver/80">You can delete your data at any time</p>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-8 px-6">
        <div className="max-w-5xl mx-auto space-y-8">

          {/* Information We Collect */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <Database className="w-6 h-6 text-developer-teal" />
                Information We Collect
              </h2>
              <div className="space-y-6 text-awareness-silver/80">
                <div>
                  <h3 className="text-lg font-medium text-awareness-silver mb-3">Account Information</h3>
                  <p className="leading-relaxed">
                    When you create a LUKHAS account, we collect your email address, username, and authentication
                    credentials. For ΛiD (Lambda ID) authentication, we also process identity verification data.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-awareness-silver mb-3">Usage Data</h3>
                  <p className="leading-relaxed">
                    We collect information about how you interact with our consciousness technology platform, including
                    API calls, feature usage, model interactions, and performance metrics. This helps us improve our
                    services and optimize consciousness workflows.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-awareness-silver mb-3">Technical Information</h3>
                  <p className="leading-relaxed">
                    We automatically collect device information, IP addresses, browser types, and operating system
                    details. This data is used for security monitoring, service optimization, and fraud prevention.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-awareness-silver mb-3">Consciousness Interaction Data</h3>
                  <p className="leading-relaxed">
                    When you interact with LUKHAS consciousness systems, we may collect prompts, responses, and
                    interaction patterns to improve model performance and ensure ethical operation. You can opt out
                    of this data collection in your account settings.
                  </p>
                </div>
              </div>
            </div>
          </GlassCard>

          {/* How We Use Information */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <Eye className="w-6 h-6 text-developer-teal" />
                How We Use Your Information
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                  <p><strong className="text-awareness-silver">Service Delivery:</strong> To provide and maintain LUKHAS consciousness technology services</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                  <p><strong className="text-awareness-silver">Personalization:</strong> To customize your experience and adapt consciousness workflows to your needs</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                  <p><strong className="text-awareness-silver">Communication:</strong> To send you service updates, security alerts, and feature announcements</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                  <p><strong className="text-awareness-silver">Security:</strong> To detect and prevent fraud, abuse, and unauthorized access</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                  <p><strong className="text-awareness-silver">Research:</strong> To improve consciousness models and develop new features (with your consent)</p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                  <p><strong className="text-awareness-silver">Legal Compliance:</strong> To comply with applicable laws, regulations, and legal obligations</p>
                </div>
              </div>
            </div>
          </GlassCard>

          {/* Data Sharing */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <Lock className="w-6 h-6 text-developer-teal" />
                Data Sharing and Disclosure
              </h2>
              <div className="space-y-6 text-awareness-silver/80">
                <p className="leading-relaxed text-lg font-medium text-awareness-silver">
                  We do not sell, rent, or trade your personal information. We only share data in these limited circumstances:
                </p>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-medium text-awareness-silver mb-2">Service Providers</h3>
                    <p className="leading-relaxed">
                      We work with trusted third-party service providers for infrastructure, analytics, and security.
                      These providers are contractually bound to protect your data and use it only for specified purposes.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-awareness-silver mb-2">Legal Requirements</h3>
                    <p className="leading-relaxed">
                      We may disclose information if required by law, subpoena, or court order, or to protect the rights,
                      property, or safety of LUKHAS, our users, or the public.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-awareness-silver mb-2">Business Transfers</h3>
                    <p className="leading-relaxed">
                      In the event of a merger, acquisition, or asset sale, user information may be transferred. We will
                      notify you via email and/or prominent notice on our services of any such change.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>

          {/* Data Security */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <Shield className="w-6 h-6 text-developer-teal" />
                Data Security
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  We implement industry-standard security measures to protect your information:
                </p>
                <ul className="space-y-3 list-disc list-inside">
                  <li>End-to-end encryption for data in transit (TLS 1.3)</li>
                  <li>AES-256 encryption for data at rest</li>
                  <li>Regular security audits and penetration testing</li>
                  <li>Multi-factor authentication (MFA) via ΛiD</li>
                  <li>Secure data centers with 24/7 monitoring</li>
                  <li>Employee access controls and security training</li>
                  <li>Incident response and breach notification procedures</li>
                </ul>
                <p className="leading-relaxed mt-4">
                  While we implement robust security measures, no system is completely secure. We encourage you to use
                  strong passwords and enable multi-factor authentication.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Your Rights */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <UserX className="w-6 h-6 text-developer-teal" />
                Your Privacy Rights
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  You have the following rights regarding your personal information:
                </p>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                    <div>
                      <strong className="text-awareness-silver">Access:</strong> Request a copy of your personal data
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                    <div>
                      <strong className="text-awareness-silver">Rectification:</strong> Correct inaccurate or incomplete data
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                    <div>
                      <strong className="text-awareness-silver">Erasure:</strong> Request deletion of your personal data (Right to be Forgotten)
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                    <div>
                      <strong className="text-awareness-silver">Portability:</strong> Receive your data in a machine-readable format
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                    <div>
                      <strong className="text-awareness-silver">Object:</strong> Opt out of certain data processing activities
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-developer-teal flex-shrink-0 mt-1" />
                    <div>
                      <strong className="text-awareness-silver">Withdraw Consent:</strong> Revoke previously granted consent
                    </div>
                  </div>
                </div>
                <p className="leading-relaxed mt-6">
                  To exercise these rights, visit your account settings or contact us at{' '}
                  <a href="mailto:privacy@lukhas.dev" className="text-developer-teal hover:underline">
                    privacy@lukhas.dev
                  </a>
                </p>
              </div>
            </div>
          </GlassCard>

          {/* International Transfers */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                International Data Transfers
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  LUKHAS operates globally. Your information may be transferred to and processed in countries other than
                  your own. We ensure appropriate safeguards are in place for international transfers:
                </p>
                <ul className="space-y-3 list-disc list-inside">
                  <li>EU Standard Contractual Clauses for transfers from the EU/EEA</li>
                  <li>UK International Data Transfer Addendum for UK transfers</li>
                  <li>Privacy Shield Framework compliance (where applicable)</li>
                  <li>Data Processing Agreements with all international partners</li>
                </ul>
                <p className="leading-relaxed mt-4">
                  For EU users, see our <a href="https://lukhas.eu/privacy" className="text-developer-teal hover:underline">
                  GDPR-specific privacy policy</a>.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Children's Privacy */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                Children's Privacy
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  LUKHAS services are not intended for children under 13 years of age. We do not knowingly collect
                  personal information from children under 13. If you are a parent or guardian and believe your child
                  has provided us with personal information, please contact us at{' '}
                  <a href="mailto:privacy@lukhas.dev" className="text-developer-teal hover:underline">
                    privacy@lukhas.dev
                  </a>
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Changes to Policy */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <FileText className="w-6 h-6 text-developer-teal" />
                Changes to This Policy
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  We may update this Privacy Policy from time to time. We will notify you of any material changes by:
                </p>
                <ul className="space-y-2 list-disc list-inside">
                  <li>Posting the updated policy on this page</li>
                  <li>Updating the "Last updated" date</li>
                  <li>Sending you an email notification (for significant changes)</li>
                  <li>Displaying an in-app notification</li>
                </ul>
                <p className="leading-relaxed mt-4">
                  Your continued use of LUKHAS services after changes take effect constitutes acceptance of the updated policy.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Contact */}
          <GlassCard className="border-developer-teal/30">
            <div className="p-8 text-center">
              <h2 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                Questions About Privacy?
              </h2>
              <p className="text-awareness-silver/80 mb-6">
                Contact our Data Protection Officer for privacy-related inquiries
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <a href="mailto:privacy@lukhas.dev">
                  <Button className="bg-developer-teal text-white">
                    Email: privacy@lukhas.dev
                  </Button>
                </a>
                <a href="/contact">
                  <Button variant="ghost" className="border border-developer-teal/30 text-awareness-silver">
                    Contact Form
                  </Button>
                </a>
              </div>
            </div>
          </GlassCard>

        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Legal</h3>
          <ul className="space-y-2">
            <li><a href="/privacy" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">Privacy Policy</a></li>
            <li><a href="/terms" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">Terms of Service</a></li>
            <li><a href="/cookies" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">Cookie Policy</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Platform</h3>
          <ul className="space-y-2">
            <li><a href="/" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">Home</a></li>
            <li><a href="/about" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">About</a></li>
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">Contact</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Compliance</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.eu" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">EU/GDPR</a></li>
            <li><a href="https://lukhas.com" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">US Compliance</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Ecosystem</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.dev" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">Developers</a></li>
            <li><a href="https://lukhas.store" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">App Store</a></li>
            <li><a href="https://lukhas.cloud" className="text-sm text-awareness-silver/70 hover:text-developer-teal transition-colors">Cloud</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

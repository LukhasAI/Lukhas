import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { FileText, Shield, AlertCircle, Scale, XCircle, CheckCircle } from 'lucide-react'

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-dream-ethereal/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-dream-ethereal">.AI</span>
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
          <Button className="bg-dream-gradient text-white">
            Explore Playground
          </Button>
        </HeaderActions>
      </Header>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="mb-6 flex justify-center">
            <Scale className="w-16 h-16 text-dream-ethereal animate-pulse" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Terms of Service
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-3xl mx-auto mb-4">
            The legal agreement governing your use of LUKHAS services
          </p>
          <p className="text-sm text-awareness-silver/60">
            Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
      </section>

      {/* Agreement Notice */}
      <section className="py-8 px-6">
        <div className="max-w-5xl mx-auto">
          <GlassCard className="border-warning-amber/30">
            <div className="p-8">
              <div className="flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-warning-amber flex-shrink-0 mt-1" />
                <div className="text-awareness-silver/90">
                  <p className="text-lg font-medium text-awareness-silver mb-2">
                    Please Read Carefully
                  </p>
                  <p className="leading-relaxed">
                    By accessing or using LUKHAS services, you agree to be bound by these Terms of Service. If you
                    disagree with any part of these terms, you may not access our services.
                  </p>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-8 px-6">
        <div className="max-w-5xl mx-auto space-y-8">

          {/* Definitions */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                1. Definitions
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  <strong className="text-awareness-silver">"Services"</strong> refers to the LUKHAS consciousness
                  technology platform, including all websites, APIs, applications, and related services operated by LUKHAS AI.
                </p>
                <p className="leading-relaxed">
                  <strong className="text-awareness-silver">"You"</strong> or <strong className="text-awareness-silver">"User"</strong> refers
                  to the individual or entity accessing or using our Services.
                </p>
                <p className="leading-relaxed">
                  <strong className="text-awareness-silver">"Content"</strong> includes text, code, data, prompts, outputs,
                  and any other materials created, uploaded, or generated through our Services.
                </p>
                <p className="leading-relaxed">
                  <strong className="text-awareness-silver">"ΛiD"</strong> (Lambda ID) refers to our authentication and identity
                  management system.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Acceptable Use */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <CheckCircle className="w-6 h-6 text-dream-ethereal" />
                2. Acceptable Use Policy
              </h2>
              <div className="space-y-6 text-awareness-silver/80">
                <p className="leading-relaxed">
                  You agree to use our Services responsibly and in compliance with all applicable laws. You may:
                </p>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                    <p>Use LUKHAS for personal, commercial, or research purposes</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                    <p>Create applications and products using our APIs</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                    <p>Share outputs generated by LUKHAS consciousness systems</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                    <p>Integrate LUKHAS into your workflows and applications</p>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>

          {/* Prohibited Activities */}
          <GlassCard className="border-error-red/20">
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <XCircle className="w-6 h-6 text-error-red" />
                3. Prohibited Activities
              </h2>
              <div className="space-y-6 text-awareness-silver/80">
                <p className="leading-relaxed">
                  You agree NOT to:
                </p>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                    <p>Use Services for illegal activities or to violate any laws</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                    <p>Generate or disseminate harmful, abusive, or discriminatory content</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                    <p>Attempt to reverse engineer, decompile, or extract models or algorithms</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                    <p>Bypass rate limits, authentication, or security measures</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                    <p>Use Services to create misleading or deceptive AI-generated content without disclosure</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                    <p>Interfere with or disrupt the integrity or performance of Services</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                    <p>Use automated systems to scrape or harvest data without permission</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <XCircle className="w-5 h-5 text-error-red flex-shrink-0 mt-1" />
                    <p>Share your account credentials or allow unauthorized access</p>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>

          {/* User Accounts */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                4. User Accounts and ΛiD Authentication
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  To access certain features, you must create an account authenticated via ΛiD (Lambda ID). You are
                  responsible for:
                </p>
                <ul className="space-y-2 list-disc list-inside ml-4">
                  <li>Maintaining the confidentiality of your account credentials</li>
                  <li>All activities that occur under your account</li>
                  <li>Notifying us immediately of any unauthorized use</li>
                  <li>Providing accurate and up-to-date information</li>
                </ul>
                <p className="leading-relaxed mt-4">
                  We reserve the right to suspend or terminate accounts that violate these Terms.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Intellectual Property */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                5. Intellectual Property Rights
              </h2>
              <div className="space-y-6 text-awareness-silver/80">
                <div>
                  <h3 className="text-lg font-medium text-awareness-silver mb-3">LUKHAS IP</h3>
                  <p className="leading-relaxed">
                    All rights, title, and interest in the Services, including software, models, algorithms, branding,
                    and documentation, remain the exclusive property of LUKHAS AI. These Terms do not grant you any
                    license to our intellectual property except as necessary to use the Services.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-awareness-silver mb-3">Your Content</h3>
                  <p className="leading-relaxed">
                    You retain ownership of content you create or upload. By using our Services, you grant LUKHAS a
                    worldwide, non-exclusive, royalty-free license to use, process, and store your content solely to
                    provide and improve Services.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-awareness-silver mb-3">Generated Outputs</h3>
                  <p className="leading-relaxed">
                    Subject to your compliance with these Terms, you own the outputs generated by LUKHAS consciousness
                    systems in response to your inputs. However, outputs may be similar to content generated for other
                    users, and we do not make any representation regarding uniqueness.
                  </p>
                </div>
              </div>
            </div>
          </GlassCard>

          {/* Service Availability */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                6. Service Availability and Modifications
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  We strive to provide reliable Services but cannot guarantee uninterrupted access. We reserve the right to:
                </p>
                <ul className="space-y-2 list-disc list-inside ml-4">
                  <li>Modify, suspend, or discontinue any aspect of Services</li>
                  <li>Implement usage limits and restrictions</li>
                  <li>Perform maintenance and updates</li>
                  <li>Change pricing and features</li>
                </ul>
                <p className="leading-relaxed mt-4">
                  We will provide reasonable notice of material changes when feasible.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Disclaimer of Warranties */}
          <GlassCard className="border-warning-amber/20">
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-warning-amber" />
                7. Disclaimer of Warranties
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed uppercase font-medium text-awareness-silver">
                  Services are provided "as is" and "as available" without warranties of any kind, either express or implied.
                </p>
                <p className="leading-relaxed">
                  We disclaim all warranties including, but not limited to, implied warranties of merchantability, fitness
                  for a particular purpose, and non-infringement. We do not warrant that:
                </p>
                <ul className="space-y-2 list-disc list-inside ml-4">
                  <li>Services will be uninterrupted, secure, or error-free</li>
                  <li>Results obtained from Services will be accurate or reliable</li>
                  <li>Quality of outputs will meet your expectations</li>
                  <li>Defects will be corrected</li>
                </ul>
                <p className="leading-relaxed mt-4">
                  You use Services at your own risk and are solely responsible for evaluating outputs before relying on them.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Limitation of Liability */}
          <GlassCard className="border-error-red/20">
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver flex items-center gap-3">
                <Shield className="w-6 h-6 text-error-red" />
                8. Limitation of Liability
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed uppercase font-medium text-awareness-silver">
                  To the maximum extent permitted by law, LUKHAS AI shall not be liable for any indirect, incidental,
                  special, consequential, or punitive damages, including loss of profits, data, use, or goodwill.
                </p>
                <p className="leading-relaxed">
                  Our total liability for any claims arising from or related to Services shall not exceed the greater of:
                  (a) $100 USD or (b) the amount you paid us in the 12 months preceding the claim.
                </p>
                <p className="leading-relaxed">
                  Some jurisdictions do not allow exclusion of certain warranties or limitation of liability, so some
                  limitations may not apply to you.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Indemnification */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                9. Indemnification
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  You agree to indemnify, defend, and hold harmless LUKHAS AI, its affiliates, officers, directors,
                  employees, and agents from any claims, liabilities, damages, losses, and expenses (including legal fees)
                  arising from:
                </p>
                <ul className="space-y-2 list-disc list-inside ml-4">
                  <li>Your use or misuse of Services</li>
                  <li>Your violation of these Terms</li>
                  <li>Your violation of any third-party rights</li>
                  <li>Content you create, upload, or share</li>
                </ul>
              </div>
            </div>
          </GlassCard>

          {/* Termination */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                10. Termination
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  We may suspend or terminate your access to Services immediately, without prior notice or liability, for any
                  reason, including breach of these Terms.
                </p>
                <p className="leading-relaxed">
                  You may terminate your account at any time by contacting us or using account settings. Upon termination:
                </p>
                <ul className="space-y-2 list-disc list-inside ml-4">
                  <li>Your right to use Services immediately ceases</li>
                  <li>We may delete your account and associated data</li>
                  <li>Provisions that by nature should survive termination shall survive</li>
                </ul>
              </div>
            </div>
          </GlassCard>

          {/* Governing Law */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                11. Governing Law and Dispute Resolution
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  These Terms are governed by and construed in accordance with the laws of the State of Delaware, USA,
                  without regard to conflict of law principles.
                </p>
                <p className="leading-relaxed">
                  Any disputes arising from these Terms or Services shall be resolved through binding arbitration in
                  accordance with the American Arbitration Association rules. You waive any right to a jury trial or to
                  participate in a class action lawsuit.
                </p>
                <p className="leading-relaxed">
                  For EU users, mandatory consumer protection laws and dispute resolution mechanisms in your jurisdiction
                  shall apply. See <a href="https://lukhas.eu/terms" className="text-dream-ethereal hover:underline">
                  EU-specific terms</a>.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* General Provisions */}
          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                12. General Provisions
              </h2>
              <div className="space-y-4 text-awareness-silver/80">
                <p className="leading-relaxed">
                  <strong className="text-awareness-silver">Entire Agreement:</strong> These Terms constitute the entire
                  agreement between you and LUKHAS AI regarding Services.
                </p>
                <p className="leading-relaxed">
                  <strong className="text-awareness-silver">Severability:</strong> If any provision is found unenforceable,
                  the remaining provisions remain in full effect.
                </p>
                <p className="leading-relaxed">
                  <strong className="text-awareness-silver">Waiver:</strong> Failure to enforce any provision does not
                  constitute a waiver of that provision.
                </p>
                <p className="leading-relaxed">
                  <strong className="text-awareness-silver">Assignment:</strong> You may not assign or transfer these Terms.
                  We may assign these Terms without restriction.
                </p>
                <p className="leading-relaxed">
                  <strong className="text-awareness-silver">Modifications:</strong> We may modify these Terms at any time.
                  Continued use constitutes acceptance of modified Terms.
                </p>
              </div>
            </div>
          </GlassCard>

          {/* Contact */}
          <GlassCard className="border-dream-ethereal/30">
            <div className="p-8 text-center">
              <h2 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                Questions About These Terms?
              </h2>
              <p className="text-awareness-silver/80 mb-6">
                Contact our legal team for terms-related inquiries
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <a href="mailto:legal@lukhas.ai">
                  <Button className="bg-dream-gradient text-white">
                    Email: legal@lukhas.ai
                  </Button>
                </a>
                <a href="/contact">
                  <Button variant="ghost" className="border border-dream-ethereal/30 text-awareness-silver">
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
            <li><a href="/privacy" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Privacy Policy</a></li>
            <li><a href="/terms" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Terms of Service</a></li>
            <li><a href="/cookies" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Cookie Policy</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Platform</h3>
          <ul className="space-y-2">
            <li><a href="/" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Home</a></li>
            <li><a href="/about" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">About</a></li>
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Contact</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Compliance</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.eu" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">EU/GDPR</a></li>
            <li><a href="https://lukhas.com" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">US Compliance</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Ecosystem</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.dev" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Developers</a></li>
            <li><a href="https://lukhas.store" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">App Store</a></li>
            <li><a href="https://lukhas.cloud" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Cloud</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

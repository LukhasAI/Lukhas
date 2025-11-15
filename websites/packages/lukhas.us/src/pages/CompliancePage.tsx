import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { Shield, FileCheck, Scale, Building2, Lock, Eye, CheckCircle, AlertTriangle } from 'lucide-react'

export default function CompliancePage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-institutional-blue/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-institutional-blue">.US</span>
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="/compliance">Compliance</HeaderNavLink>
          <HeaderNavLink href="/contact">Contact</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.com">Enterprise</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
          <Link to="/contact">
            <Button className="bg-institutional-gradient text-white">
              Contact Compliance
            </Button>
          </Link>
        </HeaderActions>
      </Header>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Regulatory <span className="text-transparent bg-clip-text bg-institutional-gradient">Compliance</span>
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto">
            Comprehensive alignment with US federal and state AI regulations
          </p>
        </div>
      </section>

      {/* CCPA Compliance */}
      <section id="ccpa" className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <div className="flex items-center gap-4 mb-6">
              <Shield className="w-12 h-12 text-institutional-blue" strokeWidth={1.5} />
              <h2 className="text-4xl font-light tracking-[0.1em] text-awareness-silver">
                CCPA <span className="text-institutional-blue">Compliance</span>
              </h2>
            </div>
            <p className="text-lg text-awareness-silver/80 max-w-4xl">
              Full compliance with the California Consumer Privacy Act (CCPA) and California Privacy Rights Act (CPRA)
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <GlassCard>
              <div className="p-8">
                <h3 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                  Consumer Rights Implementation
                </h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Right to Know:</strong> Detailed disclosure of data collection, usage, and sharing practices
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Right to Delete:</strong> Secure data deletion process within 45 days of verified requests
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Right to Opt-Out:</strong> One-click opt-out mechanisms for data sales and sharing
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Right to Correct:</strong> Streamlined process for correcting inaccurate personal information
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Right to Limit:</strong> Controls for limiting use of sensitive personal information
                    </span>
                  </li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <h3 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                  Business Practices
                </h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Privacy Notice:</strong> Clear, comprehensive privacy notices in plain language
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Data Minimization:</strong> Collection limited to necessary business purposes
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Security Measures:</strong> Reasonable security procedures protecting personal information
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Service Provider Contracts:</strong> CCPA-compliant agreements with all service providers
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-verified-green mt-1 flex-shrink-0" strokeWidth={1.5} />
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Non-Discrimination:</strong> No penalization for exercising privacy rights
                    </span>
                  </li>
                </ul>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* NIST AI Framework */}
      <section id="nist" className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <div className="flex items-center gap-4 mb-6">
              <FileCheck className="w-12 h-12 text-institutional-blue" strokeWidth={1.5} />
              <h2 className="text-4xl font-light tracking-[0.1em] text-awareness-silver">
                NIST AI <span className="text-institutional-blue">Framework</span>
              </h2>
            </div>
            <p className="text-lg text-awareness-silver/80 max-w-4xl">
              Alignment with NIST AI Risk Management Framework (AI RMF 1.0) for trustworthy AI systems
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Govern
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Organizational structures, policies, and processes for responsible AI development and deployment
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Map
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Context understanding including AI system capabilities, limitations, and potential impacts
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Measure
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Quantitative and qualitative assessment of AI system risks and trustworthiness characteristics
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Manage
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Risk prioritization, response planning, and continuous monitoring of AI system performance
                </p>
              </div>
            </GlassCard>
          </div>

          <GlassCard>
            <div className="p-8">
              <h3 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">
                Trustworthy AI Characteristics
              </h3>
              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <h4 className="text-lg font-semibold mb-2 text-awareness-silver">Valid &amp; Reliable</h4>
                  <p className="text-sm text-awareness-silver/80">AI systems perform consistently and accurately across contexts</p>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2 text-awareness-silver">Safe &amp; Secure</h4>
                  <p className="text-sm text-awareness-silver/80">Protection against cybersecurity threats and misuse</p>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2 text-awareness-silver">Accountable &amp; Transparent</h4>
                  <p className="text-sm text-awareness-silver/80">Clear documentation and explanation of AI decision-making</p>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2 text-awareness-silver">Fair &amp; Non-Discriminatory</h4>
                  <p className="text-sm text-awareness-silver/80">Bias testing and mitigation across protected characteristics</p>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2 text-awareness-silver">Privacy Enhanced</h4>
                  <p className="text-sm text-awareness-silver/80">Data protection and privacy-preserving technologies</p>
                </div>
                <div>
                  <h4 className="text-lg font-semibold mb-2 text-awareness-silver">Interpretable &amp; Explainable</h4>
                  <p className="text-sm text-awareness-silver/80">Clear explanations of AI outputs and reasoning processes</p>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* AI Bill of Rights */}
      <section id="ai-bill-of-rights" className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <div className="flex items-center gap-4 mb-6">
              <Scale className="w-12 h-12 text-institutional-blue" strokeWidth={1.5} />
              <h2 className="text-4xl font-light tracking-[0.1em] text-awareness-silver">
                AI Bill of <span className="text-institutional-blue">Rights</span>
              </h2>
            </div>
            <p className="text-lg text-awareness-silver/80 max-w-4xl">
              Adherence to White House Blueprint for an AI Bill of Rights principles
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <GlassCard>
              <div className="p-8">
                <div className="mb-4">
                  <Shield className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Safe and Effective Systems
                </h3>
                <p className="text-awareness-silver/80">
                  Protected from unsafe or ineffective systems through pre-deployment testing,
                  risk identification, and ongoing monitoring
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="mb-4">
                  <AlertTriangle className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Algorithmic Discrimination Protections
                </h3>
                <p className="text-awareness-silver/80">
                  Protection from algorithmic discrimination with proactive equity assessments
                  and bias mitigation
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="mb-4">
                  <Lock className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Data Privacy
                </h3>
                <p className="text-awareness-silver/80">
                  Built-in data protections with user consent, data minimization, and
                  privacy-preserving technologies
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="mb-4">
                  <Eye className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Notice and Explanation
                </h3>
                <p className="text-awareness-silver/80">
                  Clear notification when AI systems are being used and plain language explanations
                  of how they work
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="mb-4">
                  <CheckCircle className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Human Alternatives
                </h3>
                <p className="text-awareness-silver/80">
                  Right to opt out of AI-driven systems and access to human consideration
                  and remedy for errors
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="mb-4">
                  <Building2 className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-institutional-blue">
                  Multi-Stakeholder Engagement
                </h3>
                <p className="text-awareness-silver/80">
                  Ongoing consultation with diverse communities, domain experts, and impacted
                  stakeholders
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* State Privacy Laws */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <div className="flex items-center gap-4 mb-6">
              <Building2 className="w-12 h-12 text-institutional-blue" strokeWidth={1.5} />
              <h2 className="text-4xl font-light tracking-[0.1em] text-awareness-silver">
                State Privacy <span className="text-institutional-blue">Laws</span>
              </h2>
            </div>
            <p className="text-lg text-awareness-silver/80 max-w-4xl">
              Compliance with comprehensive state privacy regulations across the United States
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  California
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-2">CCPA / CPRA</p>
                <span className="inline-block px-3 py-1 bg-verified-green/20 text-verified-green text-xs rounded-full">
                  Compliant
                </span>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Colorado
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-2">CPA</p>
                <span className="inline-block px-3 py-1 bg-verified-green/20 text-verified-green text-xs rounded-full">
                  Compliant
                </span>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Virginia
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-2">VCDPA</p>
                <span className="inline-block px-3 py-1 bg-verified-green/20 text-verified-green text-xs rounded-full">
                  Compliant
                </span>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Connecticut
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-2">CTDPA</p>
                <span className="inline-block px-3 py-1 bg-verified-green/20 text-verified-green text-xs rounded-full">
                  Compliant
                </span>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Utah
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-2">UCPA</p>
                <span className="inline-block px-3 py-1 bg-verified-green/20 text-verified-green text-xs rounded-full">
                  Compliant
                </span>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Oregon
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-2">OCPA</p>
                <span className="inline-block px-3 py-1 bg-verified-green/20 text-verified-green text-xs rounded-full">
                  Compliant
                </span>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Montana
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-2">MCDPA</p>
                <span className="inline-block px-3 py-1 bg-verified-green/20 text-verified-green text-xs rounded-full">
                  Compliant
                </span>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Additional States
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-2">Ongoing</p>
                <span className="inline-block px-3 py-1 bg-warning-amber/20 text-warning-amber text-xs rounded-full">
                  Monitoring
                </span>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-institutional-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Need Compliance Documentation?
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Request detailed compliance reports and certifications
          </p>
          <Link to="/contact">
            <Button size="lg" className="bg-white text-institutional-blue px-12 py-6 text-lg hover:bg-awareness-silver">
              Request Documentation
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Compliance</h3>
          <ul className="space-y-2">
            <li><a href="#ccpa" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">CCPA</a></li>
            <li><a href="#nist" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">NIST Framework</a></li>
            <li><a href="#ai-bill-of-rights" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">AI Bill of Rights</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Transparency</h3>
          <ul className="space-y-2">
            <li><a href="/transparency" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Reports</a></li>
            <li><a href="/audits" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Audits</a></li>
            <li><a href="/certifications" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Certifications</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Your Rights</h3>
          <ul className="space-y-2">
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Exercise Rights</a></li>
            <li><a href="/privacy-policy" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Privacy Policy</a></li>
            <li><a href="/terms" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Terms of Service</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Contact</h3>
          <ul className="space-y-2">
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Privacy Officer</a></li>
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Legal Counsel</a></li>
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Compliance Team</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

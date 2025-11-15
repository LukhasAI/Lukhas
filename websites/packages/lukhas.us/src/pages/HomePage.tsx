import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { Scale, Shield, FileCheck, Eye, Users, Building2, CheckCircle, FileText, Award } from 'lucide-react'

export default function HomePage() {
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
          <div className="mb-6 flex justify-center">
            <Scale className="w-16 h-16 text-institutional-blue" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            American <span className="text-transparent bg-clip-text bg-institutional-gradient">Compliance</span>
          </h1>
          <p className="text-xl md:text-2xl font-light tracking-wide mb-8 text-awareness-silver/80 max-w-4xl mx-auto">
            LUKHAS AI aligned with American values, regulations, and privacy frameworks
          </p>
          <p className="text-lg text-awareness-silver/70 max-w-3xl mx-auto mb-12">
            Transparent consciousness technology adhering to CCPA, NIST AI Framework,
            and the White House AI Bill of Rights
          </p>
          <div className="flex flex-wrap justify-center gap-8 text-sm text-awareness-silver/70 tracking-wide">
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-institutional-blue rounded-full"></span>
              CCPA Compliant
            </span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-institutional-blue rounded-full"></span>
              NIST AI Framework
            </span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-institutional-blue rounded-full"></span>
              AI Bill of Rights
            </span>
          </div>
        </div>
      </section>

      {/* Compliance Overview */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-light tracking-[0.1em] mb-4 text-awareness-silver">
              US Regulatory <span className="text-institutional-blue">Framework</span>
            </h2>
            <p className="text-lg text-awareness-silver/80 max-w-3xl mx-auto">
              Full alignment with federal and state regulations governing AI systems
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard>
              <div className="p-6 text-center">
                <div className="mb-4 flex justify-center">
                  <Shield className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  CCPA Compliance
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  California Consumer Privacy Act full compliance with user rights and data protection
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <div className="mb-4 flex justify-center">
                  <FileCheck className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  NIST AI Framework
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Alignment with National Institute of Standards and Technology AI risk management
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <div className="mb-4 flex justify-center">
                  <Scale className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  AI Bill of Rights
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  White House AI principles including safe systems, data privacy, and human alternatives
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <div className="mb-4 flex justify-center">
                  <Building2 className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  State Privacy Laws
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Compliance with California, Colorado, Virginia, and other state privacy regulations
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Transparency Center */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="mb-4 flex justify-center">
              <Eye className="w-12 h-12 text-institutional-blue" strokeWidth={1.5} />
            </div>
            <h2 className="text-4xl font-light tracking-[0.1em] mb-4 text-awareness-silver">
              Transparency <span className="text-institutional-blue">Center</span>
            </h2>
            <p className="text-lg text-awareness-silver/80 max-w-3xl mx-auto">
              Public disclosure of AI operations, decision-making processes, and compliance audits
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <GlassCard>
              <div className="p-8">
                <div className="mb-4">
                  <FileText className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Transparency Reports
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Quarterly public disclosures of AI system operations, data usage, and performance metrics
                </p>
                <Button variant="ghost" className="text-institutional-blue">
                  View Reports
                </Button>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="mb-4">
                  <CheckCircle className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Audit Results
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Independent third-party audits verifying compliance with all applicable US regulations
                </p>
                <Button variant="ghost" className="text-institutional-blue">
                  View Audits
                </Button>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="mb-4">
                  <Award className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Certifications
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Current compliance certifications and security attestations for American standards
                </p>
                <Button variant="ghost" className="text-institutional-blue">
                  View Certifications
                </Button>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* User Rights */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="mb-4 flex justify-center">
              <Users className="w-12 h-12 text-institutional-blue" strokeWidth={1.5} />
            </div>
            <h2 className="text-4xl font-light tracking-[0.1em] mb-4 text-awareness-silver">
              Your Privacy <span className="text-institutional-blue">Rights</span>
            </h2>
            <p className="text-lg text-awareness-silver/80 max-w-3xl mx-auto">
              Under CCPA and other US privacy laws, you have the right to control your data
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <GlassCard>
              <div className="p-10">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-awareness-silver">
                      Right to Know
                    </h3>
                    <p className="text-awareness-silver/80 text-sm">
                      Request information about what personal data we collect, use, disclose, or sell
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-awareness-silver">
                      Right to Delete
                    </h3>
                    <p className="text-awareness-silver/80 text-sm">
                      Request deletion of your personal information (subject to legal exceptions)
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-awareness-silver">
                      Right to Opt-Out
                    </h3>
                    <p className="text-awareness-silver/80 text-sm">
                      Opt-out of the sale or sharing of your personal information
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-awareness-silver">
                      Right to Correct
                    </h3>
                    <p className="text-awareness-silver/80 text-sm">
                      Request correction of inaccurate personal information
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-awareness-silver">
                      Right to Limit
                    </h3>
                    <p className="text-awareness-silver/80 text-sm">
                      Limit use and disclosure of sensitive personal information
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-awareness-silver">
                      Non-Discrimination
                    </h3>
                    <p className="text-awareness-silver/80 text-sm">
                      Exercise your rights without discriminatory treatment
                    </p>
                  </div>
                </div>

                <div className="mt-8 pt-8 border-t border-awareness-silver/10 text-center">
                  <Link to="/contact">
                    <Button className="bg-institutional-gradient text-white">
                      Exercise Your Rights
                    </Button>
                  </Link>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-institutional-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Questions About US Compliance?
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Our privacy and compliance teams are here to help
          </p>
          <Link to="/contact">
            <Button size="lg" className="bg-white text-institutional-blue px-12 py-6 text-lg hover:bg-awareness-silver">
              Contact Compliance Team
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Compliance</h3>
          <ul className="space-y-2">
            <li><a href="/compliance#ccpa" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">CCPA</a></li>
            <li><a href="/compliance#nist" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">NIST Framework</a></li>
            <li><a href="/compliance#ai-bill-of-rights" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">AI Bill of Rights</a></li>
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

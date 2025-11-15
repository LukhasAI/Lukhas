import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { Mail, Phone, MapPin, User, FileText, Shield } from 'lucide-react'

export default function ContactPage() {
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
            Contact <span className="text-transparent bg-clip-text bg-institutional-gradient">Compliance</span>
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto">
            Reach our privacy, legal, and compliance teams for any US regulatory inquiries
          </p>
        </div>
      </section>

      {/* Contact Cards */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <GlassCard>
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <User className="w-12 h-12 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                  Privacy Officer
                </h3>
                <div className="space-y-3 text-awareness-silver/80">
                  <div className="flex items-center justify-center gap-2">
                    <Mail className="w-4 h-4 text-institutional-blue" strokeWidth={1.5} />
                    <a href="mailto:privacy-us@lukhas.us" className="hover:text-institutional-blue transition-colors">
                      privacy-us@lukhas.us
                    </a>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <Phone className="w-4 h-4 text-institutional-blue" strokeWidth={1.5} />
                    <span>+1 (555) 123-4567</span>
                  </div>
                </div>
                <p className="text-sm text-awareness-silver/70 mt-4">
                  For CCPA requests, data privacy inquiries, and user rights
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <FileText className="w-12 h-12 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                  Legal Counsel
                </h3>
                <div className="space-y-3 text-awareness-silver/80">
                  <div className="flex items-center justify-center gap-2">
                    <Mail className="w-4 h-4 text-institutional-blue" strokeWidth={1.5} />
                    <a href="mailto:legal-us@lukhas.us" className="hover:text-institutional-blue transition-colors">
                      legal-us@lukhas.us
                    </a>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <Phone className="w-4 h-4 text-institutional-blue" strokeWidth={1.5} />
                    <span>+1 (555) 123-4568</span>
                  </div>
                </div>
                <p className="text-sm text-awareness-silver/70 mt-4">
                  For legal inquiries, contract matters, and regulatory questions
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <Shield className="w-12 h-12 text-institutional-blue" strokeWidth={1.5} />
                </div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                  Compliance Team
                </h3>
                <div className="space-y-3 text-awareness-silver/80">
                  <div className="flex items-center justify-center gap-2">
                    <Mail className="w-4 h-4 text-institutional-blue" strokeWidth={1.5} />
                    <a href="mailto:compliance-us@lukhas.us" className="hover:text-institutional-blue transition-colors">
                      compliance-us@lukhas.us
                    </a>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <Phone className="w-4 h-4 text-institutional-blue" strokeWidth={1.5} />
                    <span>+1 (555) 123-4569</span>
                  </div>
                </div>
                <p className="text-sm text-awareness-silver/70 mt-4">
                  For audit requests, compliance documentation, and regulatory reports
                </p>
              </div>
            </GlassCard>
          </div>

          {/* US Office */}
          <div className="max-w-4xl mx-auto mb-16">
            <GlassCard>
              <div className="p-10">
                <div className="flex items-center gap-4 mb-6">
                  <MapPin className="w-10 h-10 text-institutional-blue" strokeWidth={1.5} />
                  <h2 className="text-3xl font-light tracking-wide text-awareness-silver">
                    US Office
                  </h2>
                </div>
                <div className="text-awareness-silver/80 space-y-2">
                  <p className="text-lg">LUKHAS AI Corporation</p>
                  <p>123 Innovation Boulevard, Suite 500</p>
                  <p>San Francisco, CA 94105</p>
                  <p>United States</p>
                </div>
                <div className="mt-6 pt-6 border-t border-awareness-silver/10">
                  <p className="text-sm text-awareness-silver/70">
                    <strong className="text-awareness-silver">Office Hours:</strong> Monday - Friday, 9:00 AM - 5:00 PM PST
                  </p>
                  <p className="text-sm text-awareness-silver/70 mt-2">
                    <strong className="text-awareness-silver">Response Time:</strong> CCPA requests within 45 days, general inquiries within 5 business days
                  </p>
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Contact Form */}
          <div className="max-w-4xl mx-auto">
            <GlassCard>
              <div className="p-10">
                <h2 className="text-3xl font-light tracking-wide mb-6 text-awareness-silver text-center">
                  Exercise Your Privacy Rights
                </h2>
                <p className="text-awareness-silver/80 text-center mb-8">
                  Submit a request to exercise your CCPA rights or contact our compliance team
                </p>

                <form className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="firstName" className="block text-sm font-medium text-awareness-silver mb-2">
                        First Name *
                      </label>
                      <input
                        type="text"
                        id="firstName"
                        name="firstName"
                        required
                        className="w-full px-4 py-3 bg-consciousness-deep border border-awareness-silver/20 rounded-lg text-awareness-silver focus:outline-none focus:border-institutional-blue transition-colors"
                      />
                    </div>
                    <div>
                      <label htmlFor="lastName" className="block text-sm font-medium text-awareness-silver mb-2">
                        Last Name *
                      </label>
                      <input
                        type="text"
                        id="lastName"
                        name="lastName"
                        required
                        className="w-full px-4 py-3 bg-consciousness-deep border border-awareness-silver/20 rounded-lg text-awareness-silver focus:outline-none focus:border-institutional-blue transition-colors"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-awareness-silver mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      required
                      className="w-full px-4 py-3 bg-consciousness-deep border border-awareness-silver/20 rounded-lg text-awareness-silver focus:outline-none focus:border-institutional-blue transition-colors"
                    />
                  </div>

                  <div>
                    <label htmlFor="requestType" className="block text-sm font-medium text-awareness-silver mb-2">
                      Request Type *
                    </label>
                    <select
                      id="requestType"
                      name="requestType"
                      required
                      className="w-full px-4 py-3 bg-consciousness-deep border border-awareness-silver/20 rounded-lg text-awareness-silver focus:outline-none focus:border-institutional-blue transition-colors"
                    >
                      <option value="">Select a request type</option>
                      <option value="right-to-know">Right to Know</option>
                      <option value="right-to-delete">Right to Delete</option>
                      <option value="right-to-opt-out">Right to Opt-Out</option>
                      <option value="right-to-correct">Right to Correct</option>
                      <option value="right-to-limit">Right to Limit</option>
                      <option value="compliance-inquiry">Compliance Inquiry</option>
                      <option value="legal-inquiry">Legal Inquiry</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-awareness-silver mb-2">
                      Message *
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      rows={6}
                      required
                      className="w-full px-4 py-3 bg-consciousness-deep border border-awareness-silver/20 rounded-lg text-awareness-silver focus:outline-none focus:border-institutional-blue transition-colors resize-none"
                      placeholder="Please provide details about your request or inquiry..."
                    />
                  </div>

                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      id="verification"
                      name="verification"
                      required
                      className="mt-1"
                    />
                    <label htmlFor="verification" className="text-sm text-awareness-silver/80">
                      I certify that I am the individual whose personal information is the subject of this request,
                      or I am authorized to make this request on their behalf. I understand that providing false
                      information may result in civil or criminal penalties. *
                    </label>
                  </div>

                  <div className="text-center">
                    <Button type="submit" size="lg" className="bg-institutional-gradient text-white px-12 py-4">
                      Submit Request
                    </Button>
                  </div>

                  <p className="text-xs text-awareness-silver/60 text-center">
                    We will respond to your request within 45 days as required by CCPA.
                    For urgent matters, please call our privacy officer directly.
                  </p>
                </form>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-institutional-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Need Immediate Assistance?
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Our compliance team is available Monday through Friday
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <a href="mailto:compliance-us@lukhas.us">
              <Button size="lg" className="bg-white text-institutional-blue px-12 py-6 text-lg hover:bg-awareness-silver">
                Email Compliance Team
              </Button>
            </a>
            <a href="tel:+15551234569">
              <Button size="lg" variant="ghost" className="bg-white/10 text-white px-12 py-6 text-lg hover:bg-white/20">
                Call +1 (555) 123-4569
              </Button>
            </a>
          </div>
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
            <li><a href="mailto:privacy-us@lukhas.us" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Privacy Officer</a></li>
            <li><a href="mailto:legal-us@lukhas.us" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Legal Counsel</a></li>
            <li><a href="mailto:compliance-us@lukhas.us" className="text-sm text-awareness-silver/70 hover:text-institutional-blue transition-colors">Compliance Team</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

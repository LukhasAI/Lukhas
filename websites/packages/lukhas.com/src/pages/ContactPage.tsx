import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Mail, MessageSquare, MapPin, Clock, Send } from 'lucide-react'

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-enterprise-amber/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-enterprise-amber">.COM</span>
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
            <MessageSquare className="w-16 h-16 text-enterprise-amber animate-pulse" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Get In Touch
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-3xl mx-auto">
            Have questions about LUKHAS consciousness technology? We're here to help.
          </p>
        </div>
      </section>

      <section className="py-8 px-6">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-8">
          <div className="space-y-6">
            <GlassCard>
              <div className="p-8">
                <div className="flex items-center gap-4 mb-4">
                  <Mail className="w-8 h-8 text-enterprise-amber" />
                  <div>
                    <h3 className="text-xl font-light text-awareness-silver">General Inquiries</h3>
                    <a href="mailto:hello@lukhas.com" className="text-enterprise-amber hover:underline">
                      hello@lukhas.com
                    </a>
                  </div>
                </div>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="flex items-center gap-4 mb-4">
                  <Send className="w-8 h-8 text-lambda-gold" />
                  <div>
                    <h3 className="text-xl font-light text-awareness-silver">Technical Support</h3>
                    <a href="mailto:support@lukhas.com" className="text-enterprise-amber hover:underline">
                      support@lukhas.com
                    </a>
                  </div>
                </div>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="flex items-center gap-4 mb-4">
                  <Clock className="w-8 h-8 text-success-green" />
                  <div>
                    <h3 className="text-xl font-light text-awareness-silver">Response Time</h3>
                    <p className="text-awareness-silver/70">Usually within 24-48 hours</p>
                  </div>
                </div>
              </div>
            </GlassCard>
          </div>

          <GlassCard>
            <div className="p-8">
              <h2 className="text-2xl font-light tracking-wide mb-6 text-awareness-silver">Send Us A Message</h2>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm text-awareness-silver/70 mb-2">Name</label>
                  <input 
                    type="text" 
                    className="w-full px-4 py-3 bg-consciousness-deep border border-enterprise-amber/30 rounded-lg text-awareness-silver focus:outline-none focus:border-enterprise-amber"
                    placeholder="Your name"
                  />
                </div>
                <div>
                  <label className="block text-sm text-awareness-silver/70 mb-2">Email</label>
                  <input 
                    type="email" 
                    className="w-full px-4 py-3 bg-consciousness-deep border border-enterprise-amber/30 rounded-lg text-awareness-silver focus:outline-none focus:border-enterprise-amber"
                    placeholder="you@example.com"
                  />
                </div>
                <div>
                  <label className="block text-sm text-awareness-silver/70 mb-2">Subject</label>
                  <input 
                    type="text" 
                    className="w-full px-4 py-3 bg-consciousness-deep border border-enterprise-amber/30 rounded-lg text-awareness-silver focus:outline-none focus:border-enterprise-amber"
                    placeholder="What's this about?"
                  />
                </div>
                <div>
                  <label className="block text-sm text-awareness-silver/70 mb-2">Message</label>
                  <textarea 
                    rows={6}
                    className="w-full px-4 py-3 bg-consciousness-deep border border-enterprise-amber/30 rounded-lg text-awareness-silver focus:outline-none focus:border-enterprise-amber resize-none"
                    placeholder="Tell us how we can help..."
                  />
                </div>
                <Button className="w-full bg-enterprise-amber text-white py-3">
                  Send Message
                </Button>
              </form>
            </div>
          </GlassCard>
        </div>
      </section>

      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Legal</h3>
          <ul className="space-y-2">
            <li><a href="/privacy" className="text-sm text-awareness-silver/70 hover:text-enterprise-amber transition-colors">Privacy Policy</a></li>
            <li><a href="/terms" className="text-sm text-awareness-silver/70 hover:text-enterprise-amber transition-colors">Terms of Service</a></li>
            <li><a href="/cookies" className="text-sm text-awareness-silver/70 hover:text-enterprise-amber transition-colors">Cookie Policy</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Platform</h3>
          <ul className="space-y-2">
            <li><a href="/" className="text-sm text-awareness-silver/70 hover:text-enterprise-amber transition-colors">Home</a></li>
            <li><a href="/about" className="text-sm text-awareness-silver/70 hover:text-enterprise-amber transition-colors">About</a></li>
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-enterprise-amber transition-colors">Contact</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Ecosystem</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.dev" className="text-sm text-awareness-silver/70 hover:text-enterprise-amber transition-colors">Developers</a></li>
            <li><a href="https://lukhas.store" className="text-sm text-awareness-silver/70 hover:text-enterprise-amber transition-colors">App Store</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

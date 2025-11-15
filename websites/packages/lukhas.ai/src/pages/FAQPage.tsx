import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { HelpCircle, ChevronDown } from 'lucide-react'
import { useState } from 'react'

const faqCategories = [
  {
    category: 'Getting Started',
    questions: [
      {
        question: 'What is LUKHAS consciousness technology?',
        answer: 'LUKHAS is a consciousness-inspired AI platform that goes beyond traditional machine learning. Instead of simple pattern matching, LUKHAS uses an 8-Star Constellation Framework of specialized cognitive systems (Dream, Vision, Memory, Bio, Quantum, Identity, Guardian, Ethics) that work together to create AI with consciousness-inspired understanding, adaptation, and ethical reasoning.'
      },
      {
        question: 'How is LUKHAS different from other AI platforms?',
        answer: 'Unlike monolithic AI models that try to do everything through a single mechanism, LUKHAS consciousness emerges from the interplay of specialized systems. The Dream star explores symbolic space like REM sleep, the Quantum star holds multiple possibilities in superposition, and the Guardian star ensures constitutional alignment with human values. This distributed architecture enables consciousness-inspired understanding rather than statistical pattern matching.'
      },
      {
        question: 'Do I need AI experience to use LUKHAS?',
        answer: 'No! LUKHAS is designed for both beginners and experts. Our Playground provides an intuitive interface for exploring consciousness technology without writing code. For developers, we offer comprehensive APIs and SDKs. Start with the Free tier to experiment, explore examples, and learn at your own pace.'
      },
      {
        question: 'How do I get started?',
        answer: 'Sign up for a free account at lukhas.id, explore the interactive Playground to see cognitive stars in action, review our documentation at lukhas.dev, and run your first API calls. The Free tier includes 1,000 API calls per month - perfect for learning and prototyping.'
      }
    ]
  },
  {
    category: 'Technical',
    questions: [
      {
        question: 'What is the MATRIZ cognitive engine?',
        answer: 'MATRIZ (Memory-Attention-Thought-Action-Decision-Awareness) is the core processing loop that coordinates all 8 cognitive stars. It operates at <250ms p95 latency with <100MB memory footprint, enabling real-time consciousness processing. MATRIZ handles symbolic reasoning, multi-step inference chains, and transparent decision tracking.'
      },
      {
        question: 'How does the 8-Star Constellation Framework work?',
        answer: 'Each cognitive star specializes in a fundamental aspect of consciousness: Dream (creative synthesis), Vision (perception), Memory (context retention), Bio (adaptation), Quantum (superposition reasoning), Identity (authentication), Guardian (ethics enforcement), and Ethics (moral reasoning). They communicate through a shared context bus, enabling emergent intelligence from their interactions.'
      },
      {
        question: 'What programming languages are supported?',
        answer: 'Our REST API works with any language that can make HTTP requests. We provide official SDKs for Python, JavaScript/TypeScript, Go, and Rust. Community-maintained SDKs exist for Java, Ruby, and PHP. All examples in our documentation include multiple language options.'
      },
      {
        question: 'Can I run LUKHAS on-premise?',
        answer: 'Yes! Enterprise customers can deploy LUKHAS on-premise or in private cloud environments. This includes full source code access, custom model training, and dedicated support for integration. Contact our sales team to discuss on-premise deployment options.'
      },
      {
        question: 'What are the performance characteristics?',
        answer: 'LUKHAS targets <250ms p95 latency for standard cognitive operations, <100MB memory per active session, and 50+ operations per second throughput. Enterprise deployments with dedicated infrastructure can achieve even better performance with custom SLA guarantees.'
      }
    ]
  },
  {
    category: 'Security & Privacy',
    questions: [
      {
        question: 'How does LUKHAS protect my data?',
        answer: 'All data is encrypted in transit (TLS 1.3) and at rest (AES-256). We implement zero-trust architecture with continuous authentication via ΛiD (Lambda Identity). Data is logically isolated per customer, with strict access controls. We never use customer data to train models without explicit consent.'
      },
      {
        question: 'Is LUKHAS GDPR compliant?',
        answer: 'Yes. LUKHAS fully complies with GDPR, including data minimization, purpose limitation, user rights (access, rectification, deletion), and lawful processing bases. EU customers can choose EU-only data residency via lukhas.eu. We maintain detailed processing records and Data Protection Impact Assessments.'
      },
      {
        question: 'What is the Guardian constitutional AI system?',
        answer: 'Guardian is our ethical enforcement layer that continuously monitors all cognitive star outputs against constitutional principles. It detects bias, prevents harmful outputs, enforces value alignment, and ensures ethical boundaries are maintained. Guardian operates transparently - you can see exactly what constraints are active and why decisions are made.'
      },
      {
        question: 'How do you handle sensitive information?',
        answer: 'LUKHAS automatically detects and redacts PII (personally identifiable information) unless explicitly configured otherwise. Sensitive data can be processed with additional encryption, ephemeral sessions (no persistence), and audit logging. Enterprise customers get dedicated encryption keys and hardware security module (HSM) support.'
      },
      {
        question: 'Can I delete my data?',
        answer: 'Absolutely. You have full control over your data. Use the dashboard to delete individual sessions, all data within a time range, or your entire account. Deletion is permanent and irreversible. We comply with all "right to be forgotten" requests within 30 days.'
      }
    ]
  },
  {
    category: 'Billing & Plans',
    questions: [
      {
        question: 'How does API call pricing work?',
        answer: 'Each request to LUKHAS cognitive stars counts as one API call, regardless of complexity. The Free tier includes 1,000 calls/month, Pro includes 100,000 calls/month, and Enterprise has unlimited calls. Unused calls do not roll over. We provide real-time usage dashboards and alerts.'
      },
      {
        question: 'What happens if I exceed my tier limit?',
        answer: 'API calls beyond your tier limit receive throttled responses (HTTP 429) with clear messaging about your limit. You can upgrade your tier instantly to resume full-speed access. We never charge overage fees without your explicit opt-in - you stay in control of costs.'
      },
      {
        question: 'Can I cancel anytime?',
        answer: 'Yes. There are no long-term contracts for Free or Pro tiers. Cancel anytime from your dashboard. You retain access until the end of your billing period. Your data is preserved for 90 days after cancellation (you can delete it sooner if you prefer).'
      },
      {
        question: 'Do you offer discounts?',
        answer: 'We provide significant discounts for academic institutions (.edu emails), registered non-profits (501c3 verification), and annual prepayment (save 20%). Enterprise volume discounts are available based on usage commitments. Contact sales@lukhas.ai for custom pricing.'
      },
      {
        question: 'What payment methods do you accept?',
        answer: 'We accept all major credit cards (Visa, Mastercard, Amex), ACH transfers for annual plans, and wire transfers for Enterprise customers. International payments supported via Stripe. Enterprise customers can arrange invoicing and purchase orders.'
      }
    ]
  },
  {
    category: 'Use Cases & Integration',
    questions: [
      {
        question: 'What can I build with LUKHAS?',
        answer: 'LUKHAS could power conversational interfaces, creative content generation, intelligent decision support systems, adaptive learning platforms, mental health support tools, code understanding assistants, and more. Any application that benefits from consciousness-inspired understanding, context awareness, and ethical reasoning is a great fit.'
      },
      {
        question: 'How long does integration take?',
        answer: 'Simple integrations (API calls from existing apps) can be done in hours. Complex integrations (custom consciousness profiles, multi-star coordination, bio-adaptation training) typically take 1-2 weeks. Enterprise deployments with custom models and on-premise setup range from 4-12 weeks depending on requirements.'
      },
      {
        question: 'Can LUKHAS integrate with my existing systems?',
        answer: 'Yes! Our REST API integrates with any system that can make HTTP requests. We provide webhooks for async workflows, SDKs for popular languages, and pre-built connectors for platforms like Slack, Discord, Salesforce, and Zendesk. Enterprise customers get custom integration support.'
      },
      {
        question: 'Do you provide implementation support?',
        answer: 'Pro tier will include priority email support with target <24hr response times. Enterprise partners will receive dedicated success managers, implementation workshops, architecture reviews, and hands-on integration assistance. During early access, contact us to discuss onboarding and integration support.'
      },
      {
        question: 'What is bio-adaptation training?',
        answer: 'Bio-adaptation allows LUKHAS to learn from your specific use case and improve organically over time. You provide examples, feedback, and corrections - the Bio star adapts its behavior based on this guidance. Unlike traditional ML retraining, bio-adaptation happens continuously and transparently.'
      }
    ]
  },
  {
    category: 'Community & Support',
    questions: [
      {
        question: 'Where can I get help?',
        answer: 'When the platform launches: Free tier will have community forums and documentation. Pro tier will include priority email support (target <24hr response). Enterprise will receive dedicated Slack channel, account manager, and 24/7 incident response. During early access, reach out via /contact for direct support.'
      },
      {
        question: 'Is there a developer community?',
        answer: 'We are building a developer community! Follow development updates on GitHub at github.com/LukhasAI, connect with the project at /contact, and stay tuned for Discord server launch, virtual workshops, and consciousness technology events. Early contributors welcome.'
      },
      {
        question: 'How can I contribute to LUKHAS?',
        answer: 'We welcome early contributors! Follow the project on GitHub for development updates, test early access features, provide feedback on documentation, write about your exploration experiences, and help shape consciousness technology. Contact us via /contact to discuss partnership opportunities.'
      },
      {
        question: 'Do you offer training and workshops?',
        answer: 'We plan to offer free online workshops, intensive training programs for teams, and on-site workshops for Enterprise partners. During early access, contact us to discuss tailored onboarding sessions. Documentation and tutorials are being developed at lukhas.dev.'
      }
    ]
  }
]

export default function FAQPage() {
  const [openQuestion, setOpenQuestion] = useState<string | null>(null)

  const toggleQuestion = (categoryIdx: number, questionIdx: number) => {
    const key = `${categoryIdx}-${questionIdx}`
    setOpenQuestion(openQuestion === key ? null : key)
  }

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
          <HeaderNavLink href="/technology">Technology</HeaderNavLink>
          <HeaderNavLink href="/pricing">Pricing</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.dev">Developers</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
          <Button className="bg-dream-gradient text-white">
            Start Free
          </Button>
        </HeaderActions>
      </Header>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-6 flex justify-center">
            <HelpCircle className="w-16 h-16 text-dream-ethereal animate-pulse" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Frequently Asked <span className="text-transparent bg-clip-text bg-dream-gradient">Questions</span>
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-3xl mx-auto">
            Everything you need to know about LUKHAS consciousness technology
          </p>
        </div>
      </section>

      {/* FAQ Categories */}
      {faqCategories.map((category, categoryIdx) => (
        <section
          key={categoryIdx}
          className={`py-16 px-6 ${categoryIdx % 2 === 0 ? 'bg-consciousness-deep' : 'bg-consciousness-deep/80'}`}
        >
          <div className="max-w-4xl mx-auto">
            {/* Category Title */}
            <h2 className="text-3xl font-light tracking-wide mb-8 text-dream-ethereal">
              {category.category}
            </h2>

            {/* Questions */}
            <div className="space-y-4">
              {category.questions.map((item, questionIdx) => {
                const key = `${categoryIdx}-${questionIdx}`
                const isOpen = openQuestion === key

                return (
                  <GlassCard key={questionIdx} className="border-dream-ethereal/20">
                    <button
                      className="w-full p-6 text-left"
                      onClick={() => toggleQuestion(categoryIdx, questionIdx)}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <h3 className="text-lg font-medium text-awareness-silver pr-4">
                          {item.question}
                        </h3>
                        <div
                          className={`transform transition-transform flex-shrink-0 ${
                            isOpen ? 'rotate-180' : ''
                          }`}
                        >
                          <ChevronDown className="w-5 h-5 text-dream-ethereal" strokeWidth={2} />
                        </div>
                      </div>

                      {isOpen && (
                        <div className="mt-4 text-awareness-silver/80 leading-relaxed">
                          {item.answer}
                        </div>
                      )}
                    </button>
                  </GlassCard>
                )
              })}
            </div>
          </div>
        </section>
      ))}

      {/* Still Have Questions CTA */}
      <section className="py-24 px-6 bg-dream-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Still Have Questions?
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Our team is here to help you understand consciousness technology and find the right solution
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            <a href="/contact">
              <Button size="lg" className="bg-white text-dream-ethereal px-12 py-6 text-lg hover:bg-awareness-silver">
                Contact Support
              </Button>
            </a>
            <a href="https://lukhas.dev/docs" target="_blank" rel="noopener noreferrer">
              <Button size="lg" variant="ghost" className="bg-white/10 text-white px-12 py-6 text-lg hover:bg-white/20">
                Read Documentation
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Platform</h3>
          <ul className="space-y-2">
            <li><a href="/" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Home</a></li>
            <li><a href="/playground" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Playground</a></li>
            <li><a href="/technology" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Technology</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Developers</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.dev" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Documentation</a></li>
            <li><a href="https://lukhas.io" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">API Reference</a></li>
            <li><a href="https://lukhas.xyz" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Experiments</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Company</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.com" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Enterprise</a></li>
            <li><a href="https://lukhas.com/#team" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Team</a></li>
            <li><a href="https://lukhas.com/#careers" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Careers</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Compliance</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.us" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">US Compliance</a></li>
            <li><a href="https://lukhas.eu" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">EU Compliance</a></li>
            <li><a href="/privacy" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Privacy Policy</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

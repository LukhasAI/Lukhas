import { Metadata } from 'next'
import { MatrizTransparencyBox } from '../../components/transparency-box'
import CalmModeToggle from '../../components/calm-mode-toggle'

// JSON-LD Schema for MATRIZ product
const matrizJsonLD = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Matriz",
  "description": "AI decision traceability and governance layer for transparent AI systems",
  "applicationCategory": "AI Governance",
  "operatingSystem": "Cross-platform",
  "url": "https://lukhas.ai/matriz",
  "author": {
    "@type": "Organization", 
    "name": "LUKHAS AI",
    "url": "https://lukhas.ai"
  },
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/InStock",
    "priceSpecification": {
      "@type": "PriceSpecification",
      "description": "Contact for pricing"
    }
  },
  "featureList": [
    "AI decision traceability",
    "Real-time audit trails", 
    "Governance integration",
    "Compliance monitoring",
    "Trinity Framework compatibility"
  ],
  "requirements": "LUKHAS Core Identity System v2.1+",
  "softwareHelp": "https://lukhas.ai/docs",
  "license": "https://lukhas.ai/license"
}

export const metadata: Metadata = {
  title: 'Matriz - AI Decision Traceability | LUKHAS AI',
  description: 'Transparent AI decision-making with real-time audit trails. Matriz provides governance and traceability for AI systems requiring auditability.',
  canonical: 'https://lukhas.ai/matriz',
  openGraph: {
    title: 'Matriz - AI Decision Traceability',
    description: 'Transparent AI decision-making with real-time audit trails and governance integration.',
    url: 'https://lukhas.ai/matriz',
    siteName: 'LUKHAS AI',
    type: 'website',
    images: [
      {
        url: '/assets/matriz-og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Matriz AI Decision Traceability System'
      }
    ]
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Matriz - AI Decision Traceability',
    description: 'Transparent AI decision-making with real-time audit trails.',
    images: ['/assets/matriz-twitter-image.jpg']
  },
  keywords: [
    'AI traceability',
    'AI governance', 
    'decision transparency',
    'AI audit trails',
    'LUKHAS AI',
    'AI compliance',
    'ethical AI'
  ]
}

export default function MatrizPage() {
  return (
    <>
      {/* JSON-LD Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(matrizJsonLD) }}
      />

      <main className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
        {/* Hero Section with MATRIZ Wordmark */}
        <section className="relative px-6 py-20 text-center">
          <div className="max-w-4xl mx-auto">
            {/* MΛTRIZ Display Wordmark - Λ as visual element with aria-label */}
            <h1 className="text-6xl md:text-8xl font-thin tracking-wider text-white mb-6" aria-label="Matriz">
              M<span className="text-purple-400 font-extralight">Λ</span>TRIZ
            </h1>
            
            {/* Poetic Layer (≤40 words) */}
            <div data-tone="poetic" className="mb-8">
              <p className="text-xl text-purple-200 font-light leading-relaxed max-w-2xl mx-auto">
                Where every decision becomes traceable light, flowing through the fabric of conscious architecture.
              </p>
            </div>

            {/* Plain Layer */}
            <div data-tone="plain" className="mb-12">
              <p className="text-lg text-gray-300 max-w-3xl mx-auto leading-relaxed">
                Matriz tracks how AI makes decisions. It creates records you can review later. This helps you understand and trust AI choices. It works with other LUKHAS tools.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900">
                Start Tracing
              </button>
              <a 
                href="/docs/matriz" 
                className="border border-purple-400 text-purple-400 hover:bg-purple-400 hover:text-white px-8 py-3 rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900"
              >
                Documentation
              </a>
            </div>
          </div>
        </section>

        {/* Technical Layer */}
        <section data-tone="technical" className="px-6 py-16 border-t border-white/10">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-semibold text-white mb-8 text-center">Technical Specifications</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold text-purple-400 mb-3">Performance Metrics</h3>
                  <ul className="text-gray-300 space-y-2">
                    <li>• Real-time tracing latency: &lt;100ms p95</li>
                    <li>• Audit coverage: 85-95% (configuration dependent)</li>
                    <li>• Storage efficiency: 10:1 compression ratio</li>
                    <li>• Integration overhead: &lt;5% system resources</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-purple-400 mb-3">Dependencies & Requirements</h3>
                  <ul className="text-gray-300 space-y-2">
                    <li>• LUKHAS Core Identity System v2.1+</li>
                    <li>• Guardian System for ethical oversight</li>
                    <li>• Memory system integration required</li>
                    <li>• Minimum 4GB RAM, 10GB storage</li>
                  </ul>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold text-purple-400 mb-3">Known Limitations</h3>
                  <ul className="text-gray-300 space-y-2">
                    <li>• Does not guarantee decision accuracy</li>
                    <li>• Cannot trace external AI system decisions</li>
                    <li>• Real-time monitoring impacts latency</li>
                    <li>• Requires network connectivity for distributed tracing</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-purple-400 mb-3">Integration Sources</h3>
                  <ul className="text-gray-300 space-y-2">
                    <li>• Uses OpenAI APIs for language processing</li>
                    <li>• Integrates with Anthropic Claude for reasoning</li>
                    <li>• Compatible with Google Gemini workflows</li>
                    <li>• <a href="/docs/api" className="text-purple-400 hover:text-purple-300">Full API documentation</a></li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Transparency Box - Always Visible */}
        <section className="px-6 py-16 border-t border-white/10">
          <div className="max-w-2xl mx-auto">
            <MatrizTransparencyBox defaultExpanded={false} />
          </div>
        </section>

        {/* Features Grid */}
        <section className="px-6 py-16 border-t border-white/10">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-semibold text-white mb-12 text-center">Key Capabilities</h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-white/5 border border-white/10 rounded-lg p-6">
                <div className="text-3xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-white mb-3">Decision Tracking</h3>
                <p className="text-gray-300 leading-relaxed">
                  Real-time monitoring of AI decision processes with complete audit trails and reasoning chain visualization.
                </p>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-lg p-6">
                <div className="text-3xl mb-4">🛡️</div>
                <h3 className="text-xl font-semibold text-white mb-3">Governance Integration</h3>
                <p className="text-gray-300 leading-relaxed">
                  Seamless integration with Guardian System for ethical oversight and compliance validation.
                </p>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-lg p-6">
                <div className="text-3xl mb-4">⚛️</div>
                <h3 className="text-xl font-semibold text-white mb-3">Trinity Framework</h3>
                <p className="text-gray-300 leading-relaxed">
                  Full compatibility with LUKHAS Trinity Framework for identity, consciousness, and guardian coordination.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="px-6 py-12 border-t border-white/10">
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-gray-400 mb-4">
              Part of the LUKHAS AI ecosystem for transparent and trustworthy AI systems.
            </p>
            <div className="flex justify-center space-x-6 text-sm">
              <a href="/docs" className="text-purple-400 hover:text-purple-300">Documentation</a>
              <a href="/support" className="text-purple-400 hover:text-purple-300">Support</a>
              <a href="/privacy" className="text-purple-400 hover:text-purple-300">Privacy</a>
              <a href="/terms" className="text-purple-400 hover:text-purple-300">Terms</a>
            </div>
          </div>
        </footer>

        {/* Calm Mode Toggle */}
        <CalmModeToggle />
      </main>
    </>
  )
}
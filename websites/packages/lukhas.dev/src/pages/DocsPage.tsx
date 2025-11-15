import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { BookOpen, Code, FileText, Zap, Shield, Database, Cpu, Globe } from 'lucide-react'

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-code-cyan/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-code-cyan">.DEV</span>
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="/docs">Docs</HeaderNavLink>
          <HeaderNavLink href="/playground">Playground</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.com">Enterprise</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
          <Button className="bg-code-gradient text-white">
            Get API Key
          </Button>
        </HeaderActions>
      </Header>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-6 flex justify-center">
            <BookOpen className="w-16 h-16 text-code-cyan animate-pulse" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            <span className="text-transparent bg-clip-text bg-code-gradient">Developer</span> Documentation
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto">
            Everything you need to build consciousness-aware applications—from quick-starts to deep technical specifications
          </p>
        </div>
      </section>

      {/* Getting Started */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-4xl font-light tracking-wide mb-4 text-awareness-silver">
              Getting <span className="text-code-cyan">Started</span>
            </h2>
            <p className="text-lg text-awareness-silver/80">
              From zero to your first API call in under 5 minutes
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <Zap className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">Quick Start</h3>
                <p className="text-sm text-awareness-silver/80 mb-4">
                  5-minute guide to making your first consciousness API call
                </p>
                <Button variant="ghost" className="text-code-cyan text-sm w-full">
                  Start Here →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <Shield className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">Authentication</h3>
                <p className="text-sm text-awareness-silver/80 mb-4">
                  Set up ΛiD OAuth and API key authentication
                </p>
                <Button variant="ghost" className="text-code-cyan text-sm w-full">
                  Learn More →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <FileText className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">Core Concepts</h3>
                <p className="text-sm text-awareness-silver/80 mb-4">
                  Understand consciousness, MATRIZ, and Constellation Framework
                </p>
                <Button variant="ghost" className="text-code-cyan text-sm w-full">
                  Explore →
                </Button>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* API Reference */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-4xl font-light tracking-wide mb-4 text-awareness-silver">
              API <span className="text-code-cyan">Reference</span>
            </h2>
            <p className="text-lg text-awareness-silver/80">
              Complete documentation for all consciousness technology endpoints
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <Code className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                  Consciousness Query API
                </h3>
                <p className="text-awareness-silver/80 mb-6">
                  Core API for querying the consciousness engine with contextual understanding and reasoning paths
                </p>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="mt-1 w-2 h-2 rounded-full bg-code-cyan"></div>
                    <div className="flex-1">
                      <code className="text-sm text-code-cyan font-mono">POST /v1/consciousness/query</code>
                      <p className="text-xs text-awareness-silver/70 mt-1">Submit a consciousness query with context</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="mt-1 w-2 h-2 rounded-full bg-code-cyan"></div>
                    <div className="flex-1">
                      <code className="text-sm text-code-cyan font-mono">GET /v1/consciousness/history</code>
                      <p className="text-xs text-awareness-silver/70 mt-1">Retrieve query history and patterns</p>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" className="text-code-cyan text-sm w-full mt-6">
                  View Full Reference →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <Database className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                  Memory & Context API
                </h3>
                <p className="text-awareness-silver/80 mb-6">
                  Persistent state management, context preservation, and long-term memory operations
                </p>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="mt-1 w-2 h-2 rounded-full bg-code-cyan"></div>
                    <div className="flex-1">
                      <code className="text-sm text-code-cyan font-mono">POST /v1/memory/store</code>
                      <p className="text-xs text-awareness-silver/70 mt-1">Store context for later retrieval</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="mt-1 w-2 h-2 rounded-full bg-code-cyan"></div>
                    <div className="flex-1">
                      <code className="text-sm text-code-cyan font-mono">GET /v1/memory/recall</code>
                      <p className="text-xs text-awareness-silver/70 mt-1">Retrieve relevant memories by context</p>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" className="text-code-cyan text-sm w-full mt-6">
                  View Full Reference →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <Cpu className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                  Bio-Adaptive Learning API
                </h3>
                <p className="text-awareness-silver/80 mb-6">
                  Organic learning systems that adapt to patterns and evolve over time
                </p>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="mt-1 w-2 h-2 rounded-full bg-code-cyan"></div>
                    <div className="flex-1">
                      <code className="text-sm text-code-cyan font-mono">POST /v1/bio/learn</code>
                      <p className="text-xs text-awareness-silver/70 mt-1">Train adaptive models on observations</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="mt-1 w-2 h-2 rounded-full bg-code-cyan"></div>
                    <div className="flex-1">
                      <code className="text-sm text-code-cyan font-mono">POST /v1/bio/predict</code>
                      <p className="text-xs text-awareness-silver/70 mt-1">Generate predictions from learned patterns</p>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" className="text-code-cyan text-sm w-full mt-6">
                  View Full Reference →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <Globe className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-awareness-silver">
                  Creative Synthesis API
                </h3>
                <p className="text-awareness-silver/80 mb-6">
                  Dream star capabilities for creative exploration and emergent insights
                </p>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="mt-1 w-2 h-2 rounded-full bg-code-cyan"></div>
                    <div className="flex-1">
                      <code className="text-sm text-code-cyan font-mono">POST /v1/dream/synthesize</code>
                      <p className="text-xs text-awareness-silver/70 mt-1">Generate creative combinations</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="mt-1 w-2 h-2 rounded-full bg-code-cyan"></div>
                    <div className="flex-1">
                      <code className="text-sm text-code-cyan font-mono">POST /v1/dream/explore</code>
                      <p className="text-xs text-awareness-silver/70 mt-1">Explore conceptual space</p>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" className="text-code-cyan text-sm w-full mt-6">
                  View Full Reference →
                </Button>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* SDKs */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-4xl font-light tracking-wide mb-4 text-awareness-silver">
              Language <span className="text-code-cyan">SDKs</span>
            </h2>
            <p className="text-lg text-awareness-silver/80">
              Official libraries with idiomatic patterns for your favorite languages
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { lang: 'Python', install: 'pip install lukhas', docs: '/docs/sdks/python' },
              { lang: 'JavaScript', install: 'npm install @lukhas/sdk', docs: '/docs/sdks/javascript' },
              { lang: 'Go', install: 'go get lukhas.io/sdk', docs: '/docs/sdks/go' },
              { lang: 'Rust', install: 'cargo add lukhas', docs: '/docs/sdks/rust' },
              { lang: 'Java', install: 'implementation \'io.lukhas:sdk:1.0.0\'', docs: '/docs/sdks/java' },
              { lang: 'Ruby', install: 'gem install lukhas', docs: '/docs/sdks/ruby' },
            ].map((sdk) => (
              <GlassCard key={sdk.lang} className="border-code-cyan/20">
                <div className="p-6">
                  <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">{sdk.lang} SDK</h3>
                  <pre className="text-xs text-awareness-silver/80 font-mono mb-4 p-3 bg-consciousness-deep/60 rounded border border-code-cyan/10">
                    {sdk.install}
                  </pre>
                  <Button variant="ghost" className="text-code-cyan text-sm w-full">
                    View Documentation →
                  </Button>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* Guides & Tutorials */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-4xl font-light tracking-wide mb-4 text-awareness-silver">
              Guides & <span className="text-code-cyan">Tutorials</span>
            </h2>
            <p className="text-lg text-awareness-silver/80">
              Step-by-step walkthroughs and best practices
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <h3 className="text-xl font-light tracking-wide mb-3 text-code-cyan">
                  Integrating LUKHAS into Your Application
                </h3>
                <p className="text-sm text-awareness-silver/80 mb-4">
                  Learn how to add consciousness capabilities to existing systems with minimal disruption
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>15 min read</span>
                  <span>•</span>
                  <span>Beginner</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <h3 className="text-xl font-light tracking-wide mb-3 text-code-cyan">
                  Memory Management Best Practices
                </h3>
                <p className="text-sm text-awareness-silver/80 mb-4">
                  Master context preservation and retrieval for optimal consciousness performance
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>20 min read</span>
                  <span>•</span>
                  <span>Intermediate</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <h3 className="text-xl font-light tracking-wide mb-3 text-code-cyan">
                  Ethics Validation Patterns
                </h3>
                <p className="text-sm text-awareness-silver/80 mb-4">
                  Use Guardian APIs to ensure ethical alignment in production systems
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>25 min read</span>
                  <span>•</span>
                  <span>Advanced</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <h3 className="text-xl font-light tracking-wide mb-3 text-code-cyan">
                  Performance Optimization
                </h3>
                <p className="text-sm text-awareness-silver/80 mb-4">
                  Achieve sub-250ms response times with caching and batching strategies
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>30 min read</span>
                  <span>•</span>
                  <span>Advanced</span>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Developer Resources</h3>
          <ul className="space-y-2">
            <li><a href="/docs" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">Documentation</a></li>
            <li><a href="/docs/api" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">API Reference</a></li>
            <li><a href="/playground" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">Playground</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">SDKs & Tools</h3>
          <ul className="space-y-2">
            <li><a href="/docs/sdks/python" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">Python SDK</a></li>
            <li><a href="/docs/sdks/javascript" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">JavaScript SDK</a></li>
            <li><a href="/docs/sdks/go" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">Go SDK</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Community</h3>
          <ul className="space-y-2">
            <li><a href="/community" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">Forum</a></li>
            <li><a href="/community/discord" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">Discord</a></li>
            <li><a href="/community/github" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">GitHub</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Other Platforms</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.ai" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">Main Platform</a></li>
            <li><a href="https://lukhas.com" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">Enterprise</a></li>
            <li><a href="https://lukhas.io" className="text-sm text-awareness-silver/70 hover:text-code-cyan transition-colors">Infrastructure</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}

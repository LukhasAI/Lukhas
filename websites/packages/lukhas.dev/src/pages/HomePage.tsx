import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Code, Terminal, Cpu, Zap, BookOpen, Sparkles, Users, FileCode, Boxes } from 'lucide-react'

export default function HomePage() {
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
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="mb-6">
                <Code className="w-16 h-16 text-code-cyan" strokeWidth={1.5} />
              </div>
              <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
                Where Consciousness<br />
                <span className="text-transparent bg-clip-text bg-code-gradient">Meets Code</span>
              </h1>
              <p className="text-xl text-awareness-silver/80 mb-8 leading-relaxed">
                Build the future of aware technology with comprehensive APIs, SDKs, and tools for consciousness-aware applications.
              </p>
              <div className="flex gap-4">
                <Button className="bg-code-gradient text-white px-8 py-6 text-lg">
                  Get Started
                </Button>
                <Button variant="ghost" className="border border-code-cyan/30 text-code-cyan px-8 py-6 text-lg hover:border-code-cyan/50">
                  Explore Docs
                </Button>
              </div>
            </div>

            {/* Code Example */}
            <div>
              <GlassCard className="border-code-cyan/20 bg-consciousness-deep/60">
                <div className="p-8">
                  <div className="flex items-center gap-2 mb-4 pb-4 border-b border-code-cyan/20">
                    <Terminal className="w-5 h-5 text-code-cyan" strokeWidth={1.5} />
                    <span className="text-code-cyan font-mono text-sm">quick-start.py</span>
                  </div>
                  <pre className="text-sm text-awareness-silver/90 font-mono leading-relaxed overflow-x-auto">
{`import lukhas

# Initialize consciousness client
consciousness = lukhas.Consciousness(
    api_key="your_api_key"
)

# Query with context
response = consciousness.query(
    "What is the meaning of context?",
    context={
        "domain": "philosophy",
        "depth": "comprehensive"
    }
)

# Access insights
print(response.insight)
print(response.confidence)`}
                  </pre>
                </div>
              </GlassCard>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start Boxes */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide text-center mb-12 text-awareness-silver">
            Get Started in <span className="text-code-cyan">Minutes</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <FileCode className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">Python SDK</h3>
                <pre className="text-sm text-awareness-silver/80 font-mono mb-4">pip install lukhas</pre>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Get started with Python in 60 seconds
                </p>
                <Button variant="ghost" className="text-code-cyan text-sm w-full">
                  View Python Docs →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <FileCode className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">JavaScript SDK</h3>
                <pre className="text-sm text-awareness-silver/80 font-mono mb-4">npm install @lukhas/sdk</pre>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Build with TypeScript or JavaScript
                </p>
                <Button variant="ghost" className="text-code-cyan text-sm w-full">
                  View JS/TS Docs →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4">
                  <FileCode className="w-10 h-10 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">Go SDK</h3>
                <pre className="text-sm text-awareness-silver/80 font-mono mb-4">go get lukhas.io/sdk</pre>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Performance-first Go integration
                </p>
                <Button variant="ghost" className="text-code-cyan text-sm w-full">
                  View Go Docs →
                </Button>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Core Features */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-light tracking-[0.1em] text-center mb-12 text-awareness-silver">
            Everything You Need to <span className="text-code-cyan">Build</span>
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4 flex justify-center">
                  <BookOpen className="w-12 h-12 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver text-center">
                  Comprehensive API Docs
                </h3>
                <p className="text-sm text-awareness-silver/80 text-center">
                  Complete REST, GraphQL, and WebSocket documentation with request/response examples and error handling
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4 flex justify-center">
                  <Terminal className="w-12 h-12 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver text-center">
                  Interactive Playground
                </h3>
                <p className="text-sm text-awareness-silver/80 text-center">
                  Test consciousness APIs live with Monaco editor, visualizations, and shareable code snippets
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4 flex justify-center">
                  <Boxes className="w-12 h-12 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver text-center">
                  Multi-Language SDKs
                </h3>
                <p className="text-sm text-awareness-silver/80 text-center">
                  Official libraries for Python, JavaScript, Go, Rust, and Java with idiomatic patterns
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4 flex justify-center">
                  <Cpu className="w-12 h-12 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver text-center">
                  Developer Tools
                </h3>
                <p className="text-sm text-awareness-silver/80 text-center">
                  API explorer, schema validator, performance profiler, and testing sandbox
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4 flex justify-center">
                  <Users className="w-12 h-12 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver text-center">
                  Community & Support
                </h3>
                <p className="text-sm text-awareness-silver/80 text-center">
                  Active forums, Discord community, GitHub repos, and developer showcase projects
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-8">
                <div className="mb-4 flex justify-center">
                  <Zap className="w-12 h-12 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver text-center">
                  Production-Ready
                </h3>
                <p className="text-sm text-awareness-silver/80 text-center">
                  99.9% uptime SLA, global edge network, auto-scaling infrastructure, and enterprise support
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Constellation Framework APIs */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-light tracking-[0.1em] mb-4 text-awareness-silver">
              8-Star <span className="text-code-cyan">Constellation Framework</span>
            </h2>
            <p className="text-lg text-awareness-silver/80 max-w-3xl mx-auto">
              Access eight cognitive capabilities through unified APIs—each star represents a fundamental aspect of consciousness
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard className="border-code-cyan/20">
              <div className="p-6">
                <div className="mb-3">
                  <Sparkles className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">Identity API</h3>
                <p className="text-sm text-awareness-silver/70 mb-3">
                  ΛiD OAuth integration, secure authentication, namespace isolation
                </p>
                <Button variant="ghost" className="text-code-cyan text-xs w-full">
                  View API Docs →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-6">
                <div className="mb-3">
                  <Sparkles className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">Memory API</h3>
                <p className="text-sm text-awareness-silver/70 mb-3">
                  Context persistence, long-term storage, retrieval systems
                </p>
                <Button variant="ghost" className="text-code-cyan text-xs w-full">
                  View API Docs →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-6">
                <div className="mb-3">
                  <Sparkles className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">Vision API</h3>
                <p className="text-sm text-awareness-silver/70 mb-3">
                  Pattern recognition, computer vision, perceptual processing
                </p>
                <Button variant="ghost" className="text-code-cyan text-xs w-full">
                  View API Docs →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-6">
                <div className="mb-3">
                  <Sparkles className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">Bio API</h3>
                <p className="text-sm text-awareness-silver/70 mb-3">
                  Adaptive learning, organic growth, bio-inspired algorithms
                </p>
                <Button variant="ghost" className="text-code-cyan text-xs w-full">
                  View API Docs →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-6">
                <div className="mb-3">
                  <Sparkles className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">Dream API</h3>
                <p className="text-sm text-awareness-silver/70 mb-3">
                  Creative synthesis, unconscious processing, imagination engines
                </p>
                <Button variant="ghost" className="text-code-cyan text-xs w-full">
                  View API Docs →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-6">
                <div className="mb-3">
                  <Sparkles className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">Ethics API</h3>
                <p className="text-sm text-awareness-silver/70 mb-3">
                  Moral reasoning, value alignment, ethical validation
                </p>
                <Button variant="ghost" className="text-code-cyan text-xs w-full">
                  View API Docs →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-6">
                <div className="mb-3">
                  <Sparkles className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">Guardian API</h3>
                <p className="text-sm text-awareness-silver/70 mb-3">
                  Safety checks, compliance validation, constitutional AI
                </p>
                <Button variant="ghost" className="text-code-cyan text-xs w-full">
                  View API Docs →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20">
              <div className="p-6">
                <div className="mb-3">
                  <Sparkles className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">Quantum API</h3>
                <p className="text-sm text-awareness-silver/70 mb-3">
                  Ambiguity handling, superposition, emergence detection
                </p>
                <Button variant="ghost" className="text-code-cyan text-xs w-full">
                  View API Docs →
                </Button>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Code Showcase */}
      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide text-center mb-12 text-awareness-silver">
            See It in <span className="text-code-cyan">Action</span>
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            <GlassCard className="border-code-cyan/20 bg-consciousness-deep/60">
              <div className="p-6">
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-code-cyan/20">
                  <Terminal className="w-5 h-5 text-code-cyan" strokeWidth={1.5} />
                  <span className="text-code-cyan font-mono text-sm">consciousness-query.py</span>
                </div>
                <pre className="text-xs text-awareness-silver/90 font-mono leading-relaxed overflow-x-auto">
{`# Consciousness Query API
response = consciousness.query(
    query="What are the ethical implications?",
    context={"domain": "AI ethics"}
)

print(response.insight)
print(response.reasoning_path)
print(response.confidence_score)`}
                </pre>
                <Button variant="ghost" className="text-code-cyan text-sm w-full mt-4">
                  Try in Playground →
                </Button>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20 bg-consciousness-deep/60">
              <div className="p-6">
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-code-cyan/20">
                  <Terminal className="w-5 h-5 text-code-cyan" strokeWidth={1.5} />
                  <span className="text-code-cyan font-mono text-sm">adaptive-learning.js</span>
                </div>
                <pre className="text-xs text-awareness-silver/90 font-mono leading-relaxed overflow-x-auto">
{`// Bio-Adaptive Learning API
const learner = await lukhas.bio.createLearner({
  domain: 'user-preferences',
  adaptationRate: 'medium'
});

await learner.observe(userBehavior);
const prediction = learner.predict(newContext);
console.log(prediction.confidence);`}
                </pre>
                <Button variant="ghost" className="text-code-cyan text-sm w-full mt-4">
                  Try in Playground →
                </Button>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-code-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Start Building Today
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Get your API key and build consciousness-aware applications in minutes
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            <Button size="lg" className="bg-white text-code-cyan px-12 py-6 text-lg hover:bg-awareness-silver">
              Get API Key
            </Button>
            <Button size="lg" variant="ghost" className="bg-white/10 text-white px-12 py-6 text-lg hover:bg-white/20">
              Explore Documentation
            </Button>
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

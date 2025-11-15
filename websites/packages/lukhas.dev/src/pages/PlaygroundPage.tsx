import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Terminal, Play, Save, Share2, Code, Sparkles, FileCode } from 'lucide-react'

export default function PlaygroundPage() {
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
      <section className="pt-32 pb-8 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-6 flex justify-center">
            <Terminal className="w-16 h-16 text-code-cyan animate-pulse" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Interactive <span className="text-transparent bg-clip-text bg-code-gradient">Playground</span>
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto mb-8">
            Test consciousness APIs live with real-time code execution, visualizations, and shareable snippets
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button className="bg-code-gradient text-white">
              <FileCode className="w-4 h-4 mr-2" strokeWidth={1.5} />
              Load Example
            </Button>
            <Button variant="ghost" className="border border-code-cyan/30 text-code-cyan hover:border-code-cyan/50">
              <Share2 className="w-4 h-4 mr-2" strokeWidth={1.5} />
              Share Snippet
            </Button>
          </div>
        </div>
      </section>

      {/* Playground Interface */}
      <section className="py-8 px-6">
        <div className="max-w-[1800px] mx-auto">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Code Editor Panel */}
            <GlassCard className="border-code-cyan/20">
              <div className="flex items-center justify-between p-4 border-b border-code-cyan/20">
                <div className="flex items-center gap-3">
                  <Code className="w-5 h-5 text-code-cyan" strokeWidth={1.5} />
                  <span className="text-code-cyan font-mono text-sm">consciousness-query.py</span>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="ghost" className="text-code-cyan">
                    <Save className="w-4 h-4" strokeWidth={1.5} />
                  </Button>
                  <Button size="sm" className="bg-code-gradient text-white">
                    <Play className="w-4 h-4 mr-2" strokeWidth={1.5} />
                    Run
                  </Button>
                </div>
              </div>
              <div className="p-6 bg-consciousness-deep/60 min-h-[600px]">
                <pre className="text-sm text-awareness-silver/90 font-mono leading-relaxed">
{`import lukhas

# Initialize consciousness client
consciousness = lukhas.Consciousness(
    api_key="your_api_key"
)

# Query with context
response = consciousness.query(
    query="What are the ethical implications of AI autonomy?",
    context={
        "domain": "AI ethics",
        "depth": "comprehensive",
        "perspective": "multi-stakeholder"
    }
)

# Access response fields
print("Insight:", response.insight)
print("Reasoning Path:", response.reasoning_path)
print("Confidence:", response.confidence)
print("Ethical Alignment:", response.ethical_score)

# Visualize consciousness state
consciousness.visualize(response.state)`}
                </pre>
              </div>
            </GlassCard>

            {/* Output/Visualization Panel */}
            <GlassCard className="border-code-cyan/20">
              <div className="flex items-center justify-between p-4 border-b border-code-cyan/20">
                <div className="flex items-center gap-3">
                  <Terminal className="w-5 h-5 text-code-cyan" strokeWidth={1.5} />
                  <span className="text-code-cyan font-mono text-sm">output</span>
                </div>
                <div className="flex gap-2">
                  <span className="text-xs text-success-green flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-success-green"></span>
                    200 OK • 245ms
                  </span>
                </div>
              </div>
              <div className="p-6 bg-consciousness-deep/60 min-h-[600px]">
                {/* Visualization */}
                <div className="mb-6 p-4 border border-code-cyan/20 rounded">
                  <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-5 h-5 text-code-cyan" strokeWidth={1.5} />
                    <span className="text-code-cyan font-mono text-sm">Consciousness Visualization</span>
                  </div>
                  <div className="space-y-2">
                    {[
                      { label: 'Ethical Alignment', value: 92, color: 'bg-success-green' },
                      { label: 'Contextual Depth', value: 88, color: 'bg-code-cyan' },
                      { label: 'Reasoning Clarity', value: 95, color: 'bg-lambda-gold' },
                      { label: 'Multi-Perspective', value: 87, color: 'bg-info-blue' },
                    ].map((metric) => (
                      <div key={metric.label}>
                        <div className="flex justify-between text-xs text-awareness-silver/70 mb-1">
                          <span>{metric.label}</span>
                          <span>{metric.value}%</span>
                        </div>
                        <div className="h-2 bg-consciousness-deep/60 rounded overflow-hidden">
                          <div
                            className={`h-full ${metric.color}`}
                            style={{ width: `${metric.value}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* JSON Output */}
                <pre className="text-xs text-awareness-silver/90 font-mono leading-relaxed overflow-x-auto">
{`{
  "insight": "AI autonomy raises significant ethical considerations across multiple dimensions: accountability (who is responsible for autonomous decisions?), transparency (can we understand how autonomous systems make choices?), and human dignity (ensuring AI serves rather than replaces human agency). The challenge lies in balancing efficiency gains with maintaining meaningful human control and preserving core human values in AI-mediated decision spaces.",

  "reasoning_path": [
    "Identified multi-stakeholder framework",
    "Analyzed accountability dimensions",
    "Evaluated transparency requirements",
    "Assessed human dignity implications",
    "Synthesized ethical balance"
  ],

  "confidence": 0.92,
  "ethical_score": 0.95,

  "metadata": {
    "processing_time_ms": 245,
    "constellation_stars_used": [
      "Ethics", "Guardian", "Vision", "Memory"
    ],
    "context_depth": "comprehensive"
  }
}`}
                </pre>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Example Library */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h2 className="text-4xl font-light tracking-wide mb-4 text-awareness-silver">
              Example <span className="text-code-cyan">Library</span>
            </h2>
            <p className="text-lg text-awareness-silver/80">
              Explore pre-built examples to understand API capabilities
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <GlassCard className="border-code-cyan/20 hover:border-code-cyan/40 transition-colors cursor-pointer">
              <div className="p-6">
                <div className="mb-3">
                  <Code className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Consciousness Query
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Basic query with contextual understanding
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>Python</span>
                  <span>•</span>
                  <span>Beginner</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20 hover:border-code-cyan/40 transition-colors cursor-pointer">
              <div className="p-6">
                <div className="mb-3">
                  <Code className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Memory Persistence
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Store and recall context across sessions
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>JavaScript</span>
                  <span>•</span>
                  <span>Intermediate</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20 hover:border-code-cyan/40 transition-colors cursor-pointer">
              <div className="p-6">
                <div className="mb-3">
                  <Code className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Adaptive Learning
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Bio-inspired pattern learning and prediction
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>Go</span>
                  <span>•</span>
                  <span>Advanced</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20 hover:border-code-cyan/40 transition-colors cursor-pointer">
              <div className="p-6">
                <div className="mb-3">
                  <Code className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Creative Synthesis
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Dream star exploration and generation
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>Python</span>
                  <span>•</span>
                  <span>Intermediate</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20 hover:border-code-cyan/40 transition-colors cursor-pointer">
              <div className="p-6">
                <div className="mb-3">
                  <Code className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Ethics Validation
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Guardian API for ethical alignment checks
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>Rust</span>
                  <span>•</span>
                  <span>Advanced</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="border-code-cyan/20 hover:border-code-cyan/40 transition-colors cursor-pointer">
              <div className="p-6">
                <div className="mb-3">
                  <Code className="w-8 h-8 text-code-cyan" strokeWidth={1.5} />
                </div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Multi-Star Workflow
                </h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Combining multiple constellation capabilities
                </p>
                <div className="flex items-center gap-2 text-xs text-awareness-silver/60">
                  <span>JavaScript</span>
                  <span>•</span>
                  <span>Expert</span>
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

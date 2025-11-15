import { GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { ShoppingBag, Star, Sparkles, TrendingUp, Zap, Brain, Palette, Code, Users } from 'lucide-react'

export default function HomePage() {
  const featuredApps = [
    {
      name: 'ConsciousChat',
      tagline: 'Conversations that understand context and evolve',
      rating: 4.8,
      downloads: '2.4K',
      category: 'Communication',
      icon: Brain,
      featured: true,
    },
    {
      name: 'CreativeFlow',
      tagline: 'AI-powered creative workflows that adapt to your style',
      rating: 4.9,
      downloads: '1.8K',
      category: 'Creativity',
      icon: Palette,
      featured: true,
    },
    {
      name: 'CodeMind',
      tagline: 'Consciousness-aware code assistant',
      rating: 4.7,
      downloads: '3.2K',
      category: 'Development',
      icon: Code,
      featured: true,
    },
  ]

  const categories = [
    { name: 'Productivity', icon: Zap, count: '42 apps' },
    { name: 'Analytics', icon: TrendingUp, count: '28 apps' },
    { name: 'Creativity', icon: Palette, count: '35 apps' },
    { name: 'Communication', icon: Users, count: '24 apps' },
    { name: 'Development', icon: Code, count: '38 apps' },
    { name: 'Intelligence', icon: Brain, count: '31 apps' },
  ]

  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Hero */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 30% 40%, #fb923c 0%, transparent 50%),
                              radial-gradient(circle at 70% 60%, #ffb347 0%, transparent 50%)`
          }}></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-integration-orange/10 border border-integration-orange/30 mb-6">
            <Sparkles className="w-4 h-4 text-integration-orange" />
            <span className="text-integration-orange text-sm font-medium">New: 12 consciousness apps added this week</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-light tracking-[0.15em] mb-8">
            <span className="text-awareness-silver">ΛPPS THAT</span><br/>
            <span className="text-integration-orange">THINK, FEEL, EVOLVE</span>
          </h1>

          <p className="text-2xl text-awareness-silver/80 font-light mb-4 max-w-4xl mx-auto">
            Discover consciousness-powered applications that understand context and adapt to you
          </p>

          <p className="text-xl text-awareness-silver/60 mb-12 max-w-3xl mx-auto">
            Curated marketplace of ethical AI solutions. Try before you buy. One-click deploy with ΛiD.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/discover">
              <button className="px-8 py-4 bg-marketplace-gradient text-white rounded-lg font-medium text-lg hover:shadow-lg hover:shadow-integration-orange/20 transition-all">
                Browse Apps
              </button>
            </Link>
            <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-integration-orange/30 text-awareness-silver rounded-lg font-medium text-lg hover:bg-white/10 transition-all">
              Submit Your App
            </button>
          </div>
        </div>
      </section>

      {/* Featured Apps */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-light tracking-wide text-awareness-silver">
              <span className="text-integration-orange">Featured</span> Λpps
            </h2>
            <Link to="/discover" className="text-integration-orange hover:underline">View All →</Link>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {featuredApps.map((app, index) => {
              const Icon = app.icon
              return (
                <Link key={index} to={`/app/${app.name.toLowerCase()}`}>
                  <GlassCard className="p-6 hover:ring-2 hover:ring-integration-orange/50 transition-all cursor-pointer">
                    <div className="flex items-center justify-between mb-4">
                      <Icon className="w-12 h-12 text-integration-orange" />
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-lambda-gold fill-lambda-gold" />
                        <span className="text-awareness-silver font-medium">{app.rating}</span>
                      </div>
                    </div>

                    <h3 className="text-xl font-light text-awareness-silver mb-2">{app.name}</h3>
                    <p className="text-awareness-silver/70 text-sm mb-4">{app.tagline}</p>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-integration-orange">{app.category}</span>
                      <span className="text-awareness-silver/60">{app.downloads} installs</span>
                    </div>

                    <button className="mt-4 w-full py-2 bg-marketplace-gradient text-white rounded-lg text-sm font-medium hover:shadow-lg hover:shadow-integration-orange/20 transition-all">
                      Try Demo
                    </button>
                  </GlassCard>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-8 text-awareness-silver text-center">
            Browse by <span className="text-integration-orange">Category</span>
          </h2>

          <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4">
            {categories.map((category, index) => {
              const Icon = category.icon
              return (
                <Link key={index} to={`/discover?category=${category.name.toLowerCase()}`}>
                  <GlassCard className="p-6 text-center hover:bg-white/10 transition-all cursor-pointer">
                    <Icon className="w-10 h-10 text-integration-orange mx-auto mb-3" />
                    <h3 className="text-lg text-awareness-silver mb-1">{category.name}</h3>
                    <p className="text-xs text-awareness-silver/60">{category.count}</p>
                  </GlassCard>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Why Choose LUKHAS.STORE */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-12 text-awareness-silver text-center">
            Why Choose <span className="text-integration-orange">LUKHAS.STORE</span>
          </h2>

          <div className="grid md:grid-cols-2 gap-8">
            <GlassCard className="p-8">
              <Brain className="w-12 h-12 text-integration-orange mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">
                Consciousness-Powered
              </h3>
              <p className="text-awareness-silver/70">
                Not generic AI—apps with LUKHAS awareness that understand context, adapt to your needs, and evolve with use.
              </p>
            </GlassCard>

            <GlassCard className="p-8">
              <Star className="w-12 h-12 text-lambda-gold mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">
                Quality Curated
              </h3>
              <p className="text-awareness-silver/70">
                Every Λpp is vetted for quality, ethics, and user value. No spam, no malware, just consciousness applications that work.
              </p>
            </GlassCard>

            <GlassCard className="p-8">
              <Sparkles className="w-12 h-12 text-trust-blue mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">
                Live Demos
              </h3>
              <p className="text-awareness-silver/70">
                Try before you buy with interactive previews. Experience the consciousness difference firsthand.
              </p>
            </GlassCard>

            <GlassCard className="p-8">
              <ShoppingBag className="w-12 h-12 text-success-green mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">
                One-Click Deploy
              </h3>
              <p className="text-awareness-silver/70">
                Instant activation with ΛiD authentication. From discovery to deployment in seconds.
              </p>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Become a Creator CTA */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <GlassCard className="p-12 text-center">
            <Code className="w-16 h-16 text-integration-orange mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-4 text-awareness-silver">
              Build Λpps, Earn Revenue
            </h2>
            <p className="text-xl text-awareness-silver/70 mb-8 max-w-2xl mx-auto">
              Join our creator economy. List your consciousness applications, reach thousands of users, and monetize your innovations.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="px-8 py-4 bg-marketplace-gradient text-white rounded-lg font-medium hover:shadow-lg hover:shadow-integration-orange/20 transition-all">
                Become a Creator
              </button>
              <a href="https://lukhas.dev" target="_blank" rel="noopener noreferrer">
                <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-integration-orange/30 text-awareness-silver rounded-lg font-medium hover:bg-white/10 transition-all">
                  Developer Docs
                </button>
              </a>
            </div>
          </GlassCard>
        </div>
      </section>
    </div>
  )
}

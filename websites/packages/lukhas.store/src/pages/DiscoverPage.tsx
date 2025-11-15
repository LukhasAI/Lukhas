import { GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { Search, Star, Filter, Brain, Palette, Code, Zap, TrendingUp, Users } from 'lucide-react'

export default function DiscoverPage() {
  const apps = [
    { name: 'ConsciousChat', rating: 4.8, installs: '2.4K', category: 'Communication', icon: Brain, price: 'Free' },
    { name: 'CreativeFlow', rating: 4.9, installs: '1.8K', category: 'Creativity', icon: Palette, price: 'Free' },
    { name: 'CodeMind', rating: 4.7, installs: '3.2K', category: 'Development', icon: Code, price: 'Free' },
    { name: 'ProductivityPro', rating: 4.6, installs: '1.5K', category: 'Productivity', icon: Zap, price: 'Free' },
    { name: 'DataVision', rating: 4.8, installs: '980', category: 'Analytics', icon: TrendingUp, price: 'Free' },
    { name: 'TeamSync', rating: 4.5, installs: '1.2K', category: 'Communication', icon: Users, price: 'Free' },
  ]

  return (
    <div className="min-h-screen bg-consciousness-deep">
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-5xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Discover <span className="text-integration-orange">›pps</span>
          </h1>
          <p className="text-xl text-awareness-silver/70 max-w-3xl">
            Browse 198 consciousness-powered applications
          </p>
        </div>
      </section>

      <section className="py-8 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex gap-4 mb-8">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-awareness-silver/40" />
              <input
                type="text"
                placeholder="Search consciousness applications..."
                className="w-full pl-12 pr-4 py-3 bg-consciousness-deep/50 border border-integration-orange/30 rounded-lg text-awareness-silver placeholder-awareness-silver/40 focus:outline-none focus:ring-2 focus:ring-integration-orange"
              />
            </div>
            <button className="px-6 py-3 bg-white/5 border border-integration-orange/30 text-awareness-silver rounded-lg flex items-center gap-2 hover:bg-white/10">
              <Filter className="w-5 h-5" />
              Filters
            </button>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {apps.map((app, index) => {
              const Icon = app.icon
              return (
                <Link key={index} to={`/app/${app.name.toLowerCase()}`}>
                  <GlassCard className="p-6 hover:ring-2 hover:ring-integration-orange/50 transition-all cursor-pointer h-full">
                    <div className="flex items-center justify-between mb-4">
                      <Icon className="w-12 h-12 text-integration-orange" />
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-lambda-gold fill-lambda-gold" />
                        <span className="text-awareness-silver font-medium">{app.rating}</span>
                      </div>
                    </div>
                    <h3 className="text-xl font-light text-awareness-silver mb-2">{app.name}</h3>
                    <p className="text-awareness-silver/70 text-sm mb-4">
                      Consciousness-powered {app.category.toLowerCase()} application
                    </p>
                    <div className="flex items-center justify-between text-sm mb-4">
                      <span className="text-integration-orange">{app.category}</span>
                      <span className="text-awareness-silver/60">{app.installs} installs</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-awareness-silver font-medium">{app.price}</span>
                      <button className="px-4 py-2 bg-marketplace-gradient text-white rounded-lg text-sm font-medium hover:shadow-lg transition-all">
                        Try Demo
                      </button>
                    </div>
                  </GlassCard>
                </Link>
              )
            })}
          </div>
        </div>
      </section>
    </div>
  )
}

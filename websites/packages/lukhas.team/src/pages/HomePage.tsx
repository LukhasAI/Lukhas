import { GlassCard } from '@lukhas/ui'
import { Users, Calendar, FileText, MessageSquare, TrendingUp, Lock } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      <section className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-lambda-gold/10 border border-lambda-gold/30 mb-6">
            <Users className="w-4 h-4 text-lambda-gold" />
            <span className="text-lambda-gold text-sm font-medium">Internal Team Portal · Secure Access</span>
          </div>
          <h1 className="text-6xl md:text-7xl font-light tracking-[0.15em] mb-8">
            <span className="text-awareness-silver">LUKHAS</span><span className="text-lambda-gold">.TEAM</span>
          </h1>
          <p className="text-2xl text-awareness-silver/80 font-light mb-4 max-w-4xl mx-auto">
            Internal Team Collaboration & Project Management
          </p>
          <p className="text-xl text-awareness-silver/60 mb-12 max-w-3xl mx-auto">
            Secure portal for LUKHAS team members. Access internal tools, resources, and project dashboards.
          </p>
          <button className="px-8 py-4 bg-gradient-to-r from-lambda-gold to-warning-amber text-white rounded-lg font-medium">
            Sign In with ΛiD
          </button>
        </div>
      </section>

      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-8 text-awareness-silver text-center">
            Team <span className="text-lambda-gold">Resources</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <GlassCard className="p-8">
              <Calendar className="w-12 h-12 text-lambda-gold mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">Sprint Planning</h3>
              <p className="text-awareness-silver/70">Weekly sprints, task boards, velocity tracking</p>
            </GlassCard>
            <GlassCard className="p-8">
              <MessageSquare className="w-12 h-12 text-trust-blue mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">Team Chat</h3>
              <p className="text-awareness-silver/70">Secure internal communications and channels</p>
            </GlassCard>
            <GlassCard className="p-8">
              <FileText className="w-12 h-12 text-success-green mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">Documentation</h3>
              <p className="text-awareness-silver/70">Internal wikis, guides, and knowledge base</p>
            </GlassCard>
          </div>
        </div>
      </section>

      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-12 text-awareness-silver text-center">
            <span className="text-lambda-gold">Project</span> Dashboards
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <GlassCard className="p-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl text-awareness-silver">MATRIZ Development</h3>
                <TrendingUp className="w-6 h-6 text-success-green" />
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-awareness-silver/60">Sprint Progress</span>
                  <span className="text-success-green">87%</span>
                </div>
                <div className="w-full h-2 bg-consciousness-deep rounded-full">
                  <div className="h-full bg-success-green rounded-full" style={{width: '87%'}}></div>
                </div>
              </div>
            </GlassCard>
            <GlassCard className="p-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl text-awareness-silver">Website Rollout</h3>
                <TrendingUp className="w-6 h-6 text-lambda-gold" />
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-awareness-silver/60">Domains Live</span>
                  <span className="text-lambda-gold">7/10</span>
                </div>
                <div className="w-full h-2 bg-consciousness-deep rounded-full">
                  <div className="h-full bg-lambda-gold rounded-full" style={{width: '70%'}}></div>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-4xl mx-auto text-center">
          <Lock className="w-16 h-16 text-lambda-gold mx-auto mb-6" />
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-4 text-awareness-silver">
            Secure <span className="text-lambda-gold">Team Portal</span>
          </h2>
          <p className="text-xl text-awareness-silver/70 mb-8">
            ΛiD authentication required. Internal use only.
          </p>
        </div>
      </section>
    </div>
  )
}

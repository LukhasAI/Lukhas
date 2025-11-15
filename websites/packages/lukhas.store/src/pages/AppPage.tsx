import { GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { Star, Download, Shield, Zap, Brain, CheckCircle } from 'lucide-react'

export default function AppPage() {
  const reviews = [
    { user: 'Sarah K.', rating: 5, text: 'Game-changer for our team workflow', verified: true },
    { user: 'Mike R.', rating: 4, text: 'Great features, easy to use', verified: true },
    { user: 'Alex T.', rating: 5, text: 'Best consciousness app I have used', verified: true },
  ]

  return (
    <div className="min-h-screen bg-consciousness-deep">
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <Link to="/discover" className="text-integration-orange hover:underline mb-4 inline-block">ê Back to Apps</Link>

          <div className="grid md:grid-cols-3 gap-8 mt-8">
            <div className="md:col-span-2">
              <div className="flex items-start gap-6 mb-8">
                <div className="w-24 h-24 rounded-2xl bg-marketplace-gradient flex items-center justify-center">
                  <Brain className="w-12 h-12 text-white" />
                </div>
                <div className="flex-1">
                  <h1 className="text-4xl font-light text-awareness-silver mb-2">ConsciousChat</h1>
                  <p className="text-xl text-awareness-silver/70 mb-4">
                    Conversations that understand context and evolve
                  </p>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <Star className="w-5 h-5 text-lambda-gold fill-lambda-gold" />
                      <span className="text-awareness-silver font-medium">4.8</span>
                      <span className="text-awareness-silver/60">(324 reviews)</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Download className="w-4 h-4 text-integration-orange" />
                      <span className="text-awareness-silver/60">2.4K installs</span>
                    </div>
                  </div>
                </div>
              </div>

              <GlassCard className="p-8 mb-8">
                <h2 className="text-2xl font-light text-awareness-silver mb-4">About this õpp</h2>
                <p className="text-awareness-silver/70 mb-4">
                  ConsciousChat brings consciousness-powered communication to your team. Unlike traditional chat apps,
                  ConsciousChat understands context, adapts to your communication style, and helps facilitate more
                  meaningful conversations.
                </p>
                <p className="text-awareness-silver/70">
                  Built on LUKHAS MATRIZ cognitive engine, every message is processed through ethical guardrails
                  ensuring privacy, security, and respectful communication.
                </p>
              </GlassCard>

              <GlassCard className="p-8 mb-8">
                <h2 className="text-2xl font-light text-awareness-silver mb-6">Key Features</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  {[
                    'Context-aware messaging',
                    'Adaptive communication style',
                    'Ethical AI guardrails',
                    'End-to-end encryption',
                    'Team collaboration',
                    'õiD authentication',
                  ].map((feature, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-0.5" />
                      <span className="text-awareness-silver/80">{feature}</span>
                    </div>
                  ))}
                </div>
              </GlassCard>

              <GlassCard className="p-8">
                <h2 className="text-2xl font-light text-awareness-silver mb-6">User Reviews</h2>
                <div className="space-y-6">
                  {reviews.map((review, index) => (
                    <div key={index} className="border-b border-awareness-silver/10 last:border-0 pb-6 last:pb-0">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-awareness-silver font-medium">{review.user}</span>
                          {review.verified && (
                            <Shield className="w-4 h-4 text-success-green" title="Verified Purchase" />
                          )}
                        </div>
                        <div className="flex items-center gap-1">
                          {[...Array(review.rating)].map((_, i) => (
                            <Star key={i} className="w-4 h-4 text-lambda-gold fill-lambda-gold" />
                          ))}
                        </div>
                      </div>
                      <p className="text-awareness-silver/70">{review.text}</p>
                    </div>
                  ))}
                </div>
              </GlassCard>
            </div>

            <div>
              <GlassCard className="p-6 sticky top-6">
                <div className="text-3xl font-light text-integration-orange mb-2">Free</div>
                <p className="text-awareness-silver/60 text-sm mb-6">With optional premium features</p>

                <button className="w-full py-3 bg-marketplace-gradient text-white rounded-lg font-medium mb-3 hover:shadow-lg transition-all">
                  Try Live Demo
                </button>
                <button className="w-full py-3 bg-white/5 border border-integration-orange/30 text-awareness-silver rounded-lg font-medium hover:bg-white/10 transition-all">
                  Install with õiD
                </button>

                <div className="mt-8 space-y-4">
                  <div>
                    <h3 className="text-awareness-silver font-medium mb-2">Category</h3>
                    <p className="text-integration-orange">Communication</p>
                  </div>
                  <div>
                    <h3 className="text-awareness-silver font-medium mb-2">Developer</h3>
                    <p className="text-awareness-silver/70">LUKHAS Team</p>
                  </div>
                  <div>
                    <h3 className="text-awareness-silver font-medium mb-2">Updated</h3>
                    <p className="text-awareness-silver/70">2 days ago</p>
                  </div>
                  <div>
                    <h3 className="text-awareness-silver font-medium mb-2">Version</h3>
                    <p className="text-awareness-silver/70">2.4.1</p>
                  </div>
                </div>

                <div className="mt-8 pt-6 border-t border-awareness-silver/10">
                  <div className="flex items-center gap-3 text-sm text-awareness-silver/70">
                    <Shield className="w-5 h-5 text-success-green" />
                    <span>Verified by LUKHAS Guardian</span>
                  </div>
                </div>
              </GlassCard>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

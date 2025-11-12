import { GlassCard } from '@lukhas/ui'
import { CheckCircle, AlertTriangle, XCircle, Activity, Globe } from 'lucide-react'

export default function StatusPage() {
  // Mock system status data
  const services = [
    { name: 'API Gateway', status: 'operational', uptime: '99.997%', latency: '19ms' },
    { name: 'Edge Computing', status: 'operational', uptime: '99.995%', latency: '8ms' },
    { name: 'Data Pipelines', status: 'operational', uptime: '99.998%', latency: '12ms' },
    { name: 'Security Layer', status: 'operational', uptime: '100.00%', latency: '5ms' },
    { name: 'Monitoring', status: 'operational', uptime: '99.999%', latency: '3ms' },
    { name: 'Compute', status: 'operational', uptime: '99.996%', latency: '22ms' },
    { name: 'Storage', status: 'operational', uptime: '99.999%', latency: '7ms' },
    { name: 'Authentication', status: 'operational', uptime: '99.998%', latency: '11ms' },
  ]

  const regions = [
    { name: 'US East', status: 'operational', load: '42%' },
    { name: 'US West', status: 'operational', load: '38%' },
    { name: 'EU Central', status: 'operational', load: '51%' },
    { name: 'EU West', status: 'operational', load: '47%' },
    { name: 'Asia Pacific', status: 'operational', load: '55%' },
    { name: 'South America', status: 'operational', load: '29%' },
  ]

  const recentIncidents = [
    {
      date: '2025-11-02',
      title: 'Brief API latency spike in EU Central',
      status: 'Resolved',
      duration: '8 minutes',
      impact: 'Minor'
    },
    {
      date: '2025-10-24',
      title: 'Scheduled maintenance: Edge Computing upgrade',
      status: 'Completed',
      duration: '2 hours',
      impact: 'None'
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational':
        return <CheckCircle className="w-5 h-5 text-success-green" />
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-warning-amber" />
      case 'outage':
        return <XCircle className="w-5 h-5 text-error-red" />
      default:
        return <Activity className="w-5 h-5 text-awareness-silver/50" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational':
        return 'text-success-green'
      case 'degraded':
        return 'text-warning-amber'
      case 'outage':
        return 'text-error-red'
      default:
        return 'text-awareness-silver/50'
    }
  }

  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Hero Section */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-success-green/10 border border-success-green/30 mb-6">
            <CheckCircle className="w-4 h-4 text-success-green" />
            <span className="text-success-green text-sm font-medium">All Systems Operational</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            System <span className="text-infrastructure-green">Status</span>
          </h1>
          <p className="text-xl text-awareness-silver/70 max-w-3xl mx-auto">
            Real-time infrastructure health and performance metrics
          </p>
        </div>
      </section>

      {/* Overall Status */}
      <section className="py-8 px-6">
        <div className="max-w-7xl mx-auto">
          <GlassCard className="p-8">
            <div className="grid md:grid-cols-4 gap-6 text-center">
              <div>
                <div className="text-3xl font-light text-infrastructure-green mb-2">99.997%</div>
                <div className="text-sm text-awareness-silver/60">30-Day Uptime</div>
              </div>
              <div>
                <div className="text-3xl font-light text-infrastructure-green mb-2">19ms</div>
                <div className="text-sm text-awareness-silver/60">Avg Latency</div>
              </div>
              <div>
                <div className="text-3xl font-light text-infrastructure-green mb-2">2.4B+</div>
                <div className="text-sm text-awareness-silver/60">Requests/Day</div>
              </div>
              <div>
                <div className="text-3xl font-light text-success-green mb-2">0</div>
                <div className="text-sm text-awareness-silver/60">Active Incidents</div>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Services Status */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-8 text-awareness-silver">
            Core <span className="text-infrastructure-green">Services</span>
          </h2>
          <GlassCard className="p-1">
            <div className="space-y-1">
              {services.map((service, index) => (
                <div
                  key={index}
                  className="p-6 hover:bg-white/5 transition-all rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      {getStatusIcon(service.status)}
                      <div className="flex-1">
                        <h3 className="text-lg font-light text-awareness-silver">{service.name}</h3>
                        <p className={`text-sm capitalize ${getStatusColor(service.status)}`}>
                          {service.status}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-8 text-sm text-awareness-silver/70">
                      <div className="text-right">
                        <div className="text-awareness-silver/50 text-xs mb-1">Uptime</div>
                        <div className="text-infrastructure-green">{service.uptime}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-awareness-silver/50 text-xs mb-1">Latency</div>
                        <div className="text-code-cyan">{service.latency}</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Regional Status */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-8 text-awareness-silver">
            Global <span className="text-infrastructure-green">Regions</span>
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {regions.map((region, index) => (
              <GlassCard key={index} className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Globe className="w-6 h-6 text-code-cyan" />
                    <h3 className="text-lg font-light text-awareness-silver">{region.name}</h3>
                  </div>
                  {getStatusIcon(region.status)}
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-awareness-silver/60">Status</span>
                    <span className={`capitalize ${getStatusColor(region.status)}`}>
                      {region.status}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-awareness-silver/60">Load</span>
                    <span className="text-awareness-silver">{region.load}</span>
                  </div>
                  <div className="mt-3">
                    <div className="w-full h-2 bg-consciousness-deep rounded-full overflow-hidden">
                      <div
                        className="h-full bg-infrastructure-gradient rounded-full"
                        style={{ width: region.load }}
                      ></div>
                    </div>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* Recent Incidents */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-8 text-awareness-silver">
            Recent <span className="text-infrastructure-green">Incidents</span>
          </h2>
          <GlassCard className="p-8">
            <div className="space-y-6">
              {recentIncidents.map((incident, index) => (
                <div
                  key={index}
                  className="pb-6 border-b border-awareness-silver/10 last:border-0 last:pb-0"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-awareness-silver/50 text-sm">{incident.date}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          incident.status === 'Resolved' || incident.status === 'Completed'
                            ? 'bg-success-green/20 text-success-green'
                            : 'bg-warning-amber/20 text-warning-amber'
                        }`}>
                          {incident.status}
                        </span>
                      </div>
                      <h3 className="text-lg text-awareness-silver mb-2">{incident.title}</h3>
                      <div className="flex gap-6 text-sm text-awareness-silver/60">
                        <div>Duration: {incident.duration}</div>
                        <div>Impact: {incident.impact}</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </section>

      {/* SLA Information */}
      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <GlassCard className="p-12 text-center">
            <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-4 text-awareness-silver">
              99.99% Uptime <span className="text-infrastructure-green">Guarantee</span>
            </h2>
            <p className="text-lg text-awareness-silver/70 mb-8">
              Enterprise SLA with financial compensation for downtime
            </p>
            <div className="grid md:grid-cols-3 gap-8 text-left">
              <div>
                <h3 className="text-infrastructure-green font-medium mb-2">Incident Response</h3>
                <p className="text-awareness-silver/70 text-sm">
                  Sub-15 minute awareness, sub-1 hour mitigation for critical issues
                </p>
              </div>
              <div>
                <h3 className="text-infrastructure-green font-medium mb-2">Transparency</h3>
                <p className="text-awareness-silver/70 text-sm">
                  Real-time status updates, post-incident reviews, full transparency
                </p>
              </div>
              <div>
                <h3 className="text-infrastructure-green font-medium mb-2">Compensation</h3>
                <p className="text-awareness-silver/70 text-sm">
                  Service credits for SLA breaches, no questions asked
                </p>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Subscribe to Updates */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-6 text-awareness-silver">
            Stay informed about infrastructure status
          </h2>
          <p className="text-xl text-awareness-silver/70 mb-8">
            Subscribe to get real-time alerts about incidents and maintenance
          </p>
          <div className="flex gap-4 max-w-md mx-auto">
            <input
              type="email"
              placeholder="your@email.com"
              className="flex-1 px-4 py-3 bg-consciousness-deep/50 border border-infrastructure-green/30 rounded-lg
                       text-awareness-silver placeholder-awareness-silver/40
                       focus:outline-none focus:ring-2 focus:ring-infrastructure-green focus:border-transparent"
            />
            <button className="px-6 py-3 bg-infrastructure-gradient text-white rounded-lg font-medium hover:shadow-lg hover:shadow-infrastructure-green/20 transition-all">
              Subscribe
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}

import { GlassCard } from '@lukhas/ui'
import { Shield, CheckCircle, Lock, FileText, Globe, AlertTriangle, Download } from 'lucide-react'

export default function CompliancePage() {
  const certifications = [
    {
      name: 'SOC 2 Type II',
      status: 'Certified',
      updated: '2025-09-15',
      description: 'Independent audit validates security controls, operational procedures, and data protection practices',
      icon: Shield,
      color: 'text-success-green',
      details: [
        'Annual independent audit by certified CPA firm',
        'Security, availability, confidentiality controls',
        'Continuous monitoring and quarterly reviews',
        'Full audit report available to enterprise customers',
      ],
    },
    {
      name: 'HIPAA Ready',
      status: 'Compliant',
      updated: '2025-10-01',
      description: 'Business associate agreements, encrypted storage, and audit trails for healthcare applications',
      icon: Lock,
      color: 'text-trust-blue',
      details: [
        'Business Associate Agreement (BAA) available',
        'Encrypted PHI storage at rest and in transit',
        'Comprehensive audit logging (6-year retention)',
        'Access controls with role-based permissions',
      ],
    },
    {
      name: 'GDPR Compliant',
      status: 'Compliant',
      updated: '2025-11-01',
      description: 'Data processing addendums, consent management, and right-to-deletion implementation',
      icon: Globe,
      color: 'text-enterprise-pink',
      details: [
        'Data Processing Agreement (DPA) for EU customers',
        'Regional data residency guarantees (EU zone)',
        'Right to access, rectification, and deletion (automated)',
        'Privacy-by-design architecture with minimal data collection',
      ],
    },
    {
      name: 'FedRAMP',
      status: 'In Progress',
      updated: 'Q2 2026 Target',
      description: 'Security controls meeting federal requirements for government deployments',
      icon: FileText,
      color: 'text-warning-amber',
      details: [
        'Moderate Impact baseline implementation',
        'Continuous monitoring system deployed',
        'Federal security documentation in review',
        'Expected authorization: Q2 2026',
      ],
    },
  ]

  const securityFeatures = [
    {
      title: 'Data Encryption',
      icon: Lock,
      items: [
        'AES-256 encryption at rest',
        'TLS 1.3 for data in transit',
        'Encrypted database backups',
        'Hardware security modules (HSM) for key management',
      ],
    },
    {
      title: 'Access Controls',
      icon: Shield,
      items: [
        'Multi-factor authentication (MFA) required',
        'Role-based access control (RBAC)',
        'Principle of least privilege enforcement',
        'Session timeout and automatic logout',
      ],
    },
    {
      title: 'Audit & Monitoring',
      icon: FileText,
      items: [
        'Comprehensive activity logging',
        'Real-time security monitoring',
        'Automated threat detection',
        'Quarterly security audits',
      ],
    },
    {
      title: 'Data Residency',
      icon: Globe,
      items: [
        'Regional deployment zones (EU, US, APAC)',
        'Data never leaves selected region',
        'Compliance with local data sovereignty laws',
        'Transparent data location tracking',
      ],
    },
  ]

  const privacyPractices = [
    {
      principle: 'Privacy by Design',
      description: 'Privacy embedded in system architecture from inception, not added as afterthought',
    },
    {
      principle: 'Data Minimization',
      description: 'Collect only essential data required for service operation. No unnecessary PII storage',
    },
    {
      principle: 'Transparent Processing',
      description: 'Clear documentation of what data is collected, how it\'s used, and who has access',
    },
    {
      principle: 'User Rights Enforcement',
      description: 'Automated implementation of access, rectification, deletion, and portability rights',
    },
  ]

  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Hero Section */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-success-green/10 border border-success-green/30 mb-6">
            <Shield className="w-4 h-4 text-success-green" />
            <span className="text-success-green text-sm font-medium">SOC 2 Type II Certified</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Security & <span className="text-enterprise-pink">Compliance</span>
          </h1>
          <p className="text-xl text-awareness-silver/70 max-w-3xl mx-auto">
            Enterprise-grade security with certifications that meet the most stringent regulatory requirements.
            Built for healthcare, finance, government, and regulated industries.
          </p>
        </div>
      </section>

      {/* Certifications Overview */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-8 text-awareness-silver text-center">
            Compliance <span className="text-enterprise-pink">Certifications</span>
          </h2>

          <div className="grid md:grid-cols-2 gap-8">
            {certifications.map((cert, index) => {
              const Icon = cert.icon
              return (
                <GlassCard key={index} className="p-8">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <Icon className={`w-12 h-12 ${cert.color}`} />
                      <div>
                        <h3 className="text-2xl font-light text-awareness-silver mb-1">{cert.name}</h3>
                        <div className="flex items-center gap-2">
                          <span className={`text-sm px-2 py-1 rounded ${
                            cert.status === 'In Progress'
                              ? 'bg-warning-amber/20 text-warning-amber'
                              : 'bg-success-green/20 text-success-green'
                          }`}>
                            {cert.status}
                          </span>
                          <span className="text-xs text-awareness-silver/50">Updated: {cert.updated}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <p className="text-awareness-silver/70 mb-6">
                    {cert.description}
                  </p>

                  <ul className="space-y-2">
                    {cert.details.map((detail, detailIndex) => (
                      <li key={detailIndex} className="flex items-start gap-3 text-sm">
                        <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                        <span className="text-awareness-silver/70">{detail}</span>
                      </li>
                    ))}
                  </ul>

                  {cert.status !== 'In Progress' && (
                    <button className="mt-6 flex items-center gap-2 text-enterprise-pink text-sm font-medium hover:underline">
                      <Download className="w-4 h-4" />
                      Download {cert.name} Report
                    </button>
                  )}
                </GlassCard>
              )
            })}
          </div>
        </div>
      </section>

      {/* Security Features */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Security <span className="text-enterprise-pink">Infrastructure</span>
            </h2>
            <p className="text-xl text-awareness-silver/70 max-w-3xl mx-auto">
              Multi-layered security architecture protecting your data at every level
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {securityFeatures.map((feature, index) => {
              const Icon = feature.icon
              return (
                <GlassCard key={index} className="p-6">
                  <Icon className="w-10 h-10 text-enterprise-pink mb-4" />
                  <h3 className="text-lg font-light text-awareness-silver mb-4">
                    {feature.title}
                  </h3>
                  <ul className="space-y-2">
                    {feature.items.map((item, itemIndex) => (
                      <li key={itemIndex} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="w-3 h-3 text-success-green flex-shrink-0 mt-1" />
                        <span className="text-awareness-silver/70">{item}</span>
                      </li>
                    ))}
                  </ul>
                </GlassCard>
              )
            })}
          </div>
        </div>
      </section>

      {/* Privacy Practices */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Privacy <span className="text-enterprise-pink">Principles</span>
            </h2>
            <p className="text-xl text-awareness-silver/70 max-w-3xl mx-auto">
              Privacy-first architecture guided by transparent principles
            </p>
          </div>

          <div className="space-y-6">
            {privacyPractices.map((practice, index) => (
              <GlassCard key={index} className="p-6">
                <div className="flex items-start gap-4">
                  <CheckCircle className="w-6 h-6 text-enterprise-pink flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl text-awareness-silver mb-2">{practice.principle}</h3>
                    <p className="text-awareness-silver/70">{practice.description}</p>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* Data Processing Agreements */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-12 text-awareness-silver text-center">
            Legal <span className="text-enterprise-pink">Agreements</span>
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            <GlassCard className="p-8 text-center">
              <FileText className="w-12 h-12 text-enterprise-pink mx-auto mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">
                Data Processing Agreement
              </h3>
              <p className="text-awareness-silver/70 text-sm mb-6">
                GDPR-compliant DPA for EU customers. Defines data processing responsibilities and obligations.
              </p>
              <button className="px-6 py-2 bg-white/5 backdrop-blur-sm border border-enterprise-pink/30 text-awareness-silver rounded-lg text-sm font-medium hover:bg-white/10 transition-all">
                Download DPA
              </button>
            </GlassCard>

            <GlassCard className="p-8 text-center">
              <Lock className="w-12 h-12 text-trust-blue mx-auto mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">
                Business Associate Agreement
              </h3>
              <p className="text-awareness-silver/70 text-sm mb-6">
                HIPAA-compliant BAA for healthcare organizations. Required for PHI processing.
              </p>
              <button className="px-6 py-2 bg-white/5 backdrop-blur-sm border border-trust-blue/30 text-awareness-silver rounded-lg text-sm font-medium hover:bg-white/10 transition-all">
                Download BAA
              </button>
            </GlassCard>

            <GlassCard className="p-8 text-center">
              <Shield className="w-12 h-12 text-success-green mx-auto mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">
                Service Level Agreement
              </h3>
              <p className="text-awareness-silver/70 text-sm mb-6">
                99.99% uptime guarantee with financial compensation for breaches.
              </p>
              <button className="px-6 py-2 bg-white/5 backdrop-blur-sm border border-success-green/30 text-awareness-silver rounded-lg text-sm font-medium hover:bg-white/10 transition-all">
                Download SLA
              </button>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Regional Compliance */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-12 text-awareness-silver text-center">
            Regional <span className="text-enterprise-pink">Compliance</span>
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <GlassCard className="p-8">
              <div className="flex items-center gap-3 mb-4">
                <Globe className="w-8 h-8 text-enterprise-pink" />
                <h3 className="text-xl font-light text-awareness-silver">European Union</h3>
              </div>
              <ul className="space-y-2 text-awareness-silver/70 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>GDPR compliant with DPA</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>Data residency in EU regions</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>Standard Contractual Clauses (SCCs)</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>Privacy Shield successor compliance</span>
                </li>
              </ul>
            </GlassCard>

            <GlassCard className="p-8">
              <div className="flex items-center gap-3 mb-4">
                <Globe className="w-8 h-8 text-trust-blue" />
                <h3 className="text-xl font-light text-awareness-silver">United States</h3>
              </div>
              <ul className="space-y-2 text-awareness-silver/70 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>HIPAA compliant with BAA</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>CCPA/CPRA consumer rights</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>SOC 2 Type II certified</span>
                </li>
                <li className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-warning-amber flex-shrink-0 mt-0.5" />
                  <span>FedRAMP in progress (Q2 2026)</span>
                </li>
              </ul>
            </GlassCard>

            <GlassCard className="p-8">
              <div className="flex items-center gap-3 mb-4">
                <Globe className="w-8 h-8 text-lambda-gold" />
                <h3 className="text-xl font-light text-awareness-silver">Asia Pacific</h3>
              </div>
              <ul className="space-y-2 text-awareness-silver/70 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>Data residency in APAC regions</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>Singapore PDPA compliance</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>Australia Privacy Act alignment</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-success-green flex-shrink-0 mt-0.5" />
                  <span>Japan APPI considerations</span>
                </li>
              </ul>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Incident Response */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-5xl mx-auto">
          <GlassCard className="p-12">
            <div className="text-center mb-8">
              <AlertTriangle className="w-16 h-16 text-enterprise-pink mx-auto mb-6" />
              <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-4 text-awareness-silver">
                Incident <span className="text-enterprise-pink">Response</span>
              </h2>
              <p className="text-lg text-awareness-silver/70">
                24/7 security operations with documented incident response procedures
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="text-3xl font-light text-enterprise-pink mb-2">&lt;15 min</div>
                <div className="text-sm text-awareness-silver/60">Incident Detection</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-light text-enterprise-pink mb-2">&lt;1 hour</div>
                <div className="text-sm text-awareness-silver/60">Critical Mitigation</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-light text-enterprise-pink mb-2">24/7/365</div>
                <div className="text-sm text-awareness-silver/60">Security Operations</div>
              </div>
            </div>

            <div className="bg-consciousness-deep/50 rounded-lg p-6">
              <h3 className="text-lg font-light text-awareness-silver mb-4">
                Response Process
              </h3>
              <ul className="space-y-3 text-awareness-silver/70 text-sm">
                <li className="flex items-start gap-3">
                  <span className="text-enterprise-pink font-medium">1.</span>
                  <span>Automated detection and immediate escalation to security team</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-enterprise-pink font-medium">2.</span>
                  <span>Impact assessment and affected customer notification within 1 hour</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-enterprise-pink font-medium">3.</span>
                  <span>Containment and mitigation with real-time status updates</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-enterprise-pink font-medium">4.</span>
                  <span>Post-incident review and public transparency report within 72 hours</span>
                </li>
              </ul>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-6 text-awareness-silver">
            Questions about compliance?
          </h2>
          <p className="text-xl text-awareness-silver/70 mb-8">
            Our security team is available to discuss your compliance requirements
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="px-8 py-4 bg-enterprise-gradient text-white rounded-lg font-medium hover:shadow-lg hover:shadow-enterprise-pink/20 transition-all">
              Contact Security Team
            </button>
            <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-enterprise-pink/30 text-awareness-silver rounded-lg font-medium hover:bg-white/10 transition-all">
              Download Compliance Pack
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}

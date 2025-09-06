/**
 * Domain Configurations for LUKHΛS λWecosystem
 * 
 * Each of the 11 domains has unique consciousness properties,
 * visual themes, and behavioral patterns that create specialized
 * experiences while maintaining unified brand identity.
 */

interface DomainConfig {
  theme: string
  particles: string
  navigation: string
  tone: {
    poetic: number    // 0-100%
    technical: number // 0-100%
    plain: number     // 0-100%
  }
  primaryColor: string
  particleBehavior: string
  userRole: string
  description: string
}

export const domainConfigs: Record<string, DomainConfig> = {
  // Main AI Platform - Central consciousness hub
  'lukhas.ai': {
    theme: 'consciousness',
    particles: 'neural',
    navigation: 'constellation',
    tone: { poetic: 30, technical: 40, plain: 30 },
    primaryColor: '#00D4FF',
    particleBehavior: 'emergence_patterns',
    userRole: 'consciousness_explorer',
    description: 'Central hub for LUKHΛS AI consciousness platform'
  },

  // Identity & Authentication - Secure digital identity
  'lukhas.id': {
    theme: 'identity',
    particles: 'biometric',
    navigation: 'secure',
    tone: { poetic: 20, technical: 40, plain: 40 },
    primaryColor: '#7C3AED',
    particleBehavior: 'signature_verification',
    userRole: 'identity_sovereign',
    description: 'Quantum-secure digital identity and consciousness verification'
  },

  // Team Collaboration - Collective consciousness
  'lukhas.team': {
    theme: 'collaboration',
    particles: 'swarm',
    navigation: 'workspace',
    tone: { poetic: 15, technical: 25, plain: 60 },
    primaryColor: '#10B981',
    particleBehavior: 'collective_intelligence',
    userRole: 'team_collaborator',
    description: 'Collective consciousness workspace for team collaboration'
  },

  // Developer Platform - Builder tools
  'lukhas.dev': {
    theme: 'builder',
    particles: 'code_fragments',
    navigation: 'technical',
    tone: { poetic: 15, technical: 60, plain: 25 },
    primaryColor: '#3B82F6',
    particleBehavior: 'code_crystallization',
    userRole: 'consciousness_builder',
    description: 'Developer platform for consciousness-aware applications'
  },

  // API Infrastructure - Data conduits
  'lukhas.io': {
    theme: 'conduit',
    particles: 'data_streams',
    navigation: 'api_focused',
    tone: { poetic: 10, technical: 70, plain: 20 },
    primaryColor: '#EF4444',
    particleBehavior: 'data_flow_visualization',
    userRole: 'api_integrator',
    description: 'API gateway and infrastructure for consciousness-scale applications'
  },

  // App Marketplace - Digital marketplace
  'lukhas.store': {
    theme: 'marketplace',
    particles: 'app_spheres',
    navigation: 'commercial',
    tone: { poetic: 25, technical: 25, plain: 50 },
    primaryColor: '#F59E0B',
    particleBehavior: 'marketplace_attraction',
    userRole: 'app_consumer',
    description: 'Marketplace for consciousness-powered applications and agents'
  },

  // Cloud Services - Managed infrastructure
  'lukhas.cloud': {
    theme: 'infrastructure',
    particles: 'cloud_nodes',
    navigation: 'enterprise',
    tone: { poetic: 15, technical: 60, plain: 25 },
    primaryColor: '#8B5CF6',
    particleBehavior: 'distributed_scaling',
    userRole: 'infrastructure_manager',
    description: 'Managed cloud infrastructure for consciousness applications'
  },

  // European Operations - GDPR-compliant
  'lukhas.eu': {
    theme: 'regional_privacy',
    particles: 'privacy_shields',
    navigation: 'compliance_focused',
    tone: { poetic: 20, technical: 35, plain: 45 },
    primaryColor: '#0C4A8B',
    particleBehavior: 'privacy_protection',
    userRole: 'eu_citizen',
    description: 'GDPR-compliant European operations with local data residency'
  },

  // US Operations - Enterprise-focused
  'lukhas.us': {
    theme: 'regional_enterprise',
    particles: 'enterprise_grid',
    navigation: 'business_focused',
    tone: { poetic: 20, technical: 40, plain: 40 },
    primaryColor: '#DC2626',
    particleBehavior: 'enterprise_coordination',
    userRole: 'us_enterprise',
    description: 'US enterprise operations with SOC2 compliance'
  },

  // Experimental Labs - Cutting edge research
  'lukhas.xyz': {
    theme: 'experimental',
    particles: 'quantum_chaos',
    navigation: 'exploratory',
    tone: { poetic: 40, technical: 40, plain: 20 },
    primaryColor: '#EC4899',
    particleBehavior: 'experimental_emergence',
    userRole: 'consciousness_researcher',
    description: 'Experimental consciousness research and prototype demonstrations'
  },

  // Corporate/Enterprise - Business-focused
  'lukhas.com': {
    theme: 'enterprise',
    particles: 'corporate_formation',
    navigation: 'executive',
    tone: { poetic: 10, technical: 30, plain: 60 },
    primaryColor: '#1F2937',
    particleBehavior: 'executive_summary',
    userRole: 'enterprise_decision_maker',
    description: 'Enterprise solutions and corporate consciousness integration'
  }
}

// Domain relationships for quantum entanglement calculations
export const domainRelationships = new Map([
  ['lukhas.ai-lukhas.dev', 0.8],      // High correlation - main platform + dev tools
  ['lukhas.ai-lukhas.id', 0.9],       // Very high correlation - platform needs identity
  ['lukhas.id-lukhas.team', 0.7],     // Identity needed for team collaboration
  ['lukhas.dev-lukhas.io', 0.8],      // Developers use APIs extensively
  ['lukhas.store-lukhas.cloud', 0.6], // Apps need hosting infrastructure
  ['lukhas.cloud-lukhas.io', 0.7],    // Cloud infrastructure serves APIs
  ['lukhas.eu-lukhas.com', 0.5],      // Regional + enterprise correlation
  ['lukhas.us-lukhas.com', 0.5],      // Regional + enterprise correlation
  ['lukhas.xyz-lukhas.ai', 0.4],      // Experimental connects to main platform
  ['lukhas.team-lukhas.store', 0.3],  // Teams might use marketplace apps
  ['lukhas.dev-lukhas.store', 0.6],   // Developers create and consume apps
])

// Route mappings for domain-to-directory structure
export const domainRouteMap: Record<string, string> = {
  'lukhas.ai': 'ai',
  'lukhas.id': 'id', 
  'lukhas.team': 'team',
  'lukhas.dev': 'dev',
  'lukhas.io': 'io',
  'lukhas.store': 'store',
  'lukhas.cloud': 'cloud',
  'lukhas.eu': 'eu',
  'lukhas.us': 'us',
  'lukhas.xyz': 'xyz',
  'lukhas.com': 'com'
}

// Domain priorities for conflict resolution
export const domainPriorities = new Map([
  ['lukhas.ai', 1],     // Highest priority - main platform
  ['lukhas.id', 2],     // Second priority - identity is critical
  ['lukhas.team', 3],   // Team collaboration
  ['lukhas.dev', 4],    // Developer platform
  ['lukhas.io', 5],     // API infrastructure
  ['lukhas.store', 6],  // Marketplace
  ['lukhas.cloud', 7],  // Cloud services
  ['lukhas.eu', 8],     // Regional domains
  ['lukhas.us', 9],
  ['lukhas.xyz', 10],   // Experimental
  ['lukhas.com', 11]    // Corporate (lowest priority)
])

// Domain consciousness weights for quantum calculations
export const domainWeights = new Map([
  ['lukhas.ai', 0.25],     // 25% of total consciousness
  ['lukhas.id', 0.15],     // 15% - identity layer
  ['lukhas.dev', 0.12],    // 12% - developer focus
  ['lukhas.team', 0.10],   // 10% - collaboration
  ['lukhas.io', 0.10],     // 10% - API infrastructure  
  ['lukhas.store', 0.08],  // 8% - marketplace
  ['lukhas.cloud', 0.08],  // 8% - cloud services
  ['lukhas.eu', 0.04],     // 4% - regional EU
  ['lukhas.us', 0.04],     // 4% - regional US
  ['lukhas.xyz', 0.03],    // 3% - experimental
  ['lukhas.com', 0.01]     // 1% - corporate
])

export default domainConfigs
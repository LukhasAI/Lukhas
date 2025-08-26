/**
 * LUKHAS AI Plan Labels - Bilingual (EN/ES)
 *
 * User-facing labels for OpenAI-style plans in English and Spanish
 * Follows LUKHAS AI brand guidelines and tone system
 */

import type { Plan } from './plans';

/**
 * English plan labels
 */
export const PLAN_LABELS_EN: Record<Plan, {
  name: string;
  tagline: string;
  description: string;
  cta: string; // Call to action button text
}> = {
  free: {
    name: 'Free',
    tagline: 'Explore consciousness',
    description: 'Perfect for individuals discovering LUKHAS AI capabilities',
    cta: 'Start free'
  },
  plus: {
    name: 'Plus',
    tagline: 'Enhance your potential',
    description: 'For creators building with quantum-inspired AI',
    cta: 'Upgrade to Plus'
  },
  team: {
    name: 'Team',
    tagline: 'Collaborate with intelligence',
    description: 'For teams orchestrating AI-powered projects together',
    cta: 'Start team trial'
  },
  enterprise: {
    name: 'Enterprise',
    tagline: 'Scale consciousness',
    description: 'For organizations requiring enterprise-grade AI infrastructure',
    cta: 'Contact sales'
  },
  core: {
    name: 'Core Team (Internal)',
    tagline: 'Architect the future',
    description: 'Internal LUKHAS team with full system access',
    cta: 'Internal access'
  }
};

/**
 * Spanish plan labels
 */
export const PLAN_LABELS_ES: Record<Plan, {
  name: string;
  tagline: string;
  description: string;
  cta: string;
}> = {
  free: {
    name: 'Gratis',
    tagline: 'Explora la consciencia',
    description: 'Perfecto para individuos descubriendo las capacidades de LUKHAS AI',
    cta: 'Comenzar gratis'
  },
  plus: {
    name: 'Plus',
    tagline: 'Potencia tu creatividad',
    description: 'Para creadores construyendo con IA cuántica-inspirada',
    cta: 'Actualizar a Plus'
  },
  team: {
    name: 'Equipo',
    tagline: 'Colabora con inteligencia',
    description: 'Para equipos orquestando proyectos potenciados por IA',
    cta: 'Prueba para equipos'
  },
  enterprise: {
    name: 'Empresarial',
    tagline: 'Escala la consciencia',
    description: 'Para organizaciones que requieren infraestructura de IA empresarial',
    cta: 'Contactar ventas'
  },
  core: {
    name: 'Equipo Interno',
    tagline: 'Arquitecta el futuro',
    description: 'Equipo interno de LUKHAS con acceso completo al sistema',
    cta: 'Acceso interno'
  }
};

/**
 * Feature labels for plan comparison (English)
 */
export const FEATURE_LABELS_EN = {
  // Core features
  matrizAccess: 'MΛTRIZ Access',
  consciousnessEngine: 'Consciousness Engine',
  dreamStates: 'Dream States',
  quantumInspired: 'Quantum-Inspired Processing',
  bioInspired: 'Bio-Inspired Adaptation',
  guardianSystem: 'Guardian Ethics System',

  // Authentication & Security
  sso: 'Single Sign-On (SSO)',
  scim: 'SCIM User Provisioning',
  rbac: 'Role-Based Access Control',
  passkeys: 'Passkey Authentication',
  magicLinks: 'Magic Link Login',
  backupCodes: 'Backup Recovery Codes',

  // API & Integration
  apiAccess: 'API Access',
  adminApi: 'Admin API',
  webhooks: 'Webhooks',
  customIntegrations: 'Custom Integrations',

  // Analytics & Monitoring
  analytics: 'Analytics Dashboard',
  auditLogs: 'Audit Logs',
  complianceReports: 'Compliance Reports',

  // Limits & Quotas
  rateLimit: 'API Rate Limit',
  storage: 'Storage',
  teamMembers: 'Team Members',
  concurrentSessions: 'Concurrent Sessions',

  // Support
  communitySupport: 'Community Support',
  prioritySupport: 'Priority Support',
  dedicatedSupport: 'Dedicated Support',
  sla: 'SLA Guarantee'
};

/**
 * Feature labels for plan comparison (Spanish)
 */
export const FEATURE_LABELS_ES = {
  // Core features
  matrizAccess: 'Acceso a MΛTRIZ',
  consciousnessEngine: 'Motor de Consciencia',
  dreamStates: 'Estados de Sueño',
  quantumInspired: 'Procesamiento Cuántico-Inspirado',
  bioInspired: 'Adaptación Bio-Inspirada',
  guardianSystem: 'Sistema Guardián de Ética',

  // Authentication & Security
  sso: 'Inicio de Sesión Único (SSO)',
  scim: 'Aprovisionamiento SCIM',
  rbac: 'Control de Acceso por Roles',
  passkeys: 'Autenticación con Passkey',
  magicLinks: 'Enlace Mágico',
  backupCodes: 'Códigos de Respaldo',

  // API & Integration
  apiAccess: 'Acceso API',
  adminApi: 'API de Administración',
  webhooks: 'Webhooks',
  customIntegrations: 'Integraciones Personalizadas',

  // Analytics & Monitoring
  analytics: 'Panel de Análisis',
  auditLogs: 'Registros de Auditoría',
  complianceReports: 'Informes de Cumplimiento',

  // Limits & Quotas
  rateLimit: 'Límite de Tasa API',
  storage: 'Almacenamiento',
  teamMembers: 'Miembros del Equipo',
  concurrentSessions: 'Sesiones Concurrentes',

  // Support
  communitySupport: 'Soporte Comunitario',
  prioritySupport: 'Soporte Prioritario',
  dedicatedSupport: 'Soporte Dedicado',
  sla: 'Garantía SLA'
};

/**
 * Pricing labels (bilingual)
 */
export const PRICING_LABELS = {
  en: {
    monthly: 'per month',
    yearly: 'per year',
    perSeat: 'per seat',
    save: 'Save',
    freeTrial: 'free trial',
    days: 'days',
    customPricing: 'Custom pricing',
    contactSales: 'Contact sales',
    currentPlan: 'Current plan',
    recommended: 'Recommended'
  },
  es: {
    monthly: 'por mes',
    yearly: 'por año',
    perSeat: 'por usuario',
    save: 'Ahorra',
    freeTrial: 'prueba gratis',
    days: 'días',
    customPricing: 'Precio personalizado',
    contactSales: 'Contactar ventas',
    currentPlan: 'Plan actual',
    recommended: 'Recomendado'
  }
};

/**
 * Tier upgrade prompts (bilingual)
 */
export const UPGRADE_PROMPTS = {
  en: {
    rateLimit: 'You've reached your rate limit. Upgrade for higher limits.',
    storage: 'Storage quota exceeded. Upgrade for more space.',
    teamSize: 'Team member limit reached. Upgrade to add more members.',
    feature: 'This feature requires {plan} plan or higher.',
    sso: 'SSO is available starting with Team plan.',
    scim: 'SCIM provisioning requires Enterprise plan.',
    api: 'Advanced API features require Plus plan or higher.'
  },
  es: {
    rateLimit: 'Has alcanzado tu límite de tasa. Actualiza para límites más altos.',
    storage: 'Cuota de almacenamiento excedida. Actualiza para más espacio.',
    teamSize: 'Límite de miembros alcanzado. Actualiza para añadir más.',
    feature: 'Esta función requiere el plan {plan} o superior.',
    sso: 'SSO está disponible a partir del plan Equipo.',
    scim: 'El aprovisionamiento SCIM requiere plan Empresarial.',
    api: 'Las funciones API avanzadas requieren plan Plus o superior.'
  }
};

/**
 * Helper function to get plan label in specified language
 */
export function getPlanLabel(plan: Plan, lang: 'en' | 'es' = 'en') {
  const labels = lang === 'es' ? PLAN_LABELS_ES : PLAN_LABELS_EN;
  return labels[plan];
}

/**
 * Helper function to get feature label in specified language
 */
export function getFeatureLabel(feature: keyof typeof FEATURE_LABELS_EN, lang: 'en' | 'es' = 'en') {
  const labels = lang === 'es' ? FEATURE_LABELS_ES : FEATURE_LABELS_EN;
  return labels[feature];
}

/**
 * Format pricing with localization
 */
export function formatPricing(amount: number, period: 'monthly' | 'yearly', lang: 'en' | 'es' = 'en'): string {
  const currency = lang === 'es' ? '€' : '$';
  const labels = PRICING_LABELS[lang];
  const periodLabel = period === 'monthly' ? labels.monthly : labels.yearly;

  if (amount === 0) {
    return lang === 'es' ? 'Gratis' : 'Free';
  }

  return `${currency}${amount} ${periodLabel}`;
}

export default {
  PLAN_LABELS_EN,
  PLAN_LABELS_ES,
  FEATURE_LABELS_EN,
  FEATURE_LABELS_ES,
  PRICING_LABELS,
  UPGRADE_PROMPTS,
  getPlanLabel,
  getFeatureLabel,
  formatPricing
};

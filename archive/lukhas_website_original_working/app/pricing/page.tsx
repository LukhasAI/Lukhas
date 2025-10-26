'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ChevronLeftIcon,
  LanguageIcon,
  CheckIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/TransparencyBox'
import { TierGrid, TIER_CONTENT_EN, TIER_CONTENT_ES } from '@/components/TierCard'
import { PLAN_PRICING, PLAN_FEATURES, RATE_ENVELOPES } from '@/packages/auth/plans'
import { getPlanLabel, formatPricing, PRICING_LABELS } from '@/packages/auth/plan-labels'

export default function PricingPage() {
  const router = useRouter()
  const [locale, setLocale] = useState<'en' | 'es'>('en')
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly')

  // Use locale-specific content
  const tierContent = locale === 'es' ? TIER_CONTENT_ES : TIER_CONTENT_EN
  const pricingLabels = PRICING_LABELS[locale]

  // Page title and description based on locale
  const pageContent = {
    en: {
      title: 'Plans & Pricing',
      subtitle: 'Choose the right plan for your consciousness journey',
      backToLukhas: 'Back to LUKHAS AI',
      billingToggle: {
        monthly: 'Monthly',
        yearly: 'Yearly'
      },
      saveLabel: 'Save 2 months',
      currentPlan: 'Current plan',
      choosePlan: 'Choose plan',
      contactSales: 'Contact sales',
      features: 'All plans include:',
      coreFeatures: [
        'Quantum-inspired processing',
        'Bio-inspired adaptation',
        'Guardian ethics system',
        'MΛTRIZ access'
      ]
    },
    es: {
      title: 'Planes y Precios',
      subtitle: 'Elige el plan adecuado para tu viaje de consciencia',
      backToLukhas: 'Volver a LUKHAS AI',
      billingToggle: {
        monthly: 'Mensual',
        yearly: 'Anual'
      },
      saveLabel: 'Ahorra 2 meses',
      currentPlan: 'Plan actual',
      choosePlan: 'Elegir plan',
      contactSales: 'Contactar ventas',
      features: 'Todos los planes incluyen:',
      coreFeatures: [
        'Procesamiento cuántico-inspirado',
        'Adaptación bio-inspirada',
        'Sistema guardián de ética',
        'Acceso a MΛTRIZ'
      ]
    }
  }

  const t = pageContent[locale]

  // JSON-LD structured data for pricing page
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "LUKHAS AI Pricing",
    "description": "Flexible pricing plans for LUKHAS AI consciousness platform",
    "provider": {
      "@type": "Organization",
      "name": "LUKHAS AI",
      "description": "Advanced AI platform with quantum-inspired consciousness and bio-inspired adaptation"
    },
    "offers": tierContent.map(tier => ({
      "@type": "Offer",
      "name": tier.title,
      "description": tier.plain,
      "price": tier.id === 'T1' ? "0" : "Contact for pricing",
      "priceCurrency": "USD"
    }))
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <div className="min-h-screen bg-bg-primary">
        {/* Skip to main content link for accessibility */}
        <a 
          href="#main-content" 
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-trinity-identity text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-white z-50"
        >
          Skip to main content
        </a>
        
        {/* Header */}
        <header className="flex items-center justify-between p-6" role="banner">
          <Link 
            href="/" 
            className="flex items-center text-white/80 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded"
          >
            <ChevronLeftIcon className="w-5 h-5 mr-2" aria-hidden="true" />
            {t.backToLukhas}
          </Link>
          
          <div className="flex items-center gap-4">
            {/* Language selector */}
            <button
              onClick={() => setLocale(locale === 'en' ? 'es' : 'en')}
              className="flex items-center text-white/60 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-2 py-1"
              aria-label={locale === 'en' ? 'Cambiar a español' : 'Switch to English'}
            >
              <LanguageIcon className="w-4 h-4 mr-1" />
              {locale === 'en' ? 'ES' : 'EN'}
            </button>
            
            {/* Login link */}
            <Link 
              href="/login" 
              className="text-sm text-trinity-identity hover:text-trinity-consciousness transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-2 py-1"
            >
              {locale === 'en' ? 'Sign in' : 'Iniciar sesión'}
            </Link>
          </div>
        </header>

        {/* Main Content */}
        <main id="main-content" className="px-6 py-12" role="main">
          <div className="max-w-7xl mx-auto">
            {/* Page Title */}
            <div className="text-center mb-12">
              <h1 className="text-4xl font-light text-white mb-4">
                {t.title}
              </h1>
              <p className="text-lg text-white/60">
                {t.subtitle}
              </p>
            </div>

            {/* Billing Period Toggle */}
            <div className="flex justify-center mb-12">
              <div className="inline-flex items-center p-1 bg-black/40 backdrop-blur-xl rounded-lg border border-white/10">
                <button
                  onClick={() => setBillingPeriod('monthly')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    billingPeriod === 'monthly'
                      ? 'bg-trinity-identity text-white'
                      : 'text-white/60 hover:text-white'
                  }`}
                  aria-pressed={billingPeriod === 'monthly'}
                >
                  {t.billingToggle.monthly}
                </button>
                <button
                  onClick={() => setBillingPeriod('yearly')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    billingPeriod === 'yearly'
                      ? 'bg-trinity-identity text-white'
                      : 'text-white/60 hover:text-white'
                  }`}
                  aria-pressed={billingPeriod === 'yearly'}
                >
                  {t.billingToggle.yearly}
                </button>
                {billingPeriod === 'yearly' && (
                  <span className="ml-2 px-2 py-1 bg-trinity-guardian/20 text-trinity-guardian text-xs rounded-md">
                    {t.saveLabel}
                  </span>
                )}
              </div>
            </div>

            {/* Tier Cards Grid */}
            <TierGrid items={tierContent} />

            {/* Core Features Section */}
            <div className="mt-16 text-center">
              <h2 className="text-2xl font-light text-white mb-8">
                {t.features}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
                {t.coreFeatures.map((feature, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-center p-4 bg-white/[0.03] backdrop-blur-sm rounded-lg border border-white/10"
                  >
                    <CheckIcon className="w-5 h-5 text-trinity-guardian mr-2 flex-shrink-0" />
                    <span className="text-sm text-white/80">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Help Section */}
            <div className="mt-16 text-center">
              <div className="inline-flex items-center justify-center p-4 bg-black/40 backdrop-blur-xl rounded-lg border border-white/10">
                <QuestionMarkCircleIcon className="w-5 h-5 text-white/60 mr-2" />
                <span className="text-sm text-white/60">
                  {locale === 'en' 
                    ? 'Need help choosing? Contact our team for guidance.'
                    : '¿Necesitas ayuda para elegir? Contacta a nuestro equipo para orientación.'}
                </span>
              </div>
            </div>
          </div>
        </main>

        {/* Transparency Box */}
        <div className="px-6 pb-6">
          <TransparencyBox
            locale={locale}
            capabilities={[
              locale === 'en' 
                ? "Flexible tier system from Free to Enterprise" 
                : "Sistema de niveles flexible desde Gratis hasta Empresarial",
              locale === 'en'
                ? "Rate limiting with clear RPM/RPD boundaries"
                : "Límites de tasa con límites claros de RPM/RPD",
              locale === 'en'
                ? "SSO and SCIM for enterprise tiers"
                : "SSO y SCIM para niveles empresariales",
              locale === 'en'
                ? "Quantum-inspired processing at all tiers"
                : "Procesamiento cuántico-inspirado en todos los niveles",
              locale === 'en'
                ? "Guardian ethics system always active"
                : "Sistema guardián de ética siempre activo"
            ]}
            limitations={[
              locale === 'en'
                ? "Higher tiers require identity verification"
                : "Los niveles superiores requieren verificación de identidad",
              locale === 'en'
                ? "Rate limits strictly enforced"
                : "Límites de tasa estrictamente aplicados",
              locale === 'en'
                ? "Some features require step-up authentication"
                : "Algunas funciones requieren autenticación adicional",
              locale === 'en'
                ? "Enterprise features need contract approval"
                : "Las funciones empresariales necesitan aprobación de contrato"
            ]}
            dependencies={[
              locale === 'en'
                ? "Identity service for tier management"
                : "Servicio de identidad para gestión de niveles",
              locale === 'en'
                ? "Rate limiting infrastructure"
                : "Infraestructura de límites de tasa",
              locale === 'en'
                ? "SSO providers for enterprise authentication"
                : "Proveedores SSO para autenticación empresarial",
              locale === 'en'
                ? "Guardian system for ethics monitoring"
                : "Sistema guardián para monitoreo de ética"
            ]}
            dataHandling={[
              locale === 'en'
                ? "Usage metrics collected for tier enforcement"
                : "Métricas de uso recopiladas para aplicación de niveles",
              locale === 'en'
                ? "Authentication events logged for security"
                : "Eventos de autenticación registrados por seguridad",
              locale === 'en'
                ? "Billing information processed securely"
                : "Información de facturación procesada de forma segura",
              locale === 'en'
                ? "No data sharing between tiers"
                : "Sin intercambio de datos entre niveles"
            ]}
            className="max-w-4xl mx-auto"
          />
        </div>
      </div>
    </>
  )
}
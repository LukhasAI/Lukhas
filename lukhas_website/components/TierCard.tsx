import React from 'react'

// -------------------------------------------------------------
// TierCard: accessible, tone-linted card for /pricing
// - Renders three tone layers with data-tone attributes
// - Adds badges for SSO/SCIM/etc and shows rate envelopes
// - Pure Tailwind; no external UI libs required
// - Safe for MDX usage: export components and content maps
// -------------------------------------------------------------

export type TierId = 'T1'|'T2'|'T3'|'T4'|'T5'

export type TierContent = {
  id: TierId
  title: string // e.g., "Free (Public)" / "Gratis (Público)"
  poetic: string // ≤ 40 words
  technical: string // must include "Limits:" and "Dependencies:" / "Límites:" y "Dependencias:"
  plain: string // Grade 6–8
  rpm?: number
  rpd?: number
  badges?: string[] // e.g., ['SSO','SCIM']
}

export function TierCard({ item }: { item: TierContent }) {
  return (
    <article
      data-tier={item.id}
      aria-labelledby={`tier-${item.id}-title`}
      className="group relative rounded-2xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur-sm shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Header */}
      <header className="mb-3 flex items-start justify-between gap-3">
        <h3 id={`tier-${item.id}-title`} className="text-base font-semibold tracking-tight text-white/90">
          {item.title}
        </h3>
        {item.badges?.length ? (
          <div className="flex flex-wrap gap-1.5">
            {item.badges.map((b) => (
              <span key={b} className="rounded-full border border-white/15 px-2 py-0.5 text-[10px] leading-5 text-white/70">
                {b}
              </span>
            ))}
          </div>
        ) : null}
      </header>

      {/* Rate chips */}
      {(item.rpm || item.rpd) && (
        <div className="mb-3 flex flex-wrap gap-2 text-[11px] text-white/60">
          {item.rpm ? (
            <span className="rounded-md border border-white/10 bg-white/[0.04] px-2 py-0.5">RPM: {item.rpm}</span>
          ) : null}
          {item.rpd ? (
            <span className="rounded-md border border-white/10 bg-white/[0.04] px-2 py-0.5">RPD: {item.rpd.toLocaleString()}</span>
          ) : null}
        </div>
      )}

      {/* Tone sections */}
      <section data-tone="poetic" aria-label="Overview" className="mb-2 text-sm leading-relaxed text-white/90">
        <h4 className="sr-only">Overview</h4>
        {item.poetic}
      </section>

      <section data-tone="technical" aria-label="Details" className="mb-2 rounded-lg border border-white/10 bg-white/[0.035] p-3 text-[13px] leading-relaxed text-white/80">
        <h4 className="sr-only">Details</h4>
        {item.technical}
      </section>

      <section data-tone="plain" aria-label="Simple explanation" className="text-[13px] leading-relaxed text-white/85">
        <h4 className="sr-only">Simple explanation</h4>
        {item.plain}
      </section>
    </article>
  )
}

// -------------------------------------------------------------
// TierGrid: simple responsive wrapper
// -------------------------------------------------------------
export function TierGrid({ items }: { items: TierContent[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((it) => (
        <TierCard key={it.id} item={it} />
      ))}
    </div>
  )
}

// -------------------------------------------------------------
// Content maps (EN & ES) — mirror of your MDX strings
// You can import these straight into /pricing and pass to <TierGrid />
// -------------------------------------------------------------

export const TIER_CONTENT_EN: TierContent[] = [
  {
    id: 'T1',
    title: 'Free (Public)',
    poetic: 'A quiet place to look around and learn without pressure.',
    technical:
      'Read-only demos and docs. Limits: low quotas; no write/export. Dependencies: docs service, demo datasets, identity surface for minimal tracking.',
    plain: 'Try features safely with example data. No setup required.',
    rpm: 30,
    rpd: 1000,
  },
  {
    id: 'T2',
    title: 'Plus (Registered)',
    poetic: 'Hands on the clay; ideas begin to hold their shape.',
    technical:
      'Personal projects with moderate rates. Limits: capped write calls; no org tools. Dependencies: identity, storage, rate-limit store.',
    plain: 'Create and save your own work. Fair-use limits apply.',
    rpm: 60,
    rpd: 5000,
  },
  {
    id: 'T3',
    title: 'Team (Professionals) (Verified)',
    poetic: 'A shared room where roles keep the rhythm and work flows.',
    technical:
      'Team spaces, RBAC, higher quotas. Limits: exports bounded; some admin actions require step-up (WebAuthn/TOTP). Dependencies: org service, audit log, identity.',
    plain: 'Work as a team with roles and bigger limits.',
    rpm: 120,
    rpd: 20000,
    badges: ['RBAC']
  },
  {
    id: 'T4',
    title: 'Enterprise (Premium)',
    poetic: 'Strong rails for long journeys; governance lights the path.',
    technical:
      'SSO/SLA, governance tools, export controls. Limits: contractual quotas; region/retention policies. Dependencies: SSO, SCIM, governance, billing.',
    plain: 'Enterprise login, controls, and guaranteed support.',
    rpm: 300,
    rpd: 100000,
    badges: ['SSO', 'SLA', 'Governance']
  },
  {
    id: 'T5',
    title: 'Core Team (Internal)',
    poetic: 'Behind the curtain, the workshop key fits every lock.',
    technical:
      'Internal administration with least-privilege roles. Limits: SSO+SCIM required; local auth blocked; actions logged. Dependencies: IdP, SCIM, audit, policy engine.',
    plain: 'Employees/admins only. SSO required.',
    rpm: 1000,
    rpd: 1_000_000,
    badges: ['SSO', 'SCIM', 'Internal']
  },
]

export const TIER_CONTENT_ES: TierContent[] = [
  {
    id: 'T1',
    title: 'Gratis (Público)',
    poetic: 'Un espacio tranquilo para explorar y aprender sin presión.',
    technical:
      'Demos y documentación de solo lectura. Límites: cuotas bajas; sin escritura ni exportación. Dependencias: servicio de docs, datos de demo, identidad mínima.',
    plain: 'Prueba funciones con datos de ejemplo. No necesitas configurar nada.',
    rpm: 30,
    rpd: 1000,
  },
  {
    id: 'T2',
    title: 'Plus (Registrado)',
    poetic: 'Manos en la arcilla; las ideas toman forma.',
    technical:
      'Proyectos personales con tasas moderadas. Límites: escritura con tope; sin herramientas de organización. Dependencias: identidad, almacenamiento, límites.',
    plain: 'Crea y guarda tu trabajo con límites justos.',
    rpm: 60,
    rpd: 5000,
  },
  {
    id: 'T3',
    title: 'Team (Para profesionales) (Verificado)',
    poetic: 'Un taller compartido: los roles marcan el ritmo y el trabajo fluye.',
    technical:
      'Espacios de equipo, roles y cuotas mayores. Límites: exportaciones acotadas; acciones de admin con verificación extra. Dependencias: servicio de organización, auditoría, identidad.',
    plain: 'Colabora en equipo con roles y más capacidad.',
    rpm: 120,
    rpd: 20000,
    badges: ['RBAC']
  },
  {
    id: 'T4',
    title: 'Enterprise (Premium)',
    poetic: 'Vías firmes para viajes largos; la gobernanza ilumina el camino.',
    technical:
      'SSO/SLA, herramientas de gobernanza y control de exportación. Límites: cuotas por contrato; región y retención. Dependencias: SSO, SCIM, gobernanza, facturación.',
    plain: 'Acceso empresarial, controles y soporte garantizado.',
    rpm: 300,
    rpd: 100000,
    badges: ['SSO', 'SLA', 'Gobernanza']
  },
  {
    id: 'T5',
    title: 'Equipo Interno (Solo interno)',
    poetic: 'Tras el telón, la llave del taller abre todas las cerraduras.',
    technical:
      'Administración interna con mínimo privilegio. Límites: SSO+SCIM obligatorios; sin acceso local; acciones registradas. Dependencias: IdP, SCIM, auditoría, motor de políticas.',
    plain: 'Solo empleados y admins. SSO obligatorio.',
    rpm: 1000,
    rpd: 1_000_000,
    badges: ['SSO', 'SCIM', 'Interno']
  },
]

// -------------------------------------------------------------
// Example usage (in a Next.js/React page or MDX provider):
// -------------------------------------------------------------
// import { TierGrid, TIER_CONTENT_EN, TIER_CONTENT_ES } from '@/components/TierCard'
//
// export default function PricingPage({ locale = 'en' }) {
//   const data = locale === 'es' ? TIER_CONTENT_ES : TIER_CONTENT_EN
//   return (
//     <main className="mx-auto max-w-6xl px-4 py-10">
//       <h2 className="mb-6 text-2xl font-semibold tracking-tight text-white">Plans & Pricing</h2>
//       <TierGrid items={data} />
//     </main>
//   )
// }

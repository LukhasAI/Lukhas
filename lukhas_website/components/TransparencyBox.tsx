// -----------------------------------------------------------------------------
// components/TransparencyBox.tsx
// A11y-first, policy-friendly Transparency component with required sections:
//  - capabilities, limitations, dependencies, dataHandling
//  - EN/ES headings auto-localized via `locale`
//  - Machine-checkable data attributes for linters/tests
//  - Optional JSON-LD export for structured transparency notes
//  - Tailwind-only, light footprint
// -----------------------------------------------------------------------------

import React from 'react'

export type Locale = 'en' | 'es'

export type TransparencyBoxProps = {
  title?: string
  capabilities: string[]
  limitations: string[]
  dependencies: string[]
  dataHandling: string[]
  locale?: Locale
  compact?: boolean
  className?: string
  schemaOrg?: {
    appName: string // plain name, e.g., "Lukhas ID"
    appType?: 'SoftwareApplication' | 'WebApplication'
  } | false
}

const L = {
  en: {
    title: 'Transparency',
    capabilities: 'Capabilities',
    limitations: 'Limitations',
    dependencies: 'Dependencies',
    dataHandling: 'Data handling',
    biometrics: 'Biometric Authentication',
    adaptiveMFA: 'Adaptive Security',
  },
  es: {
    title: 'Transparencia',
    capabilities: 'Capacidades',
    limitations: 'Limitaciones',
    dependencies: 'Dependencias',
    dataHandling: 'Tratamiento de datos',
    biometrics: 'Autenticación Biométrica',
    adaptiveMFA: 'Seguridad Adaptativa',
  },
}

function Section({ id, label, items }: { id: string; label: string; items: string[] }) {
  return (
    <div data-section={id}>
      <h4 className="mb-1 text-sm font-semibold text-white/90">{label}</h4>
      <ul className="list-disc pl-4 text-[13px] leading-6 text-white/80">
        {items.map((t, i) => (
          <li key={i}>{t}</li>
        ))}
      </ul>
    </div>
  )
}

export function TransparencyBox(props: TransparencyBoxProps) {
  const {
    title,
    capabilities,
    limitations,
    dependencies,
    dataHandling,
    locale = 'en',
    compact = false,
    className = '',
    schemaOrg = false,
  } = props

  const t = L[locale]

  if (process.env.NODE_ENV !== 'production') {
    const missing: string[] = []
    if (!capabilities?.length) missing.push('capabilities')
    if (!limitations?.length) missing.push('limitations')
    if (!dependencies?.length) missing.push('dependencies')
    if (!dataHandling?.length) missing.push('dataHandling')
    if (missing.length) {
      // eslint-disable-next-line no-console
      console.warn(`[TransparencyBox] Missing sections: ${missing.join(', ')}`)
    }
  }

  const box = (
    <section
      role="region"
      aria-label={title || t.title}
      data-transparency="present"
      className={
        `rounded-2xl border border-white/10 bg-white/[0.03] p-4 sm:p-5 shadow-sm ${className}`
      }
    >
      <header className="mb-3">
        <h3 className="text-base font-semibold tracking-tight text-white/90">
          {title || t.title}
        </h3>
      </header>

      <div className={`grid gap-4 ${compact ? 'sm:grid-cols-1' : 'sm:grid-cols-2'}`}>
        <Section id="capabilities" label={t.capabilities} items={capabilities} />
        <Section id="limitations" label={t.limitations} items={limitations} />
        <Section id="dependencies" label={t.dependencies} items={dependencies} />
        <Section id="dataHandling" label={t.dataHandling} items={dataHandling} />
      </div>
    </section>
  )

  if (!schemaOrg) return box

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': schemaOrg.appType || 'SoftwareApplication',
    name: schemaOrg.appName,
    additionalProperty: [
      { '@type': 'PropertyValue', name: 'Capabilities', value: capabilities.join('; ') },
      { '@type': 'PropertyValue', name: 'Limitations', value: limitations.join('; ') },
      { '@type': 'PropertyValue', name: 'Dependencies', value: dependencies.join('; ') },
      { '@type': 'PropertyValue', name: 'Data handling', value: dataHandling.join('; ') },
    ],
  }

  return (
    <div>
      {box}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
    </div>
  )
}

export default TransparencyBox

// -----------------------------------------------------------------------------
// EXAMPLES — login/signup/pricing usage (TSX & MDX)
// -----------------------------------------------------------------------------

// app/login/TransparencyLogin.tsx
export function TransparencyLoginEN() {
  return (
    <TransparencyBox
      locale="en"
      schemaOrg={{ appName: 'Lukhas ID', appType: 'SoftwareApplication' }}
      capabilities={[
        'Passwordless sign-in with passkeys (WebAuthn)',
        'One-time email link fallback (10 minutes)',
        'Short-lived sessions with rotating refresh tokens',
      ]}
      limitations={[
        'Device support for passkeys varies by platform',
        'Email delivery may be delayed or blocked',
        'Password login is disabled unless enabled by an admin',
      ]}
      dependencies={[
        'Platform authenticators (biometrics or device PIN)',
        'Email service and rate-limit store',
        'Lukhas identity service',
      ]}
      dataHandling={[
        'No biometric data is stored; only a public key',
        'Hashed backup codes; security events are logged',
        'Cookies bind sessions to devices where applicable',
      ]}
    />
  )
}

export function TransparencyLoginES() {
  return (
    <TransparencyBox
      locale="es"
      schemaOrg={{ appName: 'Lukhas ID', appType: 'SoftwareApplication' }}
      capabilities={[
        'Acceso sin contraseña con passkeys (WebAuthn)',
        'Enlace de acceso por correo (10 minutos) como alternativa',
        'Sesiones de corta duración con refresh tokens rotativos',
      ]}
      limitations={[
        'El soporte de passkeys depende del dispositivo',
        'El correo puede retrasarse o bloquearse',
        'La contraseña está desactivada salvo que un admin la habilite',
      ]}
      dependencies={[
        'Autenticadores del sistema (biometría o PIN del dispositivo)',
        'Servicio de correo y almacén de límites',
        'Servicio de identidad de Lukhas',
      ]}
      dataHandling={[
        'No almacenamos biometría; solo una clave pública',
        'Códigos de respaldo hasheados; se registran eventos de seguridad',
        'Las cookies pueden vincular la sesión al dispositivo',
      ]}
    />
  )
}

// app/signup/TransparencySignup.tsx
export function TransparencySignupEN() {
  return (
    <TransparencyBox
      locale="en"
      schemaOrg={{ appName: 'Lukhas ID', appType: 'SoftwareApplication' }}
      capabilities={[
        'Email verification followed by passkey registration',
        'Multiple passkeys supported (e.g., phone + security key)',
        'Backup codes for account recovery',
      ]}
      limitations={[
        'Older devices may not support passkeys',
        'Email verification can be delayed',
        'Recovery depends on backup codes or additional passkeys',
      ]}
      dependencies={[
        'Email provider and deliverability configuration',
        'Platform authenticators and WebAuthn APIs',
        'Identity service and rate-limit store',
      ]}
      dataHandling={[
        'No biometric secrets are transmitted to our servers',
        'We store public keys and hashed recovery codes',
        'Audit logs record authentication events',
      ]}
    />
  )
}

export function TransparencySignupES() {
  return (
    <TransparencyBox
      locale="es"
      schemaOrg={{ appName: 'Lukhas ID', appType: 'SoftwareApplication' }}
      capabilities={[
        'Verificación de correo y luego registro de passkey',
        'Varias passkeys permitidas (por ejemplo, móvil + llave física)',
        'Códigos de respaldo para recuperación',
      ]}
      limitations={[
        'Algunos dispositivos no admiten passkeys',
        'La verificación por correo puede retrasarse',
        'La recuperación depende de códigos de respaldo o passkeys extra',
      ]}
      dependencies={[
        'Proveedor de correo y configuración de entregabilidad',
        'Autenticadores del sistema y APIs WebAuthn',
        'Servicio de identidad y almacén de límites',
      ]}
      dataHandling={[
        'No transmitimos secretos biométricos a nuestros servidores',
        'Almacenamos claves públicas y códigos de recuperación hasheados',
        'Los eventos de autenticación quedan registrados en auditoría',
      ]}
    />
  )
}

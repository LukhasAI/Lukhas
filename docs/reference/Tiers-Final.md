---
status: wip
type: documentation
---
# LUKHAS Authentication & Tiers - Final Documentation

## Spanish Language Decisions (ES)

Llave de acceso (passkey) → "Llave de acceso" (primera mención: "llave de acceso (passkey)").

No es una contraseña. Usa tu huella, rostro o PIN del dispositivo.

Contraseña → solo si el admin la habilita. Evita "clave" para no mezclar con "llave".

Enlace mágico → "enlace de acceso por correo (10 minutos)".

Códigos de respaldo → 10 códigos de un uso.

Verificación en dos pasos (TOTP) → "código de 6 dígitos en app de autenticación".

Llave física → "llave de seguridad USB/NFC (por ej., YubiKey)".

### /login — bloques ES (Poética / Técnica / Clara)

**Poética (≤40 palabras)**
Una puerta reconoce tu mano; nada que recordar, solo entrar.

**Técnica (con Límites y Dependencias)**
Método por defecto: llave de acceso (passkey) con verificación del usuario (WebAuthn).
Alternativa: enlace de acceso por correo (10 minutos).
La sesión usa JWT de corta duración y refresh tokens rotativos con detección de reutilización y vinculación al dispositivo.
Se requiere verificación adicional para pagos, claves de API y administración.
Límites: soporte de llaves según dispositivo; el correo puede tardar; la contraseña está desactivada salvo que un admin la habilite.
Dependencias: autenticador del sistema, servicio de correo, almacén de límites y el servicio de identidad de Lukhas. No guardamos biometría; almacenamos una clave pública.

**Clara**
Entra con tu dispositivo. No hay contraseña.
Si falla, te enviamos un enlace de acceso que vence en 10 minutos.
Guarda tus códigos de respaldo.
Puedes añadir más de un dispositivo.

### /signup — bloques ES (Poética / Técnica / Clara)

**Poética (≤40 palabras)**
Empieza con tu propia llave; lo demás llega sin esfuerzo.

**Técnica (con Límites y Dependencias)**
Registro en dos pasos: verificación de correo y creación de una llave de acceso (passkey) con verificación del usuario.
Puedes añadir una segunda llave (otro dispositivo o llave física).
La contraseña no aparece por defecto.
Límites: algunos dispositivos no admiten llaves de acceso; los correos pueden retrasarse; la recuperación depende de códigos de respaldo o llaves adicionales.
Dependencias: proveedor de correo, autenticadores del sistema, almacén de límites y servicio de identidad. No guardamos biometría; almacenamos una clave pública.

**Clara**
Confirma tu correo.
Crea una llave de acceso con tu huella, rostro o PIN del dispositivo.
Añade otra llave (otro móvil o una llave física) como respaldo.
Si pierdes acceso, usa códigos de respaldo para volver a entrar.

### Glosario mínimo (mostrar en tooltip o "¿Qué es esto?")

Llave de acceso (passkey): credencial sin contraseña que vive en tu dispositivo. Se usa con huella, rostro o PIN.

Enlace de acceso por correo: email con un enlace de un solo uso que caduca en 10 minutos.

Códigos de respaldo: 10 códigos de un uso; imprime y guarda sin conexión.

Verificación en dos pasos (TOTP): código de 6 dígitos generado por una app (mejor que SMS).

Llave física: dispositivo USB/NFC que confirma tu identidad al tocarlo.

### Microcopy y etiquetas (ES)

Botón principal: Iniciar sesión con ΛiD (aria-label="Iniciar sesión con Lukhas ID")

Secundario: Enviarme un enlace de acceso (10 min)

En recuperación: Usar códigos de respaldo

En seguridad: Añadir llave de acceso · Añadir llave física · Configurar verificación en dos pasos

Mensajes sin enumeración (misma respuesta exista o no el email):

"Si el correo es correcto, te enviaremos un enlace de acceso."

### Consejos de seguridad y entropía (texto breve, contextual)

Llaves de acceso: protege tu dispositivo con PIN/biometría y actualízalo. Añade dos llaves (por ejemplo, móvil + llave física).

Códigos de respaldo: imprime y guarda fuera del ordenador; tacha los usados.

Dos pasos (TOTP): usa una app de autenticación; evita SMS cuando sea posible.

Si se habilitan contraseñas: usa frases de paso (4+ palabras) y no las reutilices.

### Opcional: wrappers para pasar el linter de tono

Si tus páginas usan MDX/TSX y el linter busca data-tone, puedes envolver así:

```html
<section data-tone="poetic">Una puerta reconoce tu mano; nada que recordar, solo entrar.</section>

<section data-tone="technical">
Método por defecto: llave de acceso (passkey) con verificación del usuario (WebAuthn).
Alternativa: enlace de acceso por correo (10 minutos).
La sesión usa JWT de corta duración y refresh tokens rotativos con detección de reutilización y vinculación al dispositivo.
Se requiere verificación adicional para pagos, claves de API y administración.
Límites: soporte de llaves según dispositivo; el correo puede tardar; la contraseña está desactivada salvo que un admin la habilite.
Dependencias: autenticador del sistema, servicio de correo, almacén de límites y el servicio de identidad de Lukhas. No guardamos biometría; almacenamos una clave pública.
</section>

<section data-tone="plain">
Entra con tu dispositivo. No hay contraseña.
Si falla, te enviamos un enlace de acceso que vence en 10 minutos.
Guarda tus códigos de respaldo.
Puedes añadir más de un dispositivo.
</section>
```

## English Version

### Login / Signup Copy (English)

**Poetic**

A door that recognizes your hand; nothing to remember, only to be yourself.

Begin with your own key; the rest flows with ease.

**Technical**

Login: Use your passkey first. If your device doesn't support it, request a magic link by email. Passwords are hidden by default and only appear if explicitly enabled.

Signup: Verify your email, then register your first passkey (WebAuthn with user verification). You may add a second passkey for recovery. Passwords remain optional and off by default.

Limits: Some devices may not support passkeys. Email links may be delayed. Recovery uses backup codes or additional passkeys.

Dependencies: Email provider, system authenticators, rate-limit store, and identity service.

**Plain**

Log in: Click to sign in with a passkey (fingerprint, face, or device PIN). If unavailable, you'll get a one-time email link. You don't need to type or remember a password.

Sign up: First, confirm your email. Then create a passkey. It works like unlocking your phone—safe and simple. You can add a backup passkey for extra safety.

If you ever lose access, you can use backup codes or another passkey to get back in.

## Final Tier Names & Levels

### English (public labels)
- **T1 — Free (Public)**
- **T2 — Plus (Registered)**
- **T3 — Team (Professionals) (Verified)**
- **T4 — Enterprise (Premium)**
- **T5 — Core Team (Internal)**

### Español (public labels)
- **T1 — Gratis (Público)**
- **T2 — Plus (Registrado)**
- **T3 — Team (Para Profesionales) (Verificado)**
- **T4 — Enterprise (Premium)**
- **T5 — Equipo Interno (Solo interno)**

Internal IDs stay T1..T5. Public pages show the English label by default; Spanish UI shows the ES label above.

### Paste-ready config for implementation

```typescript
export type Tier = 'T1'|'T2'|'T3'|'T4'|'T5';

// Public labels
export const TIER_LABELS_EN: Record<Tier,string> = {
  T1: 'Free (Public)',
  T2: 'Plus (Registered)',
  T3: 'Team (Professionals) (Verified)',
  T4: 'Enterprise (Premium)',
  T5: 'Core Team (Internal)'
};

export const TIER_LABELS_ES: Record<Tier,string> = {
  T1: 'Gratis (Público)',
  T2: 'Plus (Registrado)',
  T3: 'Team (Para Profesionales) (Verificado)',
  T4: 'Enterprise (Premium)',
  T5: 'Equipo Interno (Solo interno)'
};

// Map to plan engine aligned with gating (free/plus/team/enterprise/core)
export const TIER_PLAN_MAP: Record<Tier,'free'|'plus'|'team'|'enterprise'|'core'> = {
  T1: 'free',
  T2: 'plus',
  T3: 'team',
  T4: 'enterprise',
  T5: 'core'
};

// Scope envelopes (deny-by-default in middleware)
export const TIER_SCOPES: Record<Tier,string[]> = {
  T1: ['docs:read','matriz:demo:read'],
  T2: ['app:read','api:read','matriz:read'],
  T3: ['app:read','app:write','api:keys:create','matriz:write','orchestrator:run','org:read'],
  T4: ['org:settings','matriz:export','billing:manage','api:keys:*','orchestrator:*'],
  T5: ['*'] // still constrained by roles (owner/admin/developer/analyst/viewer)
};

// Rate envelopes (override via env/contract if needed)
export const RATE_LIMITS = {
  T1: { rpm: 30,  rpd: 1_000 },
  T2: { rpm: 60,  rpd: 5_000 },
  T3: { rpm: 120, rpd: 20_000 },
  T4: { rpm: 300, rpd: 100_000 },
  T5: { rpm: 1000, rpd: 1_000_000 }
} as const;
```

### Three-layer copy per tier (EN + ES)

#### T1 — Free / Gratis

**EN Poetic (≤40w):**
A quiet place to look around and learn without pressure.

**EN Technical:**
Read-only demos and docs. Limits: low quotas; no write/export. Dependencies: docs service, demo datasets, identity surface for minimal tracking.

**EN Plain:**
Try features safely with example data. No setup required.

**ES Poética (≤40 palabras):**
Un espacio tranquilo para explorar y aprender sin presión.

**ES Técnica:**
Demos y documentación de solo lectura. Límites: cuotas bajas; sin escritura ni exportación. Dependencias: servicio de docs, datos de demo, identidad mínima.

**ES Clara:**
Prueba funciones con datos de ejemplo. No necesitas configurar nada.

#### T2 — Plus / Plus

**EN Poetic:**
Hands on the clay; ideas begin to hold their shape.

**EN Technical:**
Personal projects with moderate rates. Limits: capped write calls; no org tools. Dependencies: identity, storage, rate-limit store.

**EN Plain:**
Create and save your own work. Fair-use limits apply.

**ES Poética:**
Manos en la arcilla; las ideas toman forma.

**ES Técnica:**
Proyectos personales con tasas moderadas. Límites: escritura con tope; sin herramientas de organización. Dependencias: identidad, almacenamiento, límites.

**ES Clara:**
Crea y guarda tu trabajo con límites justos.

#### T3 — Team (Professionals) / Team (Para Profesionales)

**EN Poetic:**
A shared room where roles keep the rhythm and work flows.

**EN Technical:**
Team spaces, RBAC, higher quotas. Limits: exports bounded; some admin actions require step-up (WebAuthn/TOTP). Dependencies: org service, audit log, identity.

**EN Plain:**
Work as a team with roles and bigger limits.

**ES Poética:**
Un taller compartido: los roles marcan el ritmo y el trabajo fluye.

**ES Técnica:**
Espacios de equipo, roles y cuotas mayores. Límites: exportaciones acotadas; acciones de admin con verificación extra. Dependencias: servicio de organización, auditoría, identidad.

**ES Clara:**
Colabora en equipo con roles y más capacidad.

#### T4 — Enterprise (Premium) / Enterprise (Premium)

**EN Poetic:**
Strong rails for long journeys; governance lights the path.

**EN Technical:**
SSO/SLA, governance tools, export controls. Limits: contractual quotas; region/retention policies. Dependencies: SSO, SCIM, governance, billing.

**EN Plain:**
Enterprise login, controls, and guaranteed support.

**ES Poética:**
Vías firmes para viajes largos; la gobernanza ilumina el camino.

**ES Técnica:**
SSO/SLA, herramientas de gobernanza y control de exportación. Límites: cuotas por contrato; región y retención. Dependencias: SSO, SCIM, gobernanza, facturación.

**ES Clara:**
Acceso empresarial, controles y soporte garantizado.

#### T5 — Core Team (Internal) / Equipo Interno

**EN Poetic:**
Behind the curtain, the workshop key fits every lock.

**EN Technical:**
Internal administration with least-privilege roles. Limits: SSO+SCIM required; local auth blocked; actions logged. Dependencies: IdP, SCIM, audit, policy engine.

**EN Plain:**
Employees/admins only. SSO required.

**ES Poética:**
Tras el telón, la llave del taller abre todas las cerraduras.

**ES Técnica:**
Administración interna con mínimo privilegio. Límites: SSO+SCIM obligatorios; sin acceso local; acciones registradas. Dependencias: IdP, SCIM, auditoría, motor de políticas.

**ES Clara:**
Solo empleados y admins. SSO obligatorio.

## MDX Snippets Ready for Implementation

### pricing.tiers.en.mdx
```html
<!-- T1 — Free (Public) -->
<article data-tier="T1">
  <h3>Free (Public)</h3>
  <section data-tone="poetic">
    A quiet place to look around and learn without pressure.
  </section>
  <section data-tone="technical">
    Read-only demos and docs.
    <strong>Limits:</strong> low quotas; no write/export.
    <strong>Dependencies:</strong> docs service, demo datasets, identity surface for minimal tracking.
  </section>
  <section data-tone="plain">
    Try features safely with example data. No setup required.
  </section>
</article>

<!-- T2 — Plus (Registered) -->
<article data-tier="T2">
  <h3>Plus (Registered)</h3>
  <section data-tone="poetic">
    Hands on the clay; ideas begin to hold their shape.
  </section>
  <section data-tone="technical">
    Personal projects with moderate rates.
    <strong>Limits:</strong> capped write calls; no org tools.
    <strong>Dependencies:</strong> identity, storage, rate-limit store.
  </section>
  <section data-tone="plain">
    Create and save your own work. Fair-use limits apply.
  </section>
</article>

<!-- T3 — Team (Professionals) (Verified) -->
<article data-tier="T3">
  <h3>Team (Professionals) (Verified)</h3>
  <section data-tone="poetic">
    A shared room where roles keep the rhythm and work flows.
  </section>
  <section data-tone="technical">
    Team spaces, RBAC, higher quotas.
    <strong>Limits:</strong> exports bounded; some admin actions require step-up (WebAuthn/TOTP).
    <strong>Dependencies:</strong> org service, audit log, identity.
  </section>
  <section data-tone="plain">
    Work as a team with roles and bigger limits.
  </section>
</article>

<!-- T4 — Enterprise (Premium) -->
<article data-tier="T4">
  <h3>Enterprise (Premium)</h3>
  <section data-tone="poetic">
    Strong rails for long journeys; governance lights the path.
  </section>
  <section data-tone="technical">
    SSO/SLA, governance tools, export controls.
    <strong>Limits:</strong> contractual quotas; region/retention policies.
    <strong>Dependencies:</strong> SSO, SCIM, governance, billing.
  </section>
  <section data-tone="plain">
    Enterprise login, controls, and guaranteed support.
  </section>
</article>

<!-- T5 — Core Team (Internal) -->
<article data-tier="T5">
  <h3>Core Team (Internal)</h3>
  <section data-tone="poetic">
    Behind the curtain, the workshop key fits every lock.
  </section>
  <section data-tone="technical">
    Internal administration with least-privilege roles.
    <strong>Limits:</strong> SSO+SCIM required; local auth blocked; actions logged.
    <strong>Dependencies:</strong> IdP, SCIM, audit, policy engine.
  </section>
  <section data-tone="plain">
    Employees/admins only. SSO required.
  </section>
</article>
```

### pricing.tiers.es.mdx
```html
<!-- T1 — Gratis (Público) -->
<article data-tier="T1">
  <h3>Gratis (Público)</h3>
  <section data-tone="poetic">
    Un espacio tranquilo para explorar y aprender sin presión.
  </section>
  <section data-tone="technical">
    Demos y documentación de solo lectura.
    <strong>Límites:</strong> cuotas bajas; sin escritura ni exportación.
    <strong>Dependencias:</strong> servicio de docs, datos de demo, identidad mínima.
  </section>
  <section data-tone="plain">
    Prueba funciones con datos de ejemplo. No necesitas configurar nada.
  </section>
</article>

<!-- T2 — Plus (Registrado) -->
<article data-tier="T2">
  <h3>Plus (Registrado)</h3>
  <section data-tone="poetic">
    Manos en la arcilla; las ideas toman forma.
  </section>
  <section data-tone="technical">
    Proyectos personales con tasas moderadas.
    <strong>Límites:</strong> escritura con tope; sin herramientas de organización.
    <strong>Dependencias:</strong> identidad, almacenamiento, límites.
  </section>
  <section data-tone="plain">
    Crea y guarda tu trabajo con límites justos.
  </section>
</article>

<!-- T3 — Team (Para Profesionales) (Verificado) -->
<article data-tier="T3">
  <h3>Team (Para Profesionales) (Verificado)</h3>
  <section data-tone="poetic">
    Un taller compartido: los roles marcan el ritmo y el trabajo fluye.
  </section>
  <section data-tone="technical">
    Espacios de equipo, roles y cuotas mayores.
    <strong>Límites:</strong> exportaciones acotadas; acciones de admin con verificación extra.
    <strong>Dependencias:</strong> servicio de organización, auditoría, identidad.
  </section>
  <section data-tone="plain">
    Colabora en equipo con roles y más capacidad.
  </section>
</article>

<!-- T4 — Enterprise (Premium) -->
<article data-tier="T4">
  <h3>Enterprise (Premium)</h3>
  <section data-tone="poetic">
    Vías firmes para viajes largos; la gobernanza ilumina el camino.
  </section>
  <section data-tone="technical">
    SSO/SLA, herramientas de gobernanza y control de exportación.
    <strong>Límites:</strong> cuotas por contrato; región y retención.
    <strong>Dependencias:</strong> SSO, SCIM, gobernanza, facturación.
  </section>
  <section data-tone="plain">
    Acceso empresarial, controles y soporte garantizado.
  </section>
</article>

<!-- T5 — Equipo Interno (Solo interno) -->
<article data-tier="T5">
  <h3>Equipo Interno (Solo interno)</h3>
  <section data-tone="poetic">
    Tras el telón, la llave del taller abre todas las cerraduras.
  </section>
  <section data-tone="technical">
    Administración interna con mínimo privilegio.
    <strong>Límites:</strong> SSO+SCIM obligatorios; sin acceso local; acciones registradas.
    <strong>Dependencias:</strong> IdP, SCIM, auditoría, motor de políticas.
  </section>
  <section data-tone="plain">
    Solo empleados y admins. SSO obligatorio.
  </section>
</article>
```

## Commands to run (exact)
```bash
# Full policy suite (brand/tone/route/registry/vocab + routes scanner)
make policy

# You can also run individual targets if needed:
make policy-registries
make policy-brand
make policy-tone
make policy-routes
npm run vocab:validate
```

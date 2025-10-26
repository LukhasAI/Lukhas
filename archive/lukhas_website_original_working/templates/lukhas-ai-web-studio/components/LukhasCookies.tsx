import React, { useEffect, useMemo, useState } from "react";

type ConsentKeys = "essential" | "functional" | "analytics" | "research";

type ConsentState = {
  version: string;
  updatedAt: string; // ISO
  region?: "EU" | "US" | "Other";
  choices: Record<ConsentKeys, boolean>;
};

type Props = {
  locale?: "en" | "es";
  version?: string; // bump when copy/policy changes
  storageKey?: string;
  regionHint?: ConsentState["region"];
  onSave?: (consent: ConsentState) => void;
  links?: {
    privacy?: string;
    termsEU?: string;
    cookiePolicy?: string;
  };
};

const STRINGS = {
  en: {
    title: "Your data, your call.",
    intro:
      "LUKHΛS uses only essential cookies by default. Optional cookies help with reliability, basic analytics, and (only if you opt in) research to improve our systems. We never sell your data. You can change your choices any time.",
    essentialLabel: "Essential",
    essentialDesc:
      "Required for security and core site functionality. Always on.",
    functionalLabel: "Functional",
    functionalDesc:
      "Remembers your settings (theme, language) and improves basic UX.",
    analyticsLabel: "Analytics",
    analyticsDesc:
      "Privacy-preserving, aggregated usage metrics to help us understand what's working.",
    researchLabel: "Research",
    researchDesc:
      "Optional signals to help improve LUKHΛS models. Processed with safeguards and never used for ads.",
    actions: {
      acceptEssential: "Essential only",
      acceptSelected: "Allow selected",
      acceptAll: "Allow all",
      preferences: "Preferences",
      save: "Save",
      cancel: "Cancel",
    },
    footer: {
      learnMore: "Learn more:",
      privacy: "Privacy Policy",
      terms: "EU Terms",
      cookies: "Cookie Policy",
    },
    toastSaved: "Your cookie choices are saved.",
  },
  es: {
    title: "Tus datos, tu decisión.",
    intro:
      "LUKHΛS solo usa cookies esenciales por defecto. Las opcionales ayudan con la fiabilidad, analítica básica y (solo si aceptas) investigación para mejorar nuestros sistemas. Nunca vendemos tus datos. Puedes cambiar tus opciones cuando quieras.",
    essentialLabel: "Esenciales",
    essentialDesc:
      "Necesarias para seguridad y funcionamiento básico del sitio. Siempre activas.",
    functionalLabel: "Funcionales",
    functionalDesc:
      "Recuerdan tus preferencias (tema, idioma) y mejoran la UX.",
    analyticsLabel: "Analítica",
    analyticsDesc:
      "Métricas agregadas y con privacidad para entender qué funciona.",
    researchLabel: "Investigación",
    researchDesc:
      "Señales opcionales para mejorar los modelos de LUKHΛS. Con salvaguardas y nunca para anuncios.",
    actions: {
      acceptEssential: "Solo esenciales",
      acceptSelected: "Permitir seleccionadas",
      acceptAll: "Permitir todas",
      preferences: "Preferencias",
      save: "Guardar",
      cancel: "Cancelar",
    },
    footer: {
      learnMore: "Más información:",
      privacy: "Política de Privacidad",
      terms: "Términos UE",
      cookies: "Política de Cookies",
    },
    toastSaved: "Tus preferencias de cookies se han guardado.",
  },
};

const defaultChoices: ConsentState["choices"] = {
  essential: true,
  functional: false,
  analytics: false,
  research: false,
};

export default function LukhasCookies({
  locale = "en",
  version = "1.0.0",
  storageKey = "lukhas_consent_v1",
  regionHint,
  onSave,
  links = {
    privacy: "/legal/privacy.html",
    termsEU: "/legal/terms-eu.html",
    cookiePolicy: "/legal/cookie-policy.html",
  },
}: Props) {
  const t = STRINGS[locale] ?? STRINGS.en;
  const [open, setOpen] = useState(false);
  const [showPrefs, setShowPrefs] = useState(false);
  const [choices, setChoices] = useState<ConsentState["choices"]>(defaultChoices);

  const saved = useMemo<ConsentState | null>(() => {
    try {
      const raw = localStorage.getItem(storageKey);
      return raw ? (JSON.parse(raw) as ConsentState) : null;
    } catch {
      return null;
    }
  }, [storageKey]);

  useEffect(() => {
    const needsBanner =
      !saved || !saved.version || saved.version !== version;
    if (needsBanner) {
      setOpen(true);
      setChoices(saved?.choices ?? defaultChoices);
    }
  }, [saved, version]);

  function persist(next: ConsentState["choices"]) {
    const record: ConsentState = {
      version,
      updatedAt: new Date().toISOString(),
      region: regionHint ?? saved?.region ?? "EU",
      choices: next,
    };
    localStorage.setItem(storageKey, JSON.stringify(record));
    onSave?.(record);
  }

  function acceptAll() {
    const allOn: ConsentState["choices"] = {
      essential: true,
      functional: true,
      analytics: true,
      research: true,
    };
    persist(allOn);
    setOpen(false);
  }

  function acceptEssential() {
    persist({ ...defaultChoices });
    setOpen(false);
  }

  function acceptSelected() {
    persist(choices);
    setOpen(false);
  }

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="lukhas-cookie-title"
      className="lukhas-cookie-wrap"
      style={{
        position: "fixed",
        inset: "auto 1rem 1rem 1rem",
        zIndex: 9999,
        maxWidth: 720,
        margin: "0 auto",
        borderRadius: 12,
        border: "1px solid rgba(255,255,255,0.08)",
        background:
          "linear-gradient(180deg, rgba(10,12,20,0.92) 0%, rgba(10,12,20,0.88) 100%)",
        color: "var(--text, #EAECEF)",
        boxShadow: "0 10px 30px rgba(0,0,0,0.35)",
        backdropFilter: "saturate(1.1) blur(8px)",
      }}
    >
      <div style={{ padding: "16px 18px" }}>
        <h2 id="lukhas-cookie-title" style={{ margin: "0 0 8px 0", fontSize: 18 }}>
          {t.title}
        </h2>
        <p style={{ margin: 0, opacity: 0.9, lineHeight: 1.5 }}>{t.intro}</p>

        {!showPrefs ? (
          <div
            style={{
              display: "flex",
              gap: 8,
              flexWrap: "wrap",
              marginTop: 14,
              alignItems: "center",
            }}
          >
            <button className="btn ghost" onClick={() => setShowPrefs(true)} aria-expanded={showPrefs}>
              {t.actions.preferences}
            </button>
            <div style={{ flex: 1 }} />
            <button className="btn subtle" onClick={acceptEssential}>
              {t.actions.acceptEssential}
            </button>
            <button className="btn primary" onClick={acceptAll}>
              {t.actions.acceptAll}
            </button>
          </div>
        ) : (
          <div style={{ marginTop: 12 }}>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 10 }}>
              <PrefRow
                id="essential"
                label={t.essentialLabel}
                desc={t.essentialDesc}
                checked
                disabled
                onChange={() => {}}
              />
              <PrefRow
                id="functional"
                label={t.functionalLabel}
                desc={t.functionalDesc}
                checked={choices.functional}
                onChange={(v) => setChoices((c) => ({ ...c, functional: v }))}
              />
              <PrefRow
                id="analytics"
                label={t.analyticsLabel}
                desc={t.analyticsDesc}
                checked={choices.analytics}
                onChange={(v) => setChoices((c) => ({ ...c, analytics: v }))}
              />
              <PrefRow
                id="research"
                label={t.researchLabel}
                desc={t.researchDesc}
                checked={choices.research}
                onChange={(v) => setChoices((c) => ({ ...c, research: v }))}
              />
            </ul>

            <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
              <button className="btn ghost" onClick={() => setShowPrefs(false)}>
                {t.actions.cancel}
              </button>
              <div style={{ flex: 1 }} />
              <button className="btn subtle" onClick={acceptEssential}>
                {t.actions.acceptEssential}
              </button>
              <button className="btn primary" onClick={acceptSelected}>
                {t.actions.acceptSelected}
              </button>
            </div>
          </div>
        )}

        <div
          style={{
            marginTop: 10,
            display: "flex",
            gap: 12,
            alignItems: "center",
            fontSize: 13,
            opacity: 0.85,
          }}
        >
          <span>{t.footer.learnMore}</span>
          <a className="link" href={links.privacy}>{t.footer.privacy}</a>
          <a className="link" href={links.termsEU}>{t.footer.terms}</a>
          <a className="link" href={links.cookiePolicy}>{t.footer.cookies}</a>
        </div>
      </div>

      {/* Minimal inline styles for buttons/links */}
      <style>{`
        .btn {
          border-radius: 10px;
          padding: 8px 12px;
          font-weight: 600;
          border: 1px solid rgba(255,255,255,0.12);
          background: rgba(255,255,255,0.04);
          color: #EAECEF;
          cursor: pointer;
        }
        .btn:hover { background: rgba(255,255,255,0.08); }
        .btn.primary { background: #3a64ff; border-color: #3a64ff; color: white; }
        .btn.primary:hover { filter: brightness(1.05); }
        .btn.subtle { background: rgba(255,255,255,0.06); }
        .btn.ghost { background: transparent; border-color: rgba(255,255,255,0.16); }
        .link { color: #a7b4ff; text-decoration: none; }
        .link:hover { text-decoration: underline; }
      `}</style>
    </div>
  );
}

function PrefRow({
  id,
  label,
  desc,
  checked,
  disabled,
  onChange,
}: {
  id: string;
  label: string;
  desc: string;
  checked?: boolean;
  disabled?: boolean;
  onChange: (checked: boolean) => void;
}) {
  const inputId = `lukhas-cookie-${id}`;
  return (
    <li
      style={{
        display: "grid",
        gridTemplateColumns: "1fr auto",
        gap: 12,
        alignItems: "center",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 10,
        padding: "10px 12px",
        background: "rgba(255,255,255,0.02)",
      }}
    >
      <div>
        <label htmlFor={inputId} style={{ fontWeight: 600, display: "block" }}>
          {label}
        </label>
        <p style={{ margin: "4px 0 0 0", fontSize: 13, opacity: 0.85 }}>{desc}</p>
      </div>
      <div>
        <input
          id={inputId}
          type="checkbox"
          checked={!!checked}
          disabled={disabled}
          onChange={(e) => onChange(e.target.checked)}
          aria-describedby={`${inputId}-desc`}
        />
      </div>
    </li>
  );
}

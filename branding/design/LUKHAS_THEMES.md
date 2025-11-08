# LUKHAS Themes & Cognitive-Friendly Mode — Spec

> **📌 CANONICAL SOURCE OF TRUTH FOR THEME SYSTEM**
> This document defines the authoritative theme specifications for LUKHAS ecosystem.

**Document Status**: ✅ Canonical
**Version**: 2.0
**Last Updated**: 2025-11-06
**Location**: `branding/design/LUKHAS_THEMES.md`
**Related**: [BRAND_GUIDELINES.md](../BRAND_GUIDELINES.md), [MASTER_PALETTE.yaml](colors/MASTER_PALETTE.yaml)

---

## 1 — Design principle (short)

* **Dark-first by default.** LUKHAS brand *defaults* to the dark theme (immersive, cosmic).
* **Light as alternative.** Provide a single-click / account setting / system-pref override to switch.
* **Cognitive-Friendly mode** (name: **Assistive Mode**) — an alternate UI/UX + content mode for people with cognitive or attention difficulties: higher contrast, larger icons and font, simplified language and structure, reduced motion, reduced metaphor/poetry, explicit affordances, and larger hit targets.

Everything below explains what to change and how to implement it.

---

## 2 — Theme tokens & CSS structure (dark-first)

### 2.1 Token model

We use CSS variables with theme overrides. Put this in your `design-tokens.json` and generate `:root` variables.

**Base tokens (shared)**:

```css
:root{
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --font-body: 16px;
  --radius-md: 8px;
  --btn-radius: 8px;
  --focus-ring: 3px;
}
```

**Dark theme (default)**

```css
:root{
  --bg: #0B0F1A;                /* primary dark surface */
  --surface: #0F1724;           /* elevated panels */
  --text: #E6EEF6;              /* main text */
  --muted-text: #9AA7B8;
  --matriz-accent: #7A3BFF;
  --identity-accent: #0EA5A4;
  --primary-cta-bg: var(--matriz-accent);
  --primary-cta-color: #fff;
  --card-bg: #071124;
}
```

**Light theme (alternative)**

```css
:root.light {
  --bg: #FFFFFF;
  --surface: #F7FAFC;
  --text: #0B1220;
  --muted-text: #475569;
  --matriz-accent: #6E3BFF;      /* slightly adjusted for contrast on light */
  --identity-accent: #0EA5A4;
  --primary-cta-bg: var(--matriz-accent);
  --primary-cta-color: #fff;
  --card-bg: #ffffff;
}
```

**Assistive / Cognitive-Friendly theme**

```css
:root.assistive {
  --bg: #0B0F1A;                  /* we keep dark UI to retain brand */
  --surface: #10131A;             /* slightly brighter panels */
  --text: #FFFFFF;
  --muted-text: #D1E4F2;
  --matriz-accent: #8C6DFF;       /* higher saturation for contrast */
  --primary-cta-bg: var(--matriz-accent);
  --primary-cta-color: #0B0F1A;
  --card-bg: #0B1118;

  /* Bigger base metrics */
  --font-body: 18px;              /* bigger default */
  --icon-size-lg: 32px;
  --icon-size-md: 24px;
  --icon-size-sm: 20px;
  --space-md: 20px;
  --space-lg: 32px;
  --btn-padding: 14px 22px;
  --focus-ring: 4px;
}
```

> Implementation: apply `document.documentElement.classList.add('assistive')` or `.light` for user preference.

### 2.2 CSS patterns for components

* All buttons, inputs, nav items must use `em` / `rem` sizing relative to `--font-body` so Assistive Mode scales naturally.
* Example for icon sizing:

```css
.icon { width: var(--icon-size-md); height: var(--icon-size-md); }
:root { --icon-size-md: 20px; }
:root.assistive { --icon-size-md: 28px; } /* bigger */
```

* Focus ring: `outline: none; box-shadow: 0 0 0 var(--focus-ring) var(--matriz-accent);`

---

## 3 — Assistive Mode: UI & visual rules (detailed)

### 3.1 Layout & sizing

* **Base font-size:** increase to `18px` (see token).
* **Line-height:** 1.6 for body text; headings have 1.25.
* **Hit target:** interactive controls minimum 44×44px; preferred 56×56px.
* **Iconography:** increase icons by ~25–40% (tokens above). Always show labels under icons (no icon-only controls).
* **Spacing:** +20–30% spacing around major blocks; increase margin/padding tokens.

### 3.2 Contrast & color

* Maintain WCAG contrast ≥ 4.5:1 for body text; for headings and UI emphasis strive for ≥ 7:1. Use the assistive theme token palette to achieve this.

### 3.3 Motion

* **Reduce motion aggressively.** Default assistive mode: `prefers-reduced-motion` is implied — particles disabled or reduced to static/low-motion.
* When particle system is present, provide a “Pause/Reduce Motion” control in header and respect `prefers-reduced-motion`. In assistive mode, particles default to static gradient or low-density.

### 3.4 Interaction patterns

* Always show explicit affordances: labels, tooltips, persistent help text.
* For any progressive disclosure (e.g., reasoning graphs), provide a “Show me step-by-step” linear view: collapsed semantic steps rather than a complex network solely.

---

## 4 — Assistive Mode: Content & voice rules

The Assistive Mode is not only visual — it **changes language** and the way information is presented.

### 4.1 Tone changes (quantified)

When rendering cognitive variant of a page:

* Poetic → reduce by 60% of original share
* User-friendly → increase by 30% of original share
* Academic → reduce by 30% of original share

**Example numeric mapping for lukhas.ai** (default 40/40/20):

* Assistive Mode: Poetic ≈ 16% | User-friendly ≈ 58% | Academic ≈ 26%
  Practically: lots more plain language, fewer metaphors, clearer instructions.

### 4.2 Structural rules for copy

* **Short sentences** — average sentence length ~12–14 words.
* **Headlines & subheads** every 100–150 words.
* **Bulleted lists** for steps; avoid nested bullets > 2 levels.
* **Single idea per paragraph** (max 3–4 sentences).
* **Explicit schema** for actions: Problem → What we do → What you do (3 lines max).

### 4.3 Microcopy & vocabulary adjustments

* Replace metaphors (“dreaming”, “quantum dust”) with plain captions: explain what the visual means literally.
* Provide explicit help text for features: e.g., Reasoning Graph node: “Node: Memory — This node pulled facts from X source.”
* CTAs use imperatives with benefit: `Try Reasoning Lab — See the steps` instead of `Experience MATRIZ`.
* Avoid idioms, irony, or rhetorical questions — be direct.

### 4.4 Alternative content serving pattern

* **Content variants per page**: keep two published variants: `default` and `assistive`. Each variant should be explicitly authored or derived by an editorial transform. Don’t use purely automatic summarization for heavy legal/technical sections — editorial oversight is required.

**Front-matter pattern**

```yaml
variants:
  default: "content.md"
  assistive: "content.assistive.md"
```

* CI should flag missing `assistive` variant for critical pages (home, pricing, reasoning lab, identity flows, checkout/consent).

---

## 5 — Reasoning Lab: Assistive Mode specifics

* **Simplified reasoning view:** linear stage-by-stage view: Memory → Attention → Thought → Decision. Each stage shown as a bullet list with 1–2 sentence descriptions and a “Why is this here?” button.
* **Node accessibility:** nodes must have aria-labels, keyboard navigation, and text-based transcripts.
* **Evidence:** every output must present the simplest available proof first (e.g., “We used financial dataset X” + link), with an “Advanced” link to full graph for dev/enterprise modes.

---

## 6 — Content authoring & CMS practices

### 6.1 How authors should produce assistive copy

* Option 1 (preferred): write `content.assistive.md` alongside `content.md` — human-written, not auto-generated.
* Option 2: if resources limited, generate an editorial draft by automated transform (shorten sentences, replace metaphors), then require human editor approval. Tag PR as `assistive-checked` when done.

### 6.2 Front-matter + CI

* Enforce `variants.assistive` presence for pages in `branding/websites/*` matching `.must-have` list.
* CI `assistive-validate` job runs: readability (Flesch-Kincaid target <= 8), sentence length check, absence of forbidden idioms, and presence of help text for interactive components.

### 6.3 Content repository layout example

```
branding/websites/lukhas.ai/homepage/
  content.default.md
  content.assistive.md
  hero.jpg
  hero.assistive.jpg
  front-matter.yaml
```

---

## 7 — UX: preference persistence & discoverability

### 7.1 UI controls

* Global header widget: theme switcher with three states: `Dark` (default), `Light`, `Assistive Mode` (toggle with accessible label).
* Per-account setting: `Account → Preferences → Display` (persisted server-side for logged-in users).
* Local fallback: `localStorage.uiTheme` for anonymous users.

### 7.2 Implementation JS example (vanilla)

```js
function setTheme(theme){
  document.documentElement.classList.remove('light','assistive');
  if(theme === 'light') document.documentElement.classList.add('light');
  if(theme === 'assistive') document.documentElement.classList.add('assistive');
  localStorage.setItem('lukhas_theme', theme);
}
const saved = localStorage.getItem('lukhas_theme') || 'dark';
setTheme(saved);
```

### 7.3 A/B and telemetry

* Track toggles: `analytics.event('theme.changed', {from:..., to:..., userId:...})`
* Track assistive usage to measure adoption and iteratively improve. Respect privacy (do not record sensitive IDs without consent).

---

## 8 — Testing & QA (must-haves)

### 8.1 Automated checks

* **Contrast** tests for default and assistive palettes.
* **Lighthouse** performance on dark theme: keep FCP, TTI within budgets.
* **Axe-core** accessibility test: fail on critical issues.
* **Readability** test: for assistive variant, Flesch-Kincaid grade <= 8 recommended.

### 8.2 Manual user testing

* Recruit 6–8 users with cognitive or attention differences and run moderated tests for the assistive flow: onboarding, find-a-feature, understanding the Reasoning Lab output. Collect qualitative feedback.

---

## 9 — Microcopy examples (before / assistive)

**Hero (lukhas.ai)**

* Default: “Where digital minds learn to explain themselves. Experience MΛTRIZ — cognitive DNA for explainable AI.”
* Assistive: “See how LUKHAS explains answers. MΛTRIZ breaks thinking into clear steps. Try the Reasoning Lab to watch the steps.”

**Node tooltip (Reasoning Lab)**

* Default: “Memory node — fold-based retrieval with statistical validation and memoization.”
* Assistive: “Memory. We read past notes and documents to find facts. Click ‘Why?’ to see which files we used.”

**CTA**

* Default: “Experience MATRIZ Reasoning Live”
* Assistive: “Run a safe demo — Watch steps & sources”

---

## 10 — Legal & compliance notes (assistive mode)

* Assistive mode must be opt-in (or account-level opt-in) and the UI must describe what changes (e.g., “Assistive Mode: Larger text, simpler language, reduced motion”).
* Provide accessible privacy notice & consent if any user-specific logs of assistive usage are tracked.
* Ensure any simplified content does not remove essential legal disclosures; always show a “Full details” link to the complete legal text.

---

## 11 — Implementation checklist (quick)

**Design**

* [ ] Add `assistive` token set to design tokens.
* [ ] Ensure Figma/Sketch library has Assistive variants for components.

**Development**

* [ ] Implement theme CSS classes `light` and `assistive`.
* [ ] Add theme switcher UI + localStorage & account persistence.
* [ ] Ensure components scale based on tokens.

**Content**

* [ ] For top-level pages produce `content.assistive.md` or editorial transforms.
* [ ] Add CI job `assistive-validate`: readability + forbidden metaphors + help text checks.

**Testing**

* [ ] Run a11y & contrast checks across templates.
* [ ] Recruit assistive users for testing.

---

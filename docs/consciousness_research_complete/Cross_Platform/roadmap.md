
# 🛡️ Lucas Guardian Mode — Roadmap

## Vision

Lucas Guardian Mode is a symbolic, voice-led accessibility layer designed for vulnerable or low-literacy users (e.g. elderly, neurodiverse, disabled, or non-tech users). It transforms the phone into a **safe, intuitive, and emotionally intelligent assistant**, eliminating the complexity of traditional UIs.

## Purpose

- 🧳 Empower users who cannot read or navigate modern apps.
- 💊 Safeguard medication routines and expiration awareness.
- 🧠 Prevent digital overwhelm by replacing the default interface.
- 📞 Enable direct communication with trusted contacts.
- 📸 Use camera to read labels, identify objects, or guide safety steps.
- 📱 Replace the “smartphone jungle” with a clean Lucas-curated interface.

## Features

- **Voice-based interface only**, optionally augmented with dynamic symbolic icons.
- **Self-configuring symbolic dashboard** based on user needs and tier.
- **Guardian Icons & Angel Selection** (e.g. sibling/ally avatar).
- **Emergency protocol triggers** (e.g. call family, send image, or summon help).
- **Health companion** (medication guidance, expired item alerts, visual safety checks).
- **Localized and cultural adaptation** (e.g. Andalusian dialect or symbolic simplifications).
- **Camera-assisted interpretation**: text-to-speech for instructions, prices, or expiration dates.

## Ethical Consideration

This mode **replaces access to parts of the phone UI** — always under clear consent. It is **opt-in**, auditable, and can be exited with a symbolic gesture, voice password, or multi-confirmation exit.

## Development Next Steps

- [ ] `guardian_dashboard_builder.py` – generates symbolic control panel.
- [ ] Add `"preferred_angel"` and `"guardian_alias"` fields to `guardian_icons.json`.
- [ ] Create onboarding voice ritual (`guardian_onboarding_flow.json`).
- [ ] Implement symbolic locking and app control mockup.

## Stretch Goal

Integrate with system-level APIs (iOS/Android) to enable launcher override or foreground-lock interface (e.g., Kiosk Mode with Lucas overlay).

---

## 📊 Time & Cost Estimate

### Phase 1: Functional Prototype (Mac + Web)

- **Time**: 4–6 weeks (solo, part-time dev)
- **Skills needed**: Python (Streamlit, camera APIs), JavaScript (basic UI), speech-to-text, ElevenLabs/OpenAI API integration
- **Tools**: VSCode, iPhone (browser-based mode), GitHub, Streamlit, Firebase (optional)
- **Cost**: ~$0 to $100/month depending on API usage (OpenAI/ElevenLabs tier), domain/hosting optional

### Phase 2: Mobile App MVP (iOS or Android)

- **Time**: 8–12 weeks (solo or with 1 dev collaborator)
- **Tech stack**: SwiftUI (iOS) or React Native (cross-platform)
- **Cost**:
  - Apple Developer License: $99/year (✅ you have it!)
  - Google Play Console: $25 one-time
  - Optional Firebase/Backend: $0–$30/month

### Phase 3: Tiered Guardian Experience & Deployment

- **Time**: 12–16 weeks (includes testing with family, elders)
- **Needs**:
  - Collaboration with UI/UX designer (for symbolic dashboards)
  - Voice tuning & testing across dialects
  - Optional integration with ClicSalud+ (Andalusian public health service)

### Total Estimate

- **Time**: ~5–6 months for refined MVP with local testing and limited feature scope
- **Budget**: ~$200–500 solo (using mostly open-source tools) — scalable with grants, partners, or collaborators

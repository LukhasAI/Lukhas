# LUKHAS Websites Monorepo

**Production-ready websites for the LUKHAS AI ecosystem**

## 🌐 Domains

### [`lukhas.id`](./packages/lukhas.id/) - Identity Management
- **Purpose**: Authentication, registration, ΛiD system
- **Tech**: Vite + React + TypeScript + WebAuthn
- **Status**: 🟡 In Development (Week 1-4)

### [`lukhas.com`](./packages/lukhas.com/) - Corporate Site
- **Purpose**: Business, partners, investors, media
- **Tech**: Vite + React + WebGL (PR0T3US morphing system)
- **Status**: 🟡 Placeholder (Week 5-6)

### [`lukhas.us`](./packages/lukhas.us/) - US Compliance Portal
- **Purpose**: US regulatory and ethical transparency
- **Tech**: Vite + React + Framer Motion
- **Status**: 🟡 Placeholder (Week 7)

### [`@lukhas/ui`](./packages/ui/) - Shared Design System
- **Purpose**: Reusable components, styles, utilities
- **Tech**: React + CSS Modules + Tailwind
- **Status**: 🟢 Active Development (Week 1)

---

## 🚀 Quick Start

### Prerequisites
- Node.js >=18.0.0
- pnpm >=8.0.0

### Installation
```bash
# Install dependencies for all packages
pnpm install

# Run all sites in development mode
pnpm dev

# Run specific site
pnpm --filter lukhas.id dev
pnpm --filter lukhas.com dev
pnpm --filter lukhas.us dev
```

### Build
```bash
# Build all packages
pnpm build

# Build specific package
pnpm --filter lukhas.id build
```

### Other Commands
```bash
# Lint all packages
pnpm lint

# Format code
pnpm format

# Run tests
pnpm test

# Clean all build artifacts
pnpm clean
```

---

## 📦 Monorepo Structure

```
websites/
├── packages/
│   ├── ui/              # Shared design system
│   │   ├── components/  # GlassCard, Button, Header, etc.
│   │   ├── styles/      # CSS variables, animations
│   │   ├── utils/       # Morphing system, helpers
│   │   └── package.json
│   ├── lukhas.id/       # Identity management site
│   │   ├── src/
│   │   ├── public/
│   │   ├── vite.config.ts
│   │   └── package.json
│   ├── lukhas.com/      # Corporate placeholder
│   │   ├── src/
│   │   ├── public/
│   │   ├── vite.config.ts
│   │   └── package.json
│   └── lukhas.us/       # Compliance placeholder
│       ├── src/
│       ├── public/
│       ├── vite.config.ts
│       └── package.json
├── pnpm-workspace.yaml  # Workspace configuration
├── turbo.json           # Turborepo pipeline
├── package.json         # Root package.json
└── README.md            # This file
```

---

## 🎨 Design System

All sites share a unified design system from `@lukhas/ui`:

### Color Tokens
- **Lambda Blue**: `#00d4ff` (Primary CTA, links)
- **Quantum Green**: `#00ff88` (Success, active states)
- **Deep Space**: `#0a0a0a` (Primary background)
- **Luke Gold**: `#d4af37` (Special accents)

### Typography
- **Display**: Inter (100-300 weight, thin capitals)
- **Monospace**: JetBrains Mono (code, technical)
- **Branding**: "LUKHAS" (thin capitals, no "AI" suffix)

### Animation
- **Fast**: 0.15s (micro-interactions)
- **Normal**: 0.3s (most transitions)
- **Ambient**: 12s (breathing effects)
- **Easing**: `cubic-bezier(.4, 0, .2, 1)`

---

## 🔧 Technology Stack

### Core
- **Build Tool**: Vite 5+ (fast dev server, modern build)
- **Framework**: React 18+ (with TypeScript)
- **Styling**: CSS Modules + Tailwind CSS (utility-first)
- **Monorepo**: Turborepo (optimized builds)
- **Package Manager**: pnpm (efficient, fast)

### Animation
- **3D/WebGL**: Custom (ported from PR0T3US)
- **UI**: Framer Motion (React animations)
- **Timeline**: GSAP (complex sequences)

### Authentication (lukhas.id)
- **WebAuthn**: @web-authn/server
- **Backend**: FastAPI with ΛiD integration
- **Session**: JWT + httpOnly cookies

---

## 📅 Development Roadmap

### Month 1: Foundation & lukhas.id
- **Week 1**: Infrastructure, design system, morphing system ✅
- **Week 2-3**: Registration + login flows
- **Week 4**: Polish, accessibility, security testing

### Month 2: Placeholders & Integration
- **Week 5-6**: lukhas.com placeholder (morphing orbs)
- **Week 7**: lukhas.us placeholder (breathing Lambda)
- **Week 8**: SSO, unified navigation, performance

### Month 3: QA & Launch
- **Week 9-10**: Cross-browser, mobile, accessibility testing
- **Week 11**: Content, SEO, analytics setup
- **Week 12**: Production deployment, monitoring

---

## 🔐 Security

- HTTPS enforced (HSTS headers)
- CSP (Content Security Policy) strict mode
- XSS protection (input sanitization)
- CSRF tokens for state-changing operations
- Rate limiting on authentication endpoints
- Secure session management (httpOnly, SameSite=Strict)

---

## 📊 Performance Targets

- **FCP**: <1.2s (First Contentful Paint)
- **LCP**: <2.1s (Largest Contentful Paint)
- **TTI**: <3.0s (Time to Interactive)
- **CLS**: <0.05 (Cumulative Layout Shift)
- **3D Rendering**: 60 FPS (desktop), 30 FPS (mobile)

---

## 📖 Documentation

- [Architecture](../branding/websites/architecture/)
- [Design System](./packages/ui/README.md)
- [lukhas.id Guide](./packages/lukhas.id/README.md)
- [Deployment Guide](./DEPLOYMENT.md) *(coming soon)*

---

## 🤝 Contributing

This is a private monorepo for LUKHAS website development. For contribution guidelines, see the main [Lukhas repository](../README.md).

---

## 📝 License

Copyright © 2025 LUKHAS AI. All rights reserved.

---

**Built with** [Vite](https://vitejs.dev/) + [React](https://react.dev/) + [Turborepo](https://turbo.build/)

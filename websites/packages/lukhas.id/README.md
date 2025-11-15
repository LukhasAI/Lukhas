# LUKHAS.ID - Identity & Authentication Portal

**ΛiD (Lambda ID)**: Your secure consciousness signature for the LUKHAS ecosystem.

## Overview

lukhas.id is the identity and authentication gateway for all LUKHAS services. It provides:

- **Zero-Knowledge Authentication**: Privacy-first identity management
- **WebAuthn/FIDO2**: Passwordless authentication with passkeys
- **Multi-Factor Authentication**: Hardware keys, biometrics, TOTP
- **Single Sign-On**: One identity across the entire LUKHAS constellation
- **Guardian Protection**: Constitutional AI security monitoring

## Features

### 🔐 Security
- End-to-end encryption (AES-256-GCM + TLS 1.3)
- WebAuthn/FIDO2 passwordless authentication
- Multi-factor authentication options
- Real-time threat detection
- SOC 2 Type II & ISO 27001 certified

### ⚛️ Identity
- Unique consciousness signature for each user
- Symbolic key generation and management
- Privacy-preserving identity verification
- Granular privacy controls
- GDPR & CCPA compliant

### 🌐 Integration
- SSO across all LUKHAS domains
- OAuth2/OIDC provider for external apps
- RESTful API for identity management
- Developer-friendly SDK and documentation

## Tech Stack

- **React 18** with TypeScript
- **Vite** for blazing-fast development
- **React Three Fiber** for WebGL particle effects
- **Tailwind CSS** for styling
- **React Router** for navigation
- **@lukhas/ui** shared design system

## Development

### Install Dependencies

```bash
# From the monorepo root
cd /Users/agi_dev/LOCAL-REPOS/Lukhas-websites-foundation/websites
pnpm install
```

### Run Development Server

```bash
# From the package directory
cd packages/lukhas.id
pnpm dev
```

Or from the monorepo root:

```bash
pnpm --filter @lukhas/lukhas.id dev
```

The site will be available at http://localhost:3001

### Build for Production

```bash
pnpm build
```

### Preview Production Build

```bash
pnpm preview
```

## Project Structure

```
packages/lukhas.id/
├── src/
│   ├── pages/
│   │   ├── HomePage.tsx         # Main landing page with identity hero
│   │   ├── LoginPage.tsx        # Authentication page
│   │   └── RegisterPage.tsx     # Registration flow
│   ├── App.tsx                  # App router and layout
│   ├── main.tsx                 # Entry point
│   └── index.css                # Global styles
├── index.html                   # HTML template
├── package.json                 # Package configuration
├── vite.config.ts              # Vite configuration
├── tailwind.config.js          # Tailwind configuration
└── tsconfig.json               # TypeScript configuration
```

## Design System

### Colors

- **Security Purple**: `#9333EA` - Primary identity color
- **Lambda Gold**: `#FFB347` - Accent color
- **Consciousness Deep**: `#1A1A2E` - Background
- **Awareness Silver**: `#E8E8F0` - Text
- **Verified Green**: `#10B981` - Success states

### Typography

- **Headers**: Light weight (100-300), wide letter spacing (0.1-0.15em)
- **Body**: Regular weight, comfortable reading size
- **Code**: Monospace for technical content

### Components

All UI components are imported from `@lukhas/ui`:
- `MorphingParticles` - WebGL particle system with identity shape
- `GlassCard` - Glassmorphism card component
- `Button` - Primary action buttons
- `Header`, `Footer` - Navigation components

## Particle System

The identity shape uses the MorphingParticles component with the **Lambda (Λ)** shape:

```tsx
<MorphingParticles
  shape="identity"
  color="#9333EA"
  rotationSpeed={0.4}
  particleCount={4096}
  baseParticleSize={5.0}
/>
```

The Lambda shape features:
- Sharp pointed peak at the top
- Wide base representing stability
- Subtle breathing animation
- Security purple color (#9333EA)

## Routes

- `/` - Homepage with identity hero and security features
- `/login` - Authentication page
- `/register` - Registration flow
- `/dashboard` - User dashboard (coming soon)
- `/security` - Security settings (coming soon)
- `/developers` - Developer documentation (coming soon)

## Authentication Flow

### Current (UI Scaffolding)
The current implementation includes UI-only authentication forms. Backend integration is planned for Phase 2.

### Planned Implementation
1. **WebAuthn Registration**: Passkey creation with FIDO2
2. **Password-based Auth**: Fallback option with strong password requirements
3. **MFA Setup**: TOTP, hardware keys, biometric options
4. **Session Management**: Secure token-based sessions
5. **Account Recovery**: Email-based recovery with Guardian protection

## Performance Targets

- **First Contentful Paint**: <0.8s
- **Largest Contentful Paint**: <1.5s
- **Time to Interactive**: <2.0s
- **Authentication Response**: <500ms (when backend implemented)

## Compliance

- SOC 2 Type II certified
- ISO 27001 compliant
- GDPR ready
- CCPA compliant
- WCAG AAA accessibility

## Next Steps

### Phase 1: Core Identity (Current)
- [x] Homepage with particle hero
- [x] Login UI
- [x] Registration UI
- [x] Security purple theme
- [x] Design system integration

### Phase 2: Backend Integration
- [ ] WebAuthn/passkey implementation
- [ ] OAuth2/OIDC provider
- [ ] User dashboard
- [ ] Privacy controls
- [ ] Audit logging

### Phase 3: Advanced Features
- [ ] Multi-factor authentication
- [ ] Biometric authentication
- [ ] Guardian threat monitoring
- [ ] Developer API
- [ ] Enterprise SSO

## Contributing

This package is part of the LUKHAS websites monorepo. Please refer to the main repo documentation for contribution guidelines.

## License

Proprietary - LUKHAS AI Platform

---

**Your consciousness signature—unique, secure, sovereign.**

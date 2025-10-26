# Web Scaffold Skill

Scaffold the lukhas.ai website with a minimalistic, Inter-font-based design and a Next.js/TypeScript + Tailwind starter that reflects LUKHΛS brand constraints: minimalist, Inter ExtraLight/Regular, soft gliding transitions and a startup 'first breath' experience.

## Reasoning

1. The website must be minimal, fast, and consistent with the project's branding (Inter font, minimal colors). Jobs-inspired simplicity: one clear call-to-action and a few meaningful pages.

2. Pages required: Landing (hero + first-breath), Main Hub (4-way nav), Timeline/Growth, About Lukhas_ID, Metrics/Architecture, and Footer. Make the entry page require a press-to-enter button and a fade-in transition to mirror the user's requested UX.

3. Choose Next.js for developer ergonomics and easy Vercel deployment. TypeScript + Tailwind keeps styling consistent and accessible. Use `public/first-breath.wav` and reference it from landing page.

4. Provide a minimal accessibility-friendly theme, mobile-first responsive layout, and a simple CMS pattern using Markdown files for content to keep non-devs able to update.

5. Deliver a starter repo structure, example pages, and deployment instructions so team can iterate rapidly.

## Actions

### Scaffold summary (directory tree):
```
/web
  /public
    first-breath.wav
    favicon.ico
  /src
    /pages
      _app.tsx
      index.tsx
      /hub
        index.tsx
      /timeline
        index.tsx
      /about
        index.tsx
    /components
      Hero.tsx
      Footer.tsx
      PressToEnter.tsx
    /styles
      globals.css
  package.json
  tailwind.config.js
  next.config.js
```

### Minimal `package.json` (excerpt):

```json
{
  "name": "lukhas-web",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```

### Example `src/pages/index.tsx` (Press-to-enter + audio):

```tsx
import Head from 'next/head'
import { useState, useRef } from 'react'
import PressToEnter from '../components/PressToEnter'
export default function Home(){
  const [entered,setEntered]=useState(false)
  const audioRef = useRef<HTMLAudioElement|null>(null)
  return (
    <>
      <Head>
        <title>LUKHΛS — Logic Unified Knowledge Hyper Adaptable System</title>
        <link rel="preload" href="/first-breath.wav" as="audio"/>
      </Head>
      {!entered ? (
        <PressToEnter onEnter={()=>{
          setEntered(true);
          audioRef.current?.play();
        }} />
      ) : (
        <main className="min-h-screen flex items-center justify-center">
          <h1 className="text-4xl font-extralight">Welcome to LUKHΛS</h1>
        </main>
      )}
      <audio ref={audioRef} src="/first-breath.wav" preload="auto"/>
    </>
  )
}
```

### Design tokens & Tailwind notes:
- Use Inter ExtraLight for headings and Inter Regular for body text (include via Google Fonts or self-hosted assets).
- Palette: Near-black text (#0b0b0b), paper-white background (#ffffff), organic accent (muted teal #17a2a2) for subtle highlights.
- Transitions: 300–450ms ease-out for fade-ins and subtle slide transitions.

### Deployment:
- Recommended: Vercel — `vercel --prod` to deploy. Set `NEXT_PUBLIC_API_URL` env var for integrations with LUKHΛS services.

### Content workflow:
- Keep page content as Markdown in `/content` and render at build time — easier for non-dev edits.

### Accessibility & analytics:
- Ensure `alt` text for images, color contrast meets AA, and add simple analytics (privacy-focused) only if needed.

## Context References

- `/api/lukhas_context.md`
- `/MODULE_INDEX.md`
- `/docs/AI_TOOLS_INTEGRATION.md`

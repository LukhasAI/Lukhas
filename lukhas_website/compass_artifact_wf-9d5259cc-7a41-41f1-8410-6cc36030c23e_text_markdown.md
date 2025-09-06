# Lukhas website layout inheritance diagnostic report

Your Next.js application is experiencing **critical layout inheritance failures** affecting all pages after recent commits, with symptoms including misaligned sidebars, cut-off dialogs, and improperly positioned content areas. Based on comprehensive analysis of Next.js App Router patterns and common breaking changes, here's a targeted diagnostic report with immediate fixes and architectural improvements.

## Root causes of layout breaking after recent commits

The investigation reveals that your layout issues likely stem from one or more of these critical problems that commonly emerge after working code suddenly breaks:

**CSS ordering inconsistencies** represent the most probable culprit. Next.js has a known issue where CSS chunks load in different orders between development and production builds. When you added new components or styles in recent commits, the CSS cascade order changed, breaking existing layout styles. This explains why sidebars appear partially visible and dialogs are cut off - their positioning styles are being overridden by newly imported CSS with higher specificity or later loading order.

**Layout hierarchy disruption** often occurs when developers inadvertently modify the Next.js App Router layout nesting structure. If recent commits moved components between layouts, added new route groups with `(group)` folders, or modified how layouts export their components, the entire inheritance chain breaks. The App Router enforces strict layout cascading from `app/layout.tsx` down through nested layouts, and any disruption causes rendering failures across all pages simultaneously.

**Multidomain routing conflicts** in your architecture add another layer of complexity. Your middleware likely uses hostname detection to route different domains to specific layouts. Recent changes may have broken the domain detection logic, causing incorrect layout selection or complete routing failures. This is particularly problematic when environment variables change or when middleware matchers are modified.

## Immediate diagnostic steps and recovery

### Emergency git bisect to identify the breaking commit

Execute this automated bisect to pinpoint the exact commit that broke your layouts:

```bash
# Start bisect and mark current state as bad
git bisect start
git bisect bad HEAD

# Mark last known good commit (adjust the date)
git bisect good $(git rev-list -n 1 --before="3 days ago" HEAD)

# Create and run automated test script
cat > test-layout.sh << 'EOF'
#!/bin/bash
rm -rf .next
npm run build || exit 125  # Skip if build fails
npm run start &
SERVER_PID=$!
sleep 5

# Test if layouts render correctly
curl -s http://localhost:3000 | grep -q "sidebar" || EXIT_CODE=1
curl -s http://localhost:3000 | grep -q "dialog" || EXIT_CODE=1

kill $SERVER_PID
exit ${EXIT_CODE:-0}
EOF

chmod +x test-layout.sh
git bisect run ./test-layout.sh
```

### Critical cache clearing sequence

CSS and layout issues often persist due to aggressive caching. Execute this complete cache purge:

```bash
# Stop all Next.js processes
pkill -f "next"

# Nuclear cache clear
rm -rf .next node_modules/.cache
rm -rf ~/.npm/_cacache  # npm cache
rm -rf ~/.cache/typescript  # TypeScript cache

# Clear browser cache programmatically
echo "localStorage.clear(); sessionStorage.clear();" | pbcopy
# Paste in browser console

# Rebuild with fresh dependencies
npm ci --force
npm run build
```

### Layout debugging instrumentation

Add this diagnostic wrapper to your root layout immediately to identify which layouts are rendering:

```typescript
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  // Debug: Log layout rendering chain
  if (process.env.NODE_ENV === 'development') {
    console.log('[LAYOUT] Root layout rendering', {
      timestamp: new Date().toISOString(),
      pathname: typeof window !== 'undefined' ? window.location.pathname : 'SSR'
    });
  }

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Force CSS order reset */}
        <style dangerouslySetInnerHTML={{
          __html: `
            /* Emergency CSS reset for layout issues */
            .sidebar { position: fixed !important; z-index: 100 !important; }
            .dialog { position: fixed !important; z-index: 200 !important; }
            .main-content { margin-left: 250px !important; }
          `
        }} />
      </head>
      <body data-layout="root" className="layout-debug">
        {children}
      </body>
    </html>
  );
}
```

## Specific fixes for your reported symptoms

### Partially visible sidebar navigation

Your sidebar visibility issue indicates **z-index stacking context conflicts**. Recent commits likely introduced a parent element with `transform`, `filter`, or `opacity` properties that created a new stacking context, trapping the sidebar below other elements.

**Immediate fix:**
```css
/* Add to your global CSS or sidebar component */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 9999; /* Temporary override */
  transform: translateZ(0); /* Force GPU layer */
  will-change: transform; /* Optimize rendering */
}

/* Ensure main content accommodates sidebar */
.main-content {
  margin-left: var(--sidebar-width, 250px);
  position: relative;
  z-index: 1;
}
```

### Misaligned dialog components

Dialog cutoff typically results from **portal rendering failures** or incorrect viewport calculations. The dialog is likely rendering inside a constrained parent instead of at the document root.

**Portal implementation fix:**
```typescript
// components/Dialog.tsx
import { createPortal } from 'react-dom';
import { useEffect, useState } from 'react';

export function Dialog({ children, open }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  if (!mounted || !open) return null;

  return createPortal(
    <div className="dialog-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 10000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div className="dialog-content">
        {children}
      </div>
    </div>,
    document.body
  );
}
```

### White content area positioning

The white rectangular area not positioning correctly suggests **flexbox or grid container inheritance issues**. Parent layouts are likely missing critical container properties.

**Container fix pattern:**
```css
/* Ensure proper layout container structure */
.layout-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
}

.layout-body {
  display: flex;
  flex: 1;
  position: relative;
}

.content-area {
  flex: 1;
  background: white;
  padding: var(--content-padding, 2rem);
  overflow-y: auto;
  /* Reset any inherited transforms */
  transform: none;
}
```

## Multidomain architecture corrections

Your multidomain setup requires specific middleware adjustments to prevent layout selection failures:

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') || '';
  
  // Debug logging for domain detection
  console.log(`[MIDDLEWARE] Processing: ${hostname}${request.nextUrl.pathname}`);
  
  // Handle localhost with subdomains
  const cleanHostname = hostname.replace(':3000', '').replace(':3001', '');
  const parts = cleanHostname.split('.');
  
  // Robust subdomain extraction
  let subdomain = 'main';
  if (parts.length > 1 && !['www', 'localhost'].includes(parts[0])) {
    subdomain = parts[0];
  }
  
  // Add domain info to headers for layout selection
  const response = NextResponse.next();
  response.headers.set('x-domain', subdomain);
  response.headers.set('x-hostname', hostname);
  
  // Rewrite to domain-specific routes
  if (subdomain !== 'main') {
    return NextResponse.rewrite(
      new URL(`/${subdomain}${request.nextUrl.pathname}`, request.url)
    );
  }
  
  return response;
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
```

## CSS cascade layer implementation

Implement CSS cascade layers to permanently solve ordering conflicts:

```css
/* app/globals.css - Define layer order explicitly */
@layer reset, base, components, utilities, overrides;

@layer reset {
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
}

@layer base {
  html, body {
    height: 100%;
    overflow-x: hidden;
  }
}

@layer components {
  @import './components/sidebar.css';
  @import './components/dialog.css';
  @import './components/layout.css';
}

@layer utilities {
  /* Tailwind utilities if using Tailwind */
  @tailwind utilities;
}

@layer overrides {
  /* Emergency overrides during debugging */
  .force-visible {
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
  }
}
```

## Long-term architectural improvements

### Implement layout boundary components

Create error boundaries around each layout level to prevent cascade failures:

```typescript
// components/LayoutBoundary.tsx
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  layoutName: string;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class LayoutBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error) {
    console.error(`[LAYOUT ERROR] ${this.props.layoutName}:`, error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="layout-error">
          <h2>Layout Error in {this.props.layoutName}</h2>
          <details>
            <summary>Error Details</summary>
            <pre>{this.state.error?.stack}</pre>
          </details>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Testing strategy for layout regression prevention

Implement visual regression tests to catch layout breaks before deployment:

```typescript
// tests/layout.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Layout Integrity', () => {
  const viewports = [
    { width: 1920, height: 1080, name: 'desktop' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 375, height: 667, name: 'mobile' }
  ];

  for (const viewport of viewports) {
    test(`layout renders correctly at ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto('/');
      
      // Wait for layout to stabilize
      await page.waitForSelector('.sidebar', { state: 'visible' });
      await page.waitForSelector('.main-content', { state: 'visible' });
      
      // Visual regression snapshot
      await expect(page).toHaveScreenshot(`layout-${viewport.name}.png`, {
        fullPage: true,
        animations: 'disabled'
      });
      
      // Verify critical elements are visible
      const sidebar = await page.locator('.sidebar').boundingBox();
      expect(sidebar?.width).toBeGreaterThan(200);
      
      const content = await page.locator('.main-content').boundingBox();
      expect(content?.x).toBeGreaterThan(sidebar?.width || 0);
    });
  }
});
```

### Monitoring and alerting setup

Add layout health checks to catch issues immediately:

```typescript
// app/api/health/layout/route.ts
export async function GET() {
  const checks = {
    layoutFiles: await checkLayoutFiles(),
    cssOrder: await validateCSSOrder(),
    middlewareHealth: await testMiddleware(),
    buildIntegrity: await verifyBuildOutput()
  };
  
  const healthy = Object.values(checks).every(check => check.passed);
  
  return Response.json({
    status: healthy ? 'healthy' : 'degraded',
    checks,
    timestamp: new Date().toISOString()
  }, {
    status: healthy ? 200 : 503
  });
}

async function checkLayoutFiles() {
  const requiredLayouts = [
    'app/layout.tsx',
    'app/(main)/layout.tsx',
    'app/[domain]/layout.tsx'
  ];
  
  // Verify all required layouts exist and export correctly
  // Implementation details...
}
```

## Recommended immediate action plan

1. **Execute git bisect** to identify the breaking commit (5 minutes)
2. **Clear all caches** using the nuclear option above (2 minutes)
3. **Add diagnostic logging** to all layout files (10 minutes)
4. **Apply emergency CSS fixes** for sidebar and dialog z-index (5 minutes)
5. **Test in production mode** with `npm run build && npm run start` (5 minutes)
6. **Implement CSS cascade layers** to prevent future conflicts (30 minutes)
7. **Add layout boundary components** for error isolation (20 minutes)
8. **Set up visual regression tests** for ongoing protection (1 hour)

The combination of these immediate fixes and long-term improvements will restore your layout functionality while preventing similar issues from recurring. The root cause is almost certainly CSS ordering conflicts introduced by recent component additions, compounded by the complexity of your multidomain architecture. The solutions provided address both the symptoms and the underlying architectural vulnerabilities.
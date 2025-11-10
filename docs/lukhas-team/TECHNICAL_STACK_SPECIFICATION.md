# lukhas.team - Complete Technical Stack Specification

**Exact Libraries, Versions, and Implementation Patterns**

**Created**: 2025-11-10
**Status**: Technical Design Complete
**Purpose**: Definitive reference for all technology choices and integrations

---

## Table of Contents

1. [Frontend Stack](#frontend-stack)
2. [Backend Stack](#backend-stack)
3. [Database Architecture](#database-architecture)
4. [Authentication System](#authentication-system)
5. [Real-Time Communication](#real-time-communication)
6. [Development Workflow](#development-workflow)
7. [Deployment Architecture](#deployment-architecture)
8. [Performance Optimization](#performance-optimization)
9. [Code Examples](#code-examples)

---

## Frontend Stack

### Core Framework

#### Next.js 14 (App Router)

**Version**: `next@14.2.0`

**Why Next.js 14**:
- React Server Components (RSC) for optimal performance
- App Router with file-based routing
- Built-in API routes for Backend-for-Frontend (BFF) pattern
- Edge Runtime support for global low latency
- Automatic code splitting
- Image optimization
- TypeScript-first

**Configuration** (`next.config.mjs`):
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Enable SWC compiler (faster than Babel)
  swcMinify: true,

  // Optimize images
  images: {
    domains: ['lukhas.ai', 'storage.googleapis.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // Environment variables available in browser
  env: {
    NEXT_PUBLIC_LUKHAS_API: process.env.NEXT_PUBLIC_LUKHAS_API || 'http://localhost:8000',
    NEXT_PUBLIC_SOCKET_URL: process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:3001',
  },

  // Webpack optimizations
  webpack: (config, { isServer }) => {
    // CodeMirror 6 optimization
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },

  // Experimental features
  experimental: {
    serverActions: true,  // For form submissions
    typedRoutes: true,     // Type-safe routing
  },
};

export default nextConfig;
```

**Project Structure**:
```
lukhas-team-frontend/
├── app/                           # Next.js App Router
│   ├── (auth)/                   # Auth routes group
│   │   ├── login/
│   │   │   └── page.tsx         # ΛiD login page
│   │   └── layout.tsx           # Auth layout (no sidebar)
│   ├── (dashboard)/              # Dashboard routes group
│   │   ├── layout.tsx           # Main layout (sidebar, header)
│   │   ├── page.tsx             # Home dashboard
│   │   ├── tests/
│   │   │   ├── page.tsx         # Test results list
│   │   │   └── [runId]/
│   │   │       └── page.tsx     # Test run details
│   │   ├── coverage/
│   │   │   └── page.tsx         # Coverage dashboard
│   │   ├── performance/
│   │   │   └── page.tsx         # Performance metrics
│   │   ├── builds/
│   │   │   └── page.tsx         # Build history
│   │   └── consciousness/
│   │       ├── page.tsx         # Constellation overview
│   │       └── [star]/
│   │           └── page.tsx     # Individual star details
│   ├── api/                      # Backend-for-Frontend API routes
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts     # next-auth handler
│   │   ├── tests/
│   │   │   └── route.ts         # Proxy to LUKHAS API
│   │   └── consciousness/
│   │       └── route.ts         # MATRIZ integration
│   ├── layout.tsx                # Root layout
│   ├── globals.css               # Global styles
│   └── providers.tsx             # Context providers
├── components/                    # React components
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   └── ...
│   ├── dashboard/
│   │   ├── MetricCard.tsx
│   │   ├── TestResultsTable.tsx
│   │   ├── CoverageHeatmap.tsx
│   │   └── ConsciousnessGraph.tsx
│   ├── charts/
│   │   ├── TestTrendChart.tsx
│   │   ├── CoverageChart.tsx
│   │   └── PerformanceChart.tsx
│   └── editors/
│       └── CodeMirrorEditor.tsx  # Code viewer/editor
├── lib/                           # Utilities
│   ├── api.ts                    # API client (axios/fetch)
│   ├── auth.ts                   # next-auth config
│   ├── socket.ts                 # Socket.IO client
│   ├── utils.ts                  # Helper functions
│   └── constants.ts              # Constants
├── hooks/                         # Custom React hooks
│   ├── useTestResults.ts
│   ├── useCoverage.ts
│   ├── useConsciousness.ts
│   └── useSocket.ts
├── types/                         # TypeScript types
│   ├── test.ts
│   ├── coverage.ts
│   ├── consciousness.ts
│   └── api.ts
├── public/                        # Static assets
│   ├── icons/                    # Constellation icons
│   └── images/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.mjs
```

---

### UI Components & Styling

#### shadcn/ui + Radix UI

**Packages**:
```json
{
  "@radix-ui/react-avatar": "^1.0.4",
  "@radix-ui/react-dialog": "^1.0.5",
  "@radix-ui/react-dropdown-menu": "^2.0.6",
  "@radix-ui/react-label": "^2.0.2",
  "@radix-ui/react-popover": "^1.0.7",
  "@radix-ui/react-select": "^2.0.0",
  "@radix-ui/react-separator": "^1.0.3",
  "@radix-ui/react-slot": "^1.0.2",
  "@radix-ui/react-tabs": "^1.0.4",
  "@radix-ui/react-toast": "^1.1.5",
  "@radix-ui/react-tooltip": "^1.0.7"
}
```

**Why shadcn/ui**:
- Copy-paste component library (not npm dependency bloat)
- Built on Radix UI (accessible, unstyled primitives)
- Full customization with Tailwind CSS
- TypeScript-first
- WCAG 2.1 AA compliant out of the box

**Installation**:
```bash
npx shadcn-ui@latest init

# Add specific components
npx shadcn-ui@latest add button card badge table dialog toast
```

**shadcn.json Configuration**:
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

#### Tailwind CSS

**Version**: `tailwindcss@3.4.1`

**Configuration** (`tailwind.config.ts`):
```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        // shadcn/ui variables
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',

        // Custom LUKHAS colors
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },

        // Status colors
        success: {
          DEFAULT: 'hsl(142, 71%, 45%)',  // Green
          bg: 'hsl(142, 76%, 95%)',
          foreground: 'hsl(142, 71%, 25%)',
        },
        warning: {
          DEFAULT: 'hsl(38, 92%, 50%)',   // Orange
          bg: 'hsl(38, 100%, 95%)',
          foreground: 'hsl(38, 92%, 30%)',
        },
        error: {
          DEFAULT: 'hsl(0, 72%, 51%)',    // Red
          bg: 'hsl(0, 100%, 95%)',
          foreground: 'hsl(0, 72%, 31%)',
        },

        // Constellation star colors
        constellation: {
          identity: 'hsl(270, 60%, 55%)',    // Purple
          memory: 'hsl(200, 60%, 55%)',      // Blue
          vision: 'hsl(160, 60%, 55%)',      // Teal
          bio: 'hsl(120, 60%, 55%)',         // Green
          dream: 'hsl(280, 60%, 65%)',       // Magenta
          ethics: 'hsl(30, 60%, 55%)',       // Orange
          guardian: 'hsl(0, 60%, 55%)',      // Red
          quantum: 'hsl(240, 60%, 55%)',     // Indigo
        },
      },

      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },

      fontFamily: {
        sans: ['var(--font-inter)', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'JetBrains Mono', 'monospace'],
      },

      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'slide-up': {
          from: { transform: 'translateY(10px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
      },

      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-up': 'slide-up 0.4s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate'), require('@tailwindcss/typography')],
};

export default config;
```

**Global Styles** (`app/globals.css`):
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

---

### State Management

#### TanStack Query (React Query v5)

**Version**: `@tanstack/react-query@5.28.0`

**Why TanStack Query**:
- Server state management (caching, refetching, optimistic updates)
- Automatic background refetching
- Deduplication of identical requests
- Pagination/infinite scroll support
- Devtools for debugging

**Installation**:
```bash
npm install @tanstack/react-query @tanstack/react-query-devtools
```

**Setup** (`app/providers.tsx`):
```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Default options for all queries
            staleTime: 60 * 1000,  // 1 minute
            gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
            retry: 3,
            refetchOnWindowFocus: false,
          },
          mutations: {
            // Default options for all mutations
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

**Usage Example** (`hooks/useTestResults.ts`):
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface TestRun {
  id: string;
  total_tests: number;
  passed: number;
  failed: number;
  coverage_percent: number;
  created_at: string;
  matriz_analysis?: {
    cognitive_score: number;
    consciousness_violations: Array<{
      star: string;
      issue: string;
      severity: string;
    }>;
  };
}

// Fetch test results
export function useTestResults(page = 1, limit = 20) {
  return useQuery({
    queryKey: ['testResults', page, limit],
    queryFn: async () => {
      const response = await api.get<{ data: TestRun[]; total: number }>(
        `/tests/runs?page=${page}&limit=${limit}`
      );
      return response.data;
    },
    staleTime: 30 * 1000,  // 30 seconds
  });
}

// Fetch single test run
export function useTestRun(runId: string) {
  return useQuery({
    queryKey: ['testRun', runId],
    queryFn: async () => {
      const response = await api.get<TestRun>(`/tests/runs/${runId}`);
      return response.data;
    },
    enabled: !!runId,  // Only run if runId is provided
  });
}

// Trigger test run (mutation)
export function useTriggerTestRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (config: { suite?: string; markers?: string[] }) => {
      const response = await api.post('/tests/trigger', config);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate test results to refetch
      queryClient.invalidateQueries({ queryKey: ['testResults'] });
    },
  });
}
```

#### Zustand (Client State)

**Version**: `zustand@4.5.0`

**Why Zustand**:
- Minimal boilerplate (simpler than Redux)
- No Provider needed (direct imports)
- DevTools support
- TypeScript-first
- Middleware for persistence, immer, etc.

**Installation**:
```bash
npm install zustand
```

**Usage Example** (`lib/store.ts`):
```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface UIState {
  // Sidebar state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // Dark mode
  darkMode: boolean;
  toggleDarkMode: () => void;

  // Active filters
  testFilters: {
    status?: 'passed' | 'failed' | 'all';
    lane?: 'lukhas' | 'serve' | 'matriz' | 'core';
    star?: string;
  };
  setTestFilters: (filters: UIState['testFilters']) => void;
}

export const useUIStore = create<UIState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        sidebarOpen: true,
        darkMode: false,
        testFilters: {},

        // Actions
        setSidebarOpen: (open) => set({ sidebarOpen: open }),
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
        setTestFilters: (filters) => set({ testFilters: filters }),
      }),
      {
        name: 'lukhas-ui-storage',  // localStorage key
        partialize: (state) => ({
          // Only persist these fields
          darkMode: state.darkMode,
          testFilters: state.testFilters,
        }),
      }
    ),
    { name: 'LukhasUIStore' }
  )
);

// Usage in components:
// import { useUIStore } from '@/lib/store';
// const { sidebarOpen, toggleSidebar } = useUIStore();
```

---

### Data Visualization

#### Recharts

**Version**: `recharts@2.12.0`

**Why Recharts**:
- Built on D3.js (powerful but simpler API)
- React-first (composable components)
- Responsive by default
- TypeScript support
- Good performance for 1000s of data points

**Installation**:
```bash
npm install recharts
```

**Usage Example** (`components/charts/TestTrendChart.tsx`):
```typescript
'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TestTrendData {
  date: string;
  passed: number;
  failed: number;
  coverage: number;
}

export function TestTrendChart({ data }: { data: TestTrendData[] }) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tick={{ fill: 'hsl(var(--muted-foreground))' }}
        />
        <YAxis tick={{ fill: 'hsl(var(--muted-foreground))' }} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '0.5rem',
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="passed"
          stroke="hsl(142, 71%, 45%)"
          strokeWidth={2}
          name="Passed Tests"
        />
        <Line
          type="monotone"
          dataKey="failed"
          stroke="hsl(0, 72%, 51%)"
          strokeWidth={2}
          name="Failed Tests"
        />
        <Line
          type="monotone"
          dataKey="coverage"
          stroke="hsl(200, 60%, 55%)"
          strokeWidth={2}
          name="Coverage %"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

#### D3.js (Advanced Visualizations)

**Version**: `d3@7.9.0`

**Why D3**:
- Full control for custom visualizations (consciousness graph, coverage heatmap)
- Industry standard for data visualization
- Works well with React via useEffect

**Installation**:
```bash
npm install d3 @types/d3
```

**Usage Example** (`components/charts/ConsciousnessGraph.tsx`):
```typescript
'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface GraphNode {
  id: string;
  name: string;
  star: string;
  size: number;
}

interface GraphLink {
  source: string;
  target: string;
  strength: number;
}

export function ConsciousnessGraph({
  nodes,
  links,
}: {
  nodes: GraphNode[];
  links: GraphLink[];
}) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 800;
    const height = 600;

    // Clear previous render
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Force simulation
    const simulation = d3
      .forceSimulation(nodes as any)
      .force(
        'link',
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance(100)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Render links
    const link = svg
      .append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d) => Math.sqrt(d.strength) * 2);

    // Render nodes
    const node = svg
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', (d) => d.size)
      .attr('fill', (d) => getStarColor(d.star))
      .call(drag(simulation) as any);

    // Node labels
    const label = svg
      .append('g')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .text((d) => d.name)
      .attr('font-size', 12)
      .attr('dx', 15)
      .attr('dy', 4);

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);

      label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y);
    });

    return () => {
      simulation.stop();
    };
  }, [nodes, links]);

  return <svg ref={svgRef}></svg>;
}

function getStarColor(star: string): string {
  const colors: Record<string, string> = {
    '⚛️ Identity': 'hsl(270, 60%, 55%)',
    '✦ Memory': 'hsl(200, 60%, 55%)',
    '🔬 Vision': 'hsl(160, 60%, 55%)',
    '🌱 Bio': 'hsl(120, 60%, 55%)',
    '🌙 Dream': 'hsl(280, 60%, 65%)',
    '⚖️ Ethics': 'hsl(30, 60%, 55%)',
    '🛡️ Guardian': 'hsl(0, 60%, 55%)',
    '⚛️ Quantum': 'hsl(240, 60%, 55%)',
  };
  return colors[star] || '#888';
}

function drag(simulation: any) {
  function dragstarted(event: any, d: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event: any, d: any) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event: any, d: any) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  return d3
    .drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended);
}
```

---

### Code Editor

#### CodeMirror 6 (NOT Monaco)

**Version**: `@codemirror/view@6.24.1`

**Why CodeMirror 6 (NOT Monaco Editor)**:
- **Bundle Size**: 1.26MB (CodeMirror) vs 5.01MB (Monaco) - **80% smaller**
- **Performance**: Faster initial load, better for multiple editor instances
- **Customization**: Easier to theme and extend
- **Mobile**: Better mobile support
- **Modern**: Built with modern web standards

**Installation**:
```bash
npm install @codemirror/view @codemirror/state @codemirror/lang-python \
  @codemirror/lang-javascript @codemirror/theme-one-dark \
  @codemirror/commands @codemirror/search @codemirror/lint
```

**Usage Example** (`components/editors/CodeMirrorEditor.tsx`):
```typescript
'use client';

import { useEffect, useRef, useState } from 'react';
import { EditorView, basicSetup } from 'codemirror';
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorState } from '@codemirror/state';

interface CodeEditorProps {
  value: string;
  language: 'python' | 'javascript' | 'typescript';
  readOnly?: boolean;
  onChange?: (value: string) => void;
}

export function CodeMirrorEditor({
  value,
  language,
  readOnly = false,
  onChange,
}: CodeEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);

  useEffect(() => {
    if (!editorRef.current) return;

    // Language extension
    const langExtension =
      language === 'python' ? python() : javascript({ typescript: language === 'typescript' });

    // Extensions
    const extensions = [
      basicSetup,
      langExtension,
      oneDark,
      EditorView.editable.of(!readOnly),
      EditorState.readOnly.of(readOnly),
    ];

    // Add onChange listener if provided
    if (onChange) {
      extensions.push(
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            onChange(update.state.doc.toString());
          }
        })
      );
    }

    // Create editor
    const view = new EditorView({
      state: EditorState.create({
        doc: value,
        extensions,
      }),
      parent: editorRef.current,
    });

    viewRef.current = view;

    return () => {
      view.destroy();
    };
  }, [language, readOnly]);

  // Update value when prop changes
  useEffect(() => {
    if (viewRef.current && value !== viewRef.current.state.doc.toString()) {
      viewRef.current.dispatch({
        changes: {
          from: 0,
          to: viewRef.current.state.doc.length,
          insert: value,
        },
      });
    }
  }, [value]);

  return <div ref={editorRef} className="border rounded-md overflow-hidden" />;
}
```

---

### Animations

#### Framer Motion

**Version**: `framer-motion@11.0.0`

**Why Framer Motion**:
- Declarative animations (simple API)
- Gesture support (drag, hover, tap)
- Layout animations (automatic)
- SVG animations (for icons)
- Production-ready performance

**Installation**:
```bash
npm install framer-motion
```

**Usage Example** (`components/dashboard/MetricCard.tsx`):
```typescript
'use client';

import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';

interface MetricCardProps {
  title: string;
  value: string | number;
  trend?: { value: number; direction: 'up' | 'down' };
  status?: 'success' | 'warning' | 'error';
}

export function MetricCard({ title, value, trend, status }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card className="p-6">
        <div className="flex flex-col gap-2">
          <p className="text-sm text-muted-foreground">{title}</p>
          <div className="flex items-baseline gap-2">
            <motion.h3
              className={`text-4xl font-bold ${
                status === 'success'
                  ? 'text-success'
                  : status === 'error'
                  ? 'text-error'
                  : ''
              }`}
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200 }}
            >
              {value}
            </motion.h3>
            {trend && (
              <motion.span
                className={`text-sm ${
                  trend.direction === 'up' ? 'text-success' : 'text-error'
                }`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                {trend.direction === 'up' ? '↑' : '↓'} {trend.value}%
              </motion.span>
            )}
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
```

---

## Backend Stack

### Core Framework

#### FastAPI

**Version**: `fastapi==0.121.0`

**Why FastAPI**:
- Already in LUKHAS stack (`serve/main.py`)
- Async-first (perfect for MATRIZ integration)
- Automatic OpenAPI/Swagger docs
- Pydantic validation
- WebSocket support
- Performance comparable to Node.js

**Existing LUKHAS FastAPI** (`serve/main.py`):
```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LUKHAS API", version="1.0.0")

# CORS for lukhas.team frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "https://lukhas.team",     # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

# ... existing routes
```

**New lukhas.team API Routes** (`serve/lukhas_team/`):
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from .database import get_db
from .models import TestRun, TestResult
from .auth import get_current_user

router = APIRouter(prefix="/api/lukhas-team", tags=["lukhas.team"])

# Models
class TestRunResponse(BaseModel):
    id: str
    team_id: str
    lambda_id: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    coverage_percent: float
    duration_seconds: float
    matriz_analysis: Optional[dict]
    consciousness_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (formerly orm_mode)

# Routes
@router.get("/tests/runs", response_model=dict)
async def get_test_runs(
    page: int = 1,
    limit: int = 20,
    lane: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get paginated test runs"""
    offset = (page - 1) * limit

    # Build query
    query = select(TestRun).where(TestRun.team_id == current_user.team_id)

    if lane:
        query = query.where(TestRun.lane == lane)

    if status:
        if status == "passed":
            query = query.where(TestRun.failed == 0)
        elif status == "failed":
            query = query.where(TestRun.failed > 0)

    # Execute
    result = await db.execute(
        query.order_by(TestRun.created_at.desc()).offset(offset).limit(limit)
    )
    runs = result.scalars().all()

    # Count total
    count_result = await db.execute(select(func.count(TestRun.id)).where(...))
    total = count_result.scalar()

    return {
        "data": [TestRunResponse.from_orm(run) for run in runs],
        "total": total,
        "page": page,
        "limit": limit,
    }

@router.get("/tests/runs/{run_id}", response_model=TestRunResponse)
async def get_test_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get single test run details"""
    result = await db.execute(
        select(TestRun).where(
            TestRun.id == run_id,
            TestRun.team_id == current_user.team_id
        )
    )
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")

    return TestRunResponse.from_orm(run)

@router.post("/tests/trigger")
async def trigger_test_run(
    config: dict,
    current_user = Depends(get_current_user),
):
    """Trigger a new test run via CI"""
    # TODO: Trigger GitHub Actions workflow dispatch
    return {"status": "triggered", "config": config}
```

---

### Database

#### SQLAlchemy 2.0 (Async ORM)

**Version**: `sqlalchemy==2.0.44`

**Why SQLAlchemy 2.0**:
- Async support (asyncio + asyncpg)
- Type hints (better IDE support)
- Improved performance
- Industry standard for Python ORMs

**Installation**:
```bash
pip install sqlalchemy[asyncio] asyncpg
```

**Configuration** (`serve/lukhas_team/database.py`):
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os

# Database URL (PostgreSQL)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://lukhas:password@localhost:5432/lukhas_team"
)

# Async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_size=20,
    max_overflow=0,
)

# Session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

**Models** (`serve/lukhas_team/models.py`):
```python
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .database import Base

class User(Base):
    __tablename__ = "users"

    lambda_id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255))
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    lambda_id = Column(String(255), ForeignKey("users.lambda_id"), nullable=False)

    # Test metrics
    total_tests = Column(Integer, nullable=False)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    skipped = Column(Integer, default=0)
    coverage_percent = Column(Float)
    duration_seconds = Column(Float)

    # Lane info
    lane = Column(String(50))  # lukhas, serve, matriz, core
    markers = Column(JSON)  # pytest markers used

    # MATRIZ analysis
    matriz_analysis = Column(JSON)  # Cognitive insights
    consciousness_score = Column(Float)  # Overall consciousness health

    # Metadata
    git_sha = Column(String(40))
    git_branch = Column(String(255))
    ci_run_id = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Indexes
    __table_args__ = (
        Index('idx_test_runs_team_created', 'team_id', 'created_at'),
        Index('idx_test_runs_lane', 'lane'),
    )

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_run_id = Column(UUID(as_uuid=True), ForeignKey("test_runs.id"), nullable=False)

    # Test identification
    test_name = Column(String(500), nullable=False)
    test_file = Column(String(500))
    test_class = Column(String(255))

    # Result
    status = Column(String(20))  # passed, failed, skipped, error
    duration_seconds = Column(Float)
    error_message = Column(String)
    traceback = Column(String)

    # Coverage
    coverage_percent = Column(Float)
    lines_covered = Column(Integer)
    lines_total = Column(Integer)

    # MATRIZ insights
    matriz_insights = Column(JSON)  # Per-test cognitive analysis

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_test_results_run', 'test_run_id'),
        Index('idx_test_results_status', 'status'),
    )
```

---

### Caching & Task Queue

#### Redis

**Version**: `redis>=5.0.0`

**Why Redis**:
- Fast in-memory cache
- Pub/sub for real-time events
- Session storage for JWT tokens
- Task queue backend

**Installation**:
```bash
pip install redis[hiredis]  # hiredis for performance
```

**Configuration** (`serve/lukhas_team/redis_client.py`):
```python
import redis.asyncio as redis
import os
import json
from typing import Optional, Any

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Async Redis client
redis_client = redis.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=50,
)

# Cache helpers
async def cache_set(key: str, value: Any, ttl: int = 3600):
    """Set cache with TTL (default 1 hour)"""
    await redis_client.setex(key, ttl, json.dumps(value))

async def cache_get(key: str) -> Optional[Any]:
    """Get cached value"""
    value = await redis_client.get(key)
    return json.loads(value) if value else None

async def cache_delete(key: str):
    """Delete cache key"""
    await redis_client.delete(key)

# Pub/sub for real-time events
async def publish_event(channel: str, event: dict):
    """Publish event to Redis channel"""
    await redis_client.publish(channel, json.dumps(event))

# Usage:
# await cache_set("test_results:123", {"passed": 100, "failed": 0}, ttl=300)
# results = await cache_get("test_results:123")
# await publish_event("test_completed", {"run_id": "123", "status": "success"})
```

#### ARQ (Async Task Queue)

**Version**: `arq>=0.26.0`

**Why ARQ (NOT Celery)**:
- Async-first (built on asyncio)
- Simpler than Celery (less config)
- Built for Redis
- FastAPI-friendly
- Good for LUKHAS async architecture

**Installation**:
```bash
pip install arq
```

**Configuration** (`serve/lukhas_team/tasks.py`):
```python
from arq import create_pool
from arq.connections import RedisSettings
import os

# ARQ settings
ARQ_REDIS_SETTINGS = RedisSettings.from_dsn(
    os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Task functions
async def process_test_results(ctx, run_id: str):
    """Background task: Process test results with MATRIZ"""
    # Import here to avoid circular imports
    from matriz.orchestration.async_orchestrator import AsyncCognitiveOrchestrator
    from .database import AsyncSessionLocal
    from .models import TestRun

    async with AsyncSessionLocal() as db:
        # Get test run
        result = await db.execute(
            select(TestRun).where(TestRun.id == run_id)
        )
        test_run = result.scalar_one_or_none()

        if not test_run:
            return {"error": "Test run not found"}

        # MATRIZ cognitive analysis
        orchestrator = AsyncCognitiveOrchestrator()
        analysis = await orchestrator.analyze_test_results(
            test_run_id=run_id,
            test_results=test_run.test_results,
        )

        # Update test run with analysis
        test_run.matriz_analysis = analysis
        test_run.consciousness_score = analysis.get("consciousness_score", 0.0)
        await db.commit()

        # Publish event
        await publish_event("matriz_analysis_complete", {
            "run_id": run_id,
            "consciousness_score": test_run.consciousness_score,
        })

        return {"status": "success", "run_id": run_id}

async def heal_flaky_test(ctx, test_name: str):
    """Background task: Memory Healix self-healing"""
    # TODO: Implement self-healing logic
    pass

# Worker class
class WorkerSettings:
    functions = [process_test_results, heal_flaky_test]
    redis_settings = ARQ_REDIS_SETTINGS
    max_jobs = 10
    job_timeout = 300  # 5 minutes

# Usage in FastAPI:
# from arq import create_pool
# redis_pool = await create_pool(ARQ_REDIS_SETTINGS)
# job = await redis_pool.enqueue_job("process_test_results", run_id="123")
```

---

## Real-Time Communication

### Socket.IO (NOT Native WebSocket)

**Frontend**: `socket.io-client@4.7.0`
**Backend**: `python-socketio@5.11.0`

**Why Socket.IO (NOT Native WebSocket)**:
- **Vercel Compatibility**: Serverless functions don't support persistent WebSocket connections
- **Auto-Reconnect**: Built-in reconnection logic
- **Fallback**: Falls back to HTTP long-polling if WebSocket fails
- **Room Support**: Easy pub/sub pattern
- **Event-Based**: Cleaner API than raw WebSocket

**IMPORTANT**: Socket.IO server runs on separate service (Railway), not Vercel.

**Backend Setup** (`socket_server/main.py`):
```python
import socketio
import uvicorn
from fastapi import FastAPI

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://lukhas.team",
    ],
)

# Wrap with ASGI app
app = FastAPI()
socket_app = socketio.ASGIApp(sio, app)

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def join_team(sid, data):
    """Join team room for real-time updates"""
    team_id = data.get("team_id")
    await sio.enter_room(sid, f"team:{team_id}")
    await sio.emit("joined", {"team_id": team_id}, room=sid)

# Emit test results when test completes
async def broadcast_test_completed(team_id: str, test_run: dict):
    await sio.emit("test_completed", test_run, room=f"team:{team_id}")

# Emit MATRIZ analysis updates
async def broadcast_matriz_analysis(team_id: str, analysis: dict):
    await sio.emit("matriz_analysis", analysis, room=f"team:{team_id}")

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=3001)
```

**Frontend Setup** (`lib/socket.ts`):
```typescript
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:3001';

let socket: Socket | null = null;

export function getSocket(): Socket {
  if (!socket) {
    socket = io(SOCKET_URL, {
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socket.on('connect', () => {
      console.log('Socket.IO connected');
    });

    socket.on('disconnect', () => {
      console.log('Socket.IO disconnected');
    });
  }

  return socket;
}

export function joinTeam(teamId: string) {
  const socket = getSocket();
  socket.emit('join_team', { team_id: teamId });
}

export function onTestCompleted(callback: (data: any) => void) {
  const socket = getSocket();
  socket.on('test_completed', callback);
}

export function onMatrizAnalysis(callback: (data: any) => void) {
  const socket = getSocket();
  socket.on('matriz_analysis', callback);
}
```

**Usage in Component** (`app/(dashboard)/tests/page.tsx`):
```typescript
'use client';

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { getSocket, joinTeam, onTestCompleted } from '@/lib/socket';

export default function TestsPage() {
  const queryClient = useQueryClient();

  useEffect(() => {
    // Connect to Socket.IO
    const socket = getSocket();
    joinTeam('team_123');  // TODO: Get from auth

    // Listen for test completion events
    const handleTestCompleted = (data: any) => {
      console.log('Test completed:', data);

      // Invalidate test results query to refetch
      queryClient.invalidateQueries({ queryKey: ['testResults'] });

      // Show toast notification
      toast.success('Test run completed!');
    };

    onTestCompleted(handleTestCompleted);

    return () => {
      socket.off('test_completed', handleTestCompleted);
    };
  }, [queryClient]);

  // ... rest of component
}
```

---

## Authentication System

### next-auth v5 + ΛiD WebAuthn

**Frontend**: `next-auth@5.0.0-beta.3`
**Backend**: Existing ΛiD system (`lukhas/identity/webauthn_verify.py`)

**Configuration** (`lib/auth.ts`):
```typescript
import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { startAuthentication } from '@simplewebauthn/browser';

const LUKHAS_API = process.env.NEXT_PUBLIC_LUKHAS_API || 'http://localhost:8000';

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    CredentialsProvider({
      id: 'webauthn',
      name: 'ΛiD Passkey',
      credentials: {},
      async authorize(credentials) {
        // Step 1: Get WebAuthn challenge from LUKHAS API
        const challengeResponse = await fetch(`${LUKHAS_API}/id/webauthn/challenge`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: credentials?.email }),
        });

        if (!challengeResponse.ok) return null;

        const { challenge, allowCredentials } = await challengeResponse.json();

        // Step 2: Browser WebAuthn API (prompt for passkey)
        const assertion = await startAuthentication({
          challenge,
          allowCredentials,
          userVerification: 'required',
        });

        // Step 3: Verify with LUKHAS ΛiD system
        const verifyResponse = await fetch(`${LUKHAS_API}/id/webauthn/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            assertion,
            email: credentials?.email,
          }),
        });

        if (!verifyResponse.ok) return null;

        const { lambda_id, email, display_name } = await verifyResponse.json();

        // Return user object
        return {
          id: lambda_id,
          email,
          name: display_name,
        };
      },
    }),
  ],

  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60,  // 30 days
  },

  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.lambda_id = user.id;
        token.email = user.email;
      }
      return token;
    },

    async session({ session, token }) {
      if (session.user) {
        session.user.lambda_id = token.lambda_id as string;
        session.user.email = token.email as string;
      }
      return session;
    },
  },

  pages: {
    signIn: '/login',
    error: '/auth/error',
  },
});
```

**Login Page** (`app/(auth)/login/page.tsx`):
```typescript
'use client';

import { signIn } from 'next-auth/react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePasskeyLogin = async () => {
    setLoading(true);
    try {
      const result = await signIn('webauthn', {
        email,
        redirect: true,
        callbackUrl: '/',
      });

      if (result?.error) {
        console.error('Login failed:', result.error);
        // Show error toast
      }
    } catch (error) {
      console.error('WebAuthn error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Welcome to lukhas.team</h1>
          <p className="mt-2 text-muted-foreground">
            Sign in with your ΛiD passkey
          </p>
        </div>

        <div className="space-y-4">
          <Input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Button
            onClick={handlePasskeyLogin}
            disabled={loading || !email}
            className="w-full"
          >
            {loading ? 'Authenticating...' : 'Sign in with Passkey'}
          </Button>
        </div>
      </div>
    </div>
  );
}
```

---

## Complete package.json

```json
{
  "name": "lukhas-team-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",

    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-popover": "^1.0.7",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-separator": "^1.0.3",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-tooltip": "^1.0.7",

    "@tanstack/react-query": "^5.28.0",
    "@tanstack/react-query-devtools": "^5.28.0",
    "zustand": "^4.5.0",

    "socket.io-client": "^4.7.0",

    "@codemirror/view": "^6.24.1",
    "@codemirror/state": "^6.4.1",
    "@codemirror/lang-python": "^6.1.4",
    "@codemirror/lang-javascript": "^6.2.2",
    "@codemirror/theme-one-dark": "^6.1.2",
    "@codemirror/commands": "^6.3.3",
    "@codemirror/search": "^6.5.6",
    "@codemirror/lint": "^6.5.0",

    "recharts": "^2.12.0",
    "d3": "^7.9.0",
    "framer-motion": "^11.0.0",

    "next-auth": "^5.0.0-beta.3",
    "@simplewebauthn/browser": "^9.0.0",

    "axios": "^1.6.7",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1",
    "tailwindcss-animate": "^1.0.7",
    "class-variance-authority": "^0.7.0",
    "lucide-react": "^0.344.0"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "@types/node": "^20.11.19",
    "@types/react": "^18.2.57",
    "@types/react-dom": "^18.2.19",
    "@types/d3": "^7.4.3",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.35",
    "autoprefixer": "^10.4.17",
    "eslint": "^8.56.0",
    "eslint-config-next": "^14.2.0",
    "@tailwindcss/typography": "^0.5.10"
  }
}
```

---

## Complete Backend Dependencies

**requirements.txt**:
```txt
# Core
fastapi==0.121.0
uvicorn[standard]==0.33.0
python-multipart==0.0.9

# Database
sqlalchemy==2.0.44
asyncpg>=0.29.0
alembic>=1.13.0

# Caching & Queue
redis[hiredis]>=5.0.0
arq>=0.26.0

# Auth
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=1.0.0

# Real-time
python-socketio==5.11.0

# Testing
pytest>=8.2.0
pytest-asyncio>=0.24.0
pytest-cov>=5.0.0
httpx>=0.27.0

# Existing LUKHAS dependencies (keep these)
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

---

*Continue to next section...*

---

## Database Architecture

### PostgreSQL 15 Schema Design

**Tables Overview**:

1. **users** - User accounts (ΛiD integration)
2. **teams** - Team/organization management
3. **test_runs** - Test execution metadata (partitioned by date)
4. **test_results** - Individual test results
5. **coverage_data** - Code coverage per file
6. **healix_memories** - Memory Healix learning data
7. **consciousness_reviews** - 8-Star constellation reviews
8. **user_preferences** - UI preferences and settings

**Complete Schema** (See DATABASE_SCHEMA_COMPLETE.md for full details)

---

## Deployment Architecture

### Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  lukhas.team Deployment                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend (Vercel)              Backend (Railway)           │
│  ┌──────────────────┐          ┌──────────────────────┐    │
│  │  Next.js App     │◄─────────│  FastAPI Server      │    │
│  │  (Edge Runtime)  │  HTTPS   │  (LUKHAS API)        │    │
│  │                  │          │                      │    │
│  │  • SSR/ISR       │          │  • Test Results API  │    │
│  │  • Static Assets │          │  • Coverage API      │    │
│  │  • API Routes    │          │  • MATRIZ Integration│    │
│  └──────────────────┘          └──────────────────────┘    │
│                                                             │
│  Socket.IO Server (Railway)    Database (Supabase)         │
│  ┌──────────────────┐          ┌──────────────────────┐    │
│  │  python-socketio │          │  PostgreSQL 15       │    │
│  │                  │◄─────────│  (Async via asyncpg) │    │
│  │  • Real-time     │          │                      │    │
│  │  • Room Support  │          │  • Partitioned Tables│    │
│  │  • Pub/Sub       │          │  • TimescaleDB (opt) │    │
│  └──────────────────┘          └──────────────────────┘    │
│                                                             │
│  Redis (Upstash)               Storage (Supabase)          │
│  ┌──────────────────┐          ┌──────────────────────┐    │
│  │  Redis Cloud     │          │  S3-compatible       │    │
│  │                  │          │                      │    │
│  │  • Session Cache │          │  • Allure Reports    │    │
│  │  • Task Queue    │          │  • Test Artifacts    │    │
│  │  • Pub/Sub       │          │  • Icons/Images      │    │
│  └──────────────────┘          └──────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Cost Estimate

| Service | Plan | Cost/Month | Notes |
|---------|------|------------|-------|
| **Vercel** | Hobby/Pro | $0-20 | Free for hobby, $20 for team |
| **Railway** | Starter | $20 | FastAPI + Socket.IO server |
| **Supabase** | Pro | $25 | PostgreSQL + storage (2GB) |
| **Upstash Redis** | Pay-as-go | $0-10 | 10K commands/day free |
| **Total** | | **$12-75** | Scales with usage |

**Free Tier Option** (~$12/mo):
- Vercel Hobby (free)
- Railway $5 credit/mo
- Supabase free tier (500MB)
- Upstash free tier

---

## Performance Optimization

### 1. Next.js Optimizations

**React Server Components** (RSC):
```typescript
// app/(dashboard)/tests/page.tsx
// This is a Server Component (default in App Router)
export default async function TestsPage() {
  // Fetch on server (no client-side loading state needed)
  const testRuns = await fetchTestRuns();

  return (
    <div>
      <h1>Test Results</h1>
      {/* Pass data to Client Component */}
      <TestResultsTable data={testRuns} />
    </div>
  );
}

async function fetchTestRuns() {
  const res = await fetch('http://lukhas-api/tests/runs', {
    next: { revalidate: 60 },  // ISR: Revalidate every 60s
  });
  return res.json();
}
```

**Code Splitting**:
```typescript
// Lazy load heavy components
import dynamic from 'next/dynamic';

const ConsciousnessGraph = dynamic(() => import('@/components/charts/ConsciousnessGraph'), {
  loading: () => <div>Loading graph...</div>,
  ssr: false,  // Don't render on server (D3.js is client-only)
});
```

### 2. Backend Optimizations

**Database Query Optimization**:
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Eager loading to avoid N+1 queries
async def get_test_run_with_results(db: AsyncSession, run_id: str):
    result = await db.execute(
        select(TestRun)
        .options(selectinload(TestRun.test_results))  # Eager load
        .where(TestRun.id == run_id)
    )
    return result.scalar_one_or_none()
```

**Caching Strategy**:
```python
from functools import wraps
import hashlib
import json

def cached(ttl: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name + args
            key_data = f"{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs)}"
            cache_key = f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"

            # Check cache
            cached_value = await cache_get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_set(cache_key, result, ttl=ttl)

            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=60)
async def get_team_coverage_stats(team_id: str):
    # Expensive query cached for 60 seconds
    ...
```

### 3. Real-Time Optimization

**Socket.IO Rooms** (Reduce Broadcast Overhead):
```python
# Instead of broadcasting to all clients
await sio.emit("test_completed", data)  # ❌ All clients receive

# Broadcast only to team room
await sio.emit("test_completed", data, room=f"team:{team_id}")  # ✅ Only team members
```

---

## Development Workflow

### docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: lukhas
      POSTGRES_PASSWORD: password
      POSTGRES_DB: lukhas_team
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://lukhas:password@postgres:5432/lukhas_team
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./serve:/app/serve
      - ./lukhas:/app/lukhas
      - ./MATRIZ:/app/MATRIZ
    command: uvicorn serve.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - postgres
      - redis

  # Socket.IO Server
  socketio:
    build:
      context: .
      dockerfile: Dockerfile.socketio
    ports:
      - "3001:3001"
    environment:
      REDIS_URL: redis://redis:6379/0
    command: python socket_server/main.py
    depends_on:
      - redis

  # ARQ Worker (Background Tasks)
  arq_worker:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      DATABASE_URL: postgresql+asyncpg://lukhas:password@postgres:5432/lukhas_team
      REDIS_URL: redis://redis:6379/0
    command: arq serve.lukhas_team.tasks.WorkerSettings
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

### Makefile

```makefile
.PHONY: help dev build test

help:
	@echo "lukhas.team Development Commands"
	@echo "  make dev         - Start development environment"
	@echo "  make build       - Build Docker images"
	@echo "  make test        - Run tests"
	@echo "  make migrate     - Run database migrations"
	@echo "  make frontend    - Start Next.js frontend"

dev:
	docker-compose up -d postgres redis
	@echo "Starting backend and frontend..."
	docker-compose up backend socketio arq_worker

frontend:
	cd lukhas-team-frontend && npm run dev

build:
	docker-compose build

test:
	pytest tests/ -v --cov=serve/lukhas_team

migrate:
	alembic upgrade head
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-10
**Status**: Technical Specification Complete
**Next Document**: [LAMBDA_ID_INTEGRATION_GUIDE.md](LAMBDA_ID_INTEGRATION_GUIDE.md)

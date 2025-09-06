/** @type {import('next').NextConfig} */

// 0.001% Multi-Domain Configuration for LUKHΛS λWecosystem
// Quantum Domain Mesh Architecture - Each domain exists in superposition until collapsed to specific experience
const LUKHAS_DOMAINS = [
  'lukhas.ai',     // Main AI platform - Consciousness Technology Hub
  'lukhas.id',     // Identity & authentication - Zero-knowledge sovereignty
  'lukhas.team',   // Team collaboration - Distributed consciousness coordination
  'lukhas.dev',    // Developer platform - APIs, SDKs, consciousness integration tools
  'lukhas.io',     // API infrastructure - High-performance consciousness APIs
  'lukhas.store',  // App marketplace - Consciousness-enhanced applications
  'lukhas.cloud',  // Cloud services - Distributed quantum-inspired processing
  'lukhas.eu',     // European operations - GDPR-compliant consciousness services
  'lukhas.us',     // US operations - Enterprise consciousness platforms
  'lukhas.xyz',    // Experimental labs - Research, prototypes, consciousness R&D
  'lukhas.com'     // Enterprise/corporate - Business consciousness solutions
]

// Environment detection for domain routing
const isDevelopment = process.env.NODE_ENV === 'development'
const isProduction = process.env.NODE_ENV === 'production'

const nextConfig = {
  reactStrictMode: true,
  // Fix workspace root detection issue
  outputFileTracingRoot: __dirname,
  images: {
    domains: [
      'localhost', 
      ...LUKHAS_DOMAINS,
      'dalleproduse.blob.core.windows.net',
      // Development subdomains
      'ai.localhost',
      'id.localhost', 
      'team.localhost',
      'dev.localhost',
      'io.localhost',
      'store.localhost',
      'cloud.localhost',
      'eu.localhost',
      'us.localhost',
      'xyz.localhost',
      'com.localhost'
    ],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
  // Note: For HTTPS in development, use: next dev --experimental-https
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(self), geolocation=()'
          },
          {
            key: 'Content-Security-Policy',
            value: `default-src 'self' ${LUKHAS_DOMAINS.map(d => `https://${d}`).join(' ')}; img-src 'self' data: blob: https://dalleproduse.blob.core.windows.net ${LUKHAS_DOMAINS.map(d => `https://${d}`).join(' ')}; media-src 'self' blob: data:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' data:; font-src 'self' data:; connect-src 'self' https://api.openai.com https://api.anthropic.com https://generativelanguage.googleapis.com ${LUKHAS_DOMAINS.map(d => `https://${d}`).join(' ')} ${LUKHAS_DOMAINS.map(d => `wss://${d}`).join(' ')}; worker-src 'self' blob:; frame-src 'none';`
          },
        ],
      },
      {
        source: '/.well-known/jwks.json',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400, must-revalidate',
          },
          {
            key: 'Content-Type',
            value: 'application/json'
          },
        ],
      },
      {
        source: '/fonts/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },
  async redirects() {
    return [
      // MATRIZ rebrand redirects
      {
        source: '/matada',
        destination: '/matriz',
        permanent: true,
      },
      {
        source: '/matada/:path*',
        destination: '/matriz/:path*',
        permanent: true,
      },
      {
        source: '/MATADA',
        destination: '/matriz',
        permanent: true,
      },
      {
        source: '/MATADA/:path*',
        destination: '/matriz/:path*',
        permanent: true,
      },
      // Handle lambda character in URLs (should not happen but fallback)
      {
        source: '/m%CE%BBtriz',
        destination: '/matriz',
        permanent: true,
      },
      {
        source: '/mλtriz',
        destination: '/matriz',
        permanent: true,
      },
    ]
  },
  async rewrites() {
    // Production API endpoints for different consciousness domains
    const productionAPI = process.env.LUKHAS_API_URL || 'https://api.lukhas.ai'
    const identityAPI = process.env.LUKHAS_IDENTITY_API || 'https://api.lukhas.id'
    
    // Domain-specific API routing for the quantum domain mesh
    const domainRewrites = isProduction ? [
      // Production domain routing - routes to actual microservices
      {
        source: '/api/auth/:path*',
        has: [{ type: 'host', value: 'lukhas.id' }],
        destination: `${identityAPI}/auth/:path*`
      },
      {
        source: '/api/identity/:path*', 
        has: [{ type: 'host', value: 'lukhas.id' }],
        destination: `${identityAPI}/identity/:path*`
      },
      {
        source: '/api/consciousness/:path*',
        has: [{ type: 'host', value: 'lukhas.ai' }],
        destination: `${productionAPI}/consciousness/:path*`
      },
      {
        source: '/api/dev/:path*',
        has: [{ type: 'host', value: 'lukhas.dev' }],
        destination: `${productionAPI}/dev/:path*`
      },
      {
        source: '/api/cloud/:path*',
        has: [{ type: 'host', value: 'lukhas.cloud' }],
        destination: `${productionAPI}/cloud/:path*`
      },
      {
        source: '/api/store/:path*',
        has: [{ type: 'host', value: 'lukhas.store' }],
        destination: `${productionAPI}/store/:path*`
      }
    ] : [
      // Development domain routing - routes to localhost services
      {
        source: '/api/auth/:path*',
        has: [{ type: 'host', value: 'id.localhost' }],
        destination: 'http://localhost:7402/identity/:path*'
      },
      {
        source: '/api/identity/:path*', 
        has: [{ type: 'host', value: 'id.localhost' }],
        destination: 'http://localhost:7402/:path*'
      },
      {
        source: '/api/tools/:path*',
        has: [{ type: 'host', value: 'dev.localhost' }],
        destination: 'http://localhost:8000/dev/:path*'
      },
      {
        source: '/api/cloud/:path*',
        has: [{ type: 'host', value: 'cloud.localhost' }],
        destination: 'http://localhost:8000/cloud/:path*'
      },
      {
        source: '/api/store/:path*',
        has: [{ type: 'host', value: 'store.localhost' }],
        destination: 'http://localhost:8000/store/:path*'
      }
    ]

    // Development environment rewrites (fallback for all domains)
    const devRewrites = isDevelopment ? [
      // New API service rewrites for development - all point to dev server
      { source: "/api/identity/:path*", destination: "http://localhost:7402/:path*" },
      { source: "/api/wallet/:path*",   destination: "http://localhost:7402/:path*" },
      { source: "/api/qrg/:path*",      destination: "http://localhost:7402/:path*" },
      { source: "/api/consent/:path*",  destination: "http://localhost:7402/:path*" },
      // Legacy LUKHAS backend fallback
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*', // LUKHAS backend
      }
    ] : []

    return [
      ...domainRewrites,
      ...devRewrites
    ]
  },
  webpack: (config) => {
    config.module.rules.push({
      test: /\.(woff|woff2|eot|ttf|otf)$/,
      use: {
        loader: 'file-loader',
        options: {
          publicPath: '/_next/static/fonts/',
          outputPath: 'static/fonts/',
        },
      },
    })

    return config
  },
}

module.exports = nextConfig

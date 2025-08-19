/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost', 'lukhas.ai'],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
  // HTTPS development configuration for WebAuthn support
  server: {
    https: process.env.NODE_ENV === 'development' && process.env.DEV_HTTPS_ENABLED === 'true' ? {
      key: process.env.DEV_SSL_KEY || './certs/localhost.key',
      cert: process.env.DEV_SSL_CERT || './certs/localhost.crt',
    } : undefined,
  },
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
            value: 'camera=(), microphone=(), geolocation=()'
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
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*', // LUKHAS backend
      },
      {
        source: '/proteus',
        destination: 'http://localhost:8080', // PR0T3US visualizer (served separately)
      },
      {
        source: '/proteus/:path*',
        destination: 'http://localhost:8080/:path*', // PR0T3US assets
      },
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
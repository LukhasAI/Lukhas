/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizePackageImports: ['framer-motion', 'lucide-react']
  },
  images: {
    formats: ['image/avif', 'image/webp'],
    remotePatterns: []
  },
  poweredByHeader: false,
  compress: true,
  reactStrictMode: true
}

module.exports = nextConfig
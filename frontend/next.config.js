/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'https://lexredline-3ekz.onrender.com/api/v1/:path*',
      },
    ]
  },
}

module.exports = nextConfig

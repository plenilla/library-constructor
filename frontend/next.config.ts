/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: 'export', // ← Убираем статический экспорт
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    // либо просто перечислить имена хостов
    domains: ['www.exhibitdes.ru', 'exhibitdes.ru'],
    // либо паттерны (Next 12+)
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'www.exhibitdes.ru',
        port: '',
        pathname: '/static/picture/**',
      },
    ],
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-Forwarded-Host",
            value: "exhibitdes.ru",
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
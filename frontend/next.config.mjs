/** @type {import('next').NextConfig} */
// Force redeploy - implement custom map background
const nextConfig = {
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: '**.r2.cloudflarestorage.com',
            },
            {
                protocol: 'https',
                hostname: '**.cloudflare.com',
            },
            {
                protocol: 'https',
                hostname: '**.r2.dev',
            },
        ],
    },
};

export default nextConfig;

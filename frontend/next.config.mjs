const apiInternalUrl = process.env.API_INTERNAL_URL || "http://localhost:8000";

const nextConfig = {
  poweredByHeader: false,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: apiInternalUrl + "/api/:path*"
      }
    ];
  }
};

export default nextConfig;

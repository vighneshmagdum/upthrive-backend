const apiInternalUrl = process.env.API_INTERNAL_URL || "http://localhost:8000";
const staticExport = process.env.STATIC_EXPORT === "true";

const nextConfig = {
  poweredByHeader: false,
  ...(staticExport ? { output: "export", trailingSlash: true, images: { unoptimized: true } } : {}),
  async rewrites() {
    if (staticExport) return [];
    return [
      {
        source: "/api/:path*",
        destination: apiInternalUrl + "/api/:path*"
      }
    ];
  }
};

export default nextConfig;

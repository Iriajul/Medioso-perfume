import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Self-contained server bundle for the production Docker image.
  output: "standalone",
  images: {
    remotePatterns: [new URL("https://res.cloudinary.com/**")],
  },
  experimental: {
    // Image uploads go through server actions (10MB max + multipart overhead).
    serverActions: { bodySizeLimit: "11mb" },
  },
};

export default nextConfig;

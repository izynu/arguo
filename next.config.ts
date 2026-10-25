import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Default build stays "standalone". CI static export for GitHub Pages sets
  // NEXT_OUTPUT=export and NEXT_PUBLIC_BASE_PATH (see
  // .github/workflows/deploy-pages.yml). NEXT_PUBLIC_BASE_PATH drives both the
  // asset prefix here and client-side data fetch prefixes in src/lib/site-config.ts.
  output: process.env.NEXT_OUTPUT === "export" ? "export" : "standalone",
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || undefined,
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
};

export default nextConfig;

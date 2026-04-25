import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export", // Required for GitHub Pages
  images: {
    unoptimized: true, // Required for GitHub Pages
  },
  basePath: "/soup_cornell_claude_hackathon",
  assetPrefix: "/soup_cornell_claude_hackathon",
};

export default nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  images: {
    unoptimized: true,
  },
  // ADD THESE TWO LINES:
  // Use your EXACT repository name here
  basePath: "/soup_cornell_claude_hackathon",
  assetPrefix: "/soup_cornell_claude_hackathon",
};

export default nextConfig;

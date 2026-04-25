/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export", // CRITICAL: Tells Next to create a 'out' folder
  images: {
    unoptimized: true, // GitHub Pages can't resize images on the fly
  },
  // If your repo is NOT 'username.github.io' (e.g. it is 'username.github.io/my-repo')
  // add the line below:
  // basePath: '/your-repo-name',
};

export default nextConfig;

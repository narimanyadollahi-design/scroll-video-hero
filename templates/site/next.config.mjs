/** @type {import('next').NextConfig} */
const isExport = process.env.EXPORT === "1";
const nextConfig = {
  reactStrictMode: true,
  // EXPORT=1 -> fully static site in ./out (for USB / any static host)
  ...(isExport ? { output: "export", images: { unoptimized: true } } : {}),
  ...(isExport
    ? {}
    : {
        async headers() {
          return [
            {
              source: "/:all*(mp4|webm|jpg|webp)",
              headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
            },
          ];
        },
      }),
};
export default nextConfig;

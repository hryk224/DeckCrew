import path from "node:path";
import type { NextConfig } from "next";

const isDemo = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

const nextConfig: NextConfig = {
  turbopack: {
    root: path.join(__dirname, ".."),
  },
  ...(isDemo && {
    output: "export",
    basePath: "/DeckCrew",
    images: { unoptimized: true },
  }),
};

export default nextConfig;

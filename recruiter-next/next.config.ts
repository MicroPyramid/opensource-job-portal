import type { NextConfig } from "next";

// Django serves media from MEDIA_URL: /media/ off the API host locally, and from
// an S3 bucket in production (jobsp/settings_server.py). Derive the dev pattern
// from API_BASE_URL rather than hardcoding a host — see MIGRATION.md debt #1.
const apiUrl = new URL(process.env.API_BASE_URL ?? "http://localhost:8000/api/v1");
const mediaHost = process.env.MEDIA_HOSTNAME;

const nextConfig: NextConfig = {
  // Every internal link in the recruiter UI is written with a trailing slash
  // (/dashboard/jobs/). This must stay on to match SvelteKit's behaviour.
  trailingSlash: true,

  // Replaces SvelteKit's adapter-node. Build output is .next/standalone/server.js
  output: "standalone",

  images: {
    remotePatterns: [
      {
        protocol: apiUrl.protocol.replace(":", "") as "http" | "https",
        hostname: apiUrl.hostname,
        port: apiUrl.port,
        pathname: "/media/**",
      },
      ...(mediaHost
        ? ([
            {
              protocol: "https" as const,
              hostname: mediaHost,
              pathname: "/**",
            },
          ])
        : []),
    ],
  },
};

export default nextConfig;

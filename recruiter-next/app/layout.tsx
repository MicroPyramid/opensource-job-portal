import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PeelJobs Recruiter",
  description: "Post jobs, manage applicants, and grow your team on PeelJobs.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full">{children}</body>
    </html>
  );
}

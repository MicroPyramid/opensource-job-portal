import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PeelJobs Recruiter",
  description: "Post jobs, manage applicants, and grow your team on PeelJobs.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // No utility classes on <html>/<body>: the SvelteKit app.html had none, and
    // page layouts set their own `min-h-screen`. The h-full/min-h-full pair here
    // was create-next-app boilerplate.
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

import Link from "next/link";
import { Building2 } from "lucide-react";

/**
 * Public auth shell: header, page content, footer.
 *
 * Ports recruiter/src/routes/(auth)/+layout.svelte. The <main> element it used to
 * own now lives in components/auth/AuthMain.tsx and is rendered by each page —
 * see the note there for why.
 */
export default function AuthLayout({ children }: LayoutProps<"/">) {
  return (
    <div className="min-h-screen bg-surface flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link href="/" className="flex items-center gap-2">
            <Building2 className="w-8 h-8 text-primary" />
            <span className="text-xl font-bold text-black">PeelJobs</span>
            <span className="text-sm text-muted ml-2">For Employers</span>
          </Link>
        </div>
      </header>

      {children}

      {/* Footer */}
      <footer className="bg-white border-t border-border py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted">
            <p>&copy; 2025 PeelJobs. All rights reserved.</p>
            {/* NOTE: all four of these 404 on the recruiter host — the pages live
                on the job-seeker site. Ported as-is for parity; see MIGRATION.md
                debt #14. */}
            <div className="flex gap-6">
              <Link href="/about/" className="hover:text-black transition-colors">
                About
              </Link>
              <Link href="/privacy/" className="hover:text-black transition-colors">
                Privacy
              </Link>
              <Link href="/terms/" className="hover:text-black transition-colors">
                Terms
              </Link>
              <Link href="/contact/" className="hover:text-black transition-colors">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

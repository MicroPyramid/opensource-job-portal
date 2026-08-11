import { Sidebar } from "@/components/dashboard/Sidebar";
import { requireAuth } from "@/lib/auth/dal";
import { logoutAction } from "./actions";

/**
 * Authenticated dashboard shell.
 *
 * Ports (dashboard)/+layout.server.ts and +layout.svelte. The server load and the
 * markup merge into this one Server Component: it awaits the user, then hands it
 * to the client-side chrome as a prop.
 *
 * `requireAuth()` is the authoritative check. `proxy.ts` has already bounced
 * requests with no cookies at all, but a cookie that Django rejects only shows up
 * here — in which case the DAL redirects to /login/, matching the original's
 * behaviour of clearing cookies and bouncing on a failed /auth/me/.
 */
export default async function DashboardLayout({ children }: LayoutProps<"/">) {
  const user = await requireAuth();

  return (
    <div className="min-h-screen bg-surface">
      <Sidebar user={user} logoutAction={logoutAction} />

      <main className="lg:pl-64 pt-16 lg:pt-0">
        <div className="p-6 md:p-8">{children}</div>
      </main>
    </div>
  );
}

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

/**
 * Entry redirect. Ports recruiter/src/routes/+page.server.ts — sends the user to
 * the dashboard if they hold auth cookies, otherwise to login.
 *
 * This is an optimistic cookie-presence check only; the dashboard layout does the
 * authoritative check against the API. See MIGRATION.md § Auth architecture.
 */
export default async function Home() {
  const cookieStore = await cookies();
  const hasAuth =
    cookieStore.has("access_token") || cookieStore.has("refresh_token");

  redirect(hasAuth ? "/dashboard/" : "/login/");
}

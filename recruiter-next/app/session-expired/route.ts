import { NextResponse, type NextRequest } from "next/server";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "@/lib/auth/cookie-config";

/**
 * Clears a dead session, then sends the user to login.
 *
 * This exists to break a redirect loop. When a cookie is present but Django
 * rejects it — a deactivated recruiter, a deleted account, a blacklisted token —
 * `requireAuth()` wants to bounce to /login/, but `proxy.ts` sees a token in the
 * request and bounces authenticated-looking traffic straight back to /dashboard/.
 * The two ping-pong forever.
 *
 * The SvelteKit layout avoided this by deleting the cookies before redirecting,
 * which a Server Component cannot do — Next only permits cookie writes in Server
 * Actions and Route Handlers. Hence this handler: `requireAuth()` redirects here
 * instead, the cookies are cleared on the response, and the follow-on redirect to
 * /login/ then carries no credentials for the proxy to react to.
 */
export async function GET(request: NextRequest) {
  const redirectTo = request.nextUrl.searchParams.get("redirect");

  const target = new URL("/login/", request.url);
  if (redirectTo) target.searchParams.set("redirect", redirectTo);

  const response = NextResponse.redirect(target);
  response.cookies.delete(ACCESS_TOKEN);
  response.cookies.delete(REFRESH_TOKEN);

  return response;
}

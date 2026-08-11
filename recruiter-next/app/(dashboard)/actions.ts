"use server";

import { redirect, unstable_rethrow } from "next/navigation";
import { logout as apiLogout } from "@/lib/api/auth";
import { clearAuthCookies } from "@/lib/auth/session";

/**
 * Log out: blacklist the refresh token server-side, drop our cookies, go to login.
 *
 * Replaces `authStore.logout()`, which did the same work from the browser across
 * three round trips (`/api/auth/clear-cookies`, the Django logout, then a
 * client-side `goto`). One server round trip now, and the cookie clearing cannot
 * be skipped by a failed fetch.
 */
export async function logoutAction() {
  // Best-effort: if Django is unreachable the local session must still end.
  try {
    await apiLogout();
  } catch (error) {
    // Never swallow Next's own control-flow signals.
    unstable_rethrow(error);
    // Token blacklisting failed — the cookies are cleared regardless, so the
    // session is over on this device either way.
  }

  await clearAuthCookies();
  redirect("/login/");
}

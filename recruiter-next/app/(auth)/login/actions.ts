"use server";

import { redirect } from "next/navigation";
import { login } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { setAuthCookies } from "@/lib/auth/session";

export interface LoginState {
  error?: string;
  /** Echoed back so the field survives a failed submit. */
  email?: string;
}

/**
 * Ports the default form action in (auth)/login/+page.server.ts.
 *
 * Two differences from the original:
 *  - The Django error branches (`detail` / `non_field_errors` / per-field) were
 *    unpacked by hand there; `ApiError.message` already runs them through
 *    `formatApiError`, which produces the same strings.
 *  - `redirect()` is called outside the try block. The original wrapped it and
 *    then had to re-throw by sniffing `error?.status === 302` (debt #6) —
 *    redirect signals as a thrown value, so catching it at all is the bug.
 */
export async function loginAction(
  _prevState: LoginState,
  formData: FormData,
): Promise<LoginState> {
  const email = formData.get("email")?.toString() ?? "";
  const password = formData.get("password")?.toString() ?? "";
  const rememberMe = formData.get("remember_me") === "on";
  const redirectTo = formData.get("redirect_to")?.toString() || "/dashboard/";

  if (!email || !password) {
    return { error: "Email and password are required", email };
  }

  try {
    const data = await login({ email, password, remember_me: rememberMe });
    await setAuthCookies(data.access, data.refresh);
  } catch (error) {
    if (error instanceof ApiError) {
      return { error: error.message, email };
    }

    console.error("Login error:", error);
    return {
      error: "An unexpected error occurred. Please try again.",
      email,
    };
  }

  // Outside the catch: redirect() works by throwing.
  redirect(redirectTo);
}

import "server-only";
import { api } from "@/lib/api/client";
import type {
  User,
  Company,
  RegisterData,
  LoginData,
  AuthResponse,
  VerifyEmailData,
  ForgotPasswordData,
  ResetPasswordData,
  ChangePasswordData,
  AcceptInvitationData,
  MutationResponse,
} from "@/lib/types";

/**
 * Recruiter authentication API.
 *
 * Ports recruiter/src/lib/api/auth.ts. The `skipAuth` third argument is preserved
 * — these endpoints are called before a session exists, so sending a stale
 * Authorization header would be wrong.
 *
 * Note: unlike the original's header comment, login DOES return tokens in the
 * response body (see AuthResponse). It is this app, not Django, that puts them
 * into HttpOnly cookies — see lib/auth/session.ts.
 */

/**
 * Registration returns a deliberately thin user/company — Django serialises only
 * these fields inline rather than running the full serializers
 * (api/v1/recruiter/auth_views.py). The original typed this as the complete
 * `User` and `Company`, promising fields the response never contains.
 */
export interface RegisterResponse {
  success: boolean;
  user: Pick<User, "id" | "email" | "user_type" | "is_active">;
  company: Pick<Company, "id" | "name" | "slug"> | null;
  message: string;
}

// ===== Registration & Login =====

export function register(data: RegisterData) {
  return api.post<RegisterResponse>("/recruiter/auth/register/", data, true);
}

export function login(data: LoginData) {
  return api.post<AuthResponse>("/recruiter/auth/login/", data, true);
}

/** Blacklists the refresh token server-side. Clearing cookies is the caller's job. */
export function logout() {
  return api.post<MutationResponse>("/recruiter/auth/logout/", {});
}

// ===== Email Verification =====

export function verifyEmail(data: VerifyEmailData) {
  return api.post<AuthResponse>("/recruiter/auth/verify-email/", data, true);
}

export function resendVerification(email: string) {
  return api.post<MutationResponse>(
    "/recruiter/auth/resend-verification/",
    { email },
    true,
  );
}

// ===== Password Management =====

export function forgotPassword(data: ForgotPasswordData) {
  return api.post<MutationResponse>("/recruiter/auth/forgot-password/", data, true);
}

export function resetPassword(data: ResetPasswordData) {
  return api.post<MutationResponse>("/recruiter/auth/reset-password/", data, true);
}

export function changePassword(data: ChangePasswordData) {
  return api.post<MutationResponse>("/recruiter/auth/change-password/", data);
}

// ===== Team Invitation =====

export function acceptInvitation(data: AcceptInvitationData) {
  return api.post<AuthResponse>(
    "/recruiter/auth/accept-invitation/",
    data,
    true,
  );
}

// ===== User Info =====

/**
 * Fetch the authenticated recruiter.
 *
 * Prefer `getCurrentUser()` from lib/auth/dal.ts in pages and actions — it wraps
 * this in React `cache()` so a request makes one call, not one per consumer.
 */
export function me() {
  return api.get<User>("/recruiter/auth/me/");
}

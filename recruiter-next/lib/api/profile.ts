import "server-only";
import { api } from "@/lib/api/client";
import type { User } from "@/lib/types";

/**
 * Recruiter profile API. Ports recruiter/src/lib/api/profile.ts.
 *
 * Both endpoints return the full `UserSerializer` payload
 * (api/v1/recruiter/auth_views.py), so `user` is a complete `User` — the
 * original typed it `any`.
 */

export interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  job_title?: string;
  mobile?: string;
}

export interface ProfileMutationResponse {
  success: boolean;
  user: User;
  message: string;
}

export function updateProfile(data: UpdateProfileData) {
  return api.patch<ProfileMutationResponse>(
    "/recruiter/profile/update/",
    data,
  );
}

export function uploadProfilePicture(file: File) {
  const formData = new FormData();
  formData.append("profile_pic", file);

  return api.postFormData<ProfileMutationResponse>(
    "/recruiter/profile/picture/",
    formData,
  );
}

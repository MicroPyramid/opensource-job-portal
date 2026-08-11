import "server-only";
import { api } from "@/lib/api/client";
import type {
  TeamListResponse,
  TeamMember,
  TeamMemberDetail,
  InvitationsListResponse,
  SendInvitationData,
  UpdateTeamMemberData,
  MutationResponse,
  TeamInvitation,
} from "@/lib/types";

/**
 * Team management API. Ports recruiter/src/lib/api/team.ts.
 *
 * Everything except the two list calls is admin-only; Django enforces that, and
 * `requireCompany()` in lib/auth/dal.ts keeps non-company users off these routes.
 *
 * Response shapes were re-derived from api/v1/recruiter/views.py rather than
 * carried over: the original annotated these as `ApiResponse<{ user }>` /
 * `ApiResponse<{ invitation }>`, but Django returns those keys at the top level,
 * so the nested `.data` those types promised never existed.
 */

// ===== Team Members =====

export function listTeamMembers() {
  return api.get<TeamListResponse>("/recruiter/team/");
}

export function getTeamMember(userId: number) {
  return api.get<TeamMemberDetail>(`/recruiter/team/${userId}/`);
}

/** Update job title / admin flag. Returns `TeamMemberSerializer`, not a full `User`. */
export function updateTeamMember(userId: number, data: UpdateTeamMemberData) {
  return api.patch<MutationResponse & { user: TeamMember }>(
    `/recruiter/team/${userId}/update/`,
    data,
  );
}

export function removeTeamMember(userId: number) {
  return api.delete<MutationResponse>(`/recruiter/team/${userId}/remove/`);
}

// ===== Team Invitations =====

export function inviteTeamMember(data: SendInvitationData) {
  return api.post<MutationResponse & { invitation: TeamInvitation }>(
    "/recruiter/team/invite/",
    data,
  );
}

export function listInvitations() {
  return api.get<InvitationsListResponse>("/recruiter/team/invitations/");
}

export function resendInvitation(invitationId: number) {
  return api.post<MutationResponse & { invitation: TeamInvitation }>(
    `/recruiter/team/invitations/${invitationId}/resend/`,
    {},
  );
}

export function cancelInvitation(invitationId: number) {
  return api.delete<MutationResponse>(
    `/recruiter/team/invitations/${invitationId}/cancel/`,
  );
}

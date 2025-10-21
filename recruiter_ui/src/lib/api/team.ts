/**
 * Team Management API for Recruiters
 * Handles team member CRUD operations and invitations
 */

import { ApiClient } from './client';
import type {
	TeamListResponse,
	TeamMemberDetail,
	InvitationsListResponse,
	SendInvitationData,
	UpdateTeamMemberData,
	ApiResponse,
	TeamInvitation
} from '$lib/types';

// ===== Team Members =====

/**
 * List all team members with stats
 */
export async function listTeamMembers(): Promise<TeamListResponse> {
	return ApiClient.get('/recruiter/team/');
}

/**
 * Get team member details
 */
export async function getTeamMember(userId: number): Promise<TeamMemberDetail> {
	return ApiClient.get(`/recruiter/team/${userId}/`);
}

/**
 * Update team member (job title, promote to admin, etc.)
 * Admin only
 */
export async function updateTeamMember(
	userId: number,
	data: UpdateTeamMemberData
): Promise<ApiResponse<{ user: any }>> {
	return ApiClient.patch(`/recruiter/team/${userId}/update/`, data);
}

/**
 * Remove team member
 * Admin only
 */
export async function removeTeamMember(userId: number): Promise<ApiResponse> {
	return ApiClient.delete(`/recruiter/team/${userId}/remove/`);
}

// ===== Team Invitations =====

/**
 * Invite new team member
 * Admin only
 */
export async function inviteTeamMember(
	data: SendInvitationData
): Promise<ApiResponse<{ invitation: TeamInvitation }>> {
	return ApiClient.post('/recruiter/team/invite/', data);
}

/**
 * List all invitations (pending, accepted, expired)
 * Admin only
 */
export async function listInvitations(): Promise<InvitationsListResponse> {
	return ApiClient.get('/recruiter/team/invitations/');
}

/**
 * Resend invitation email
 * Admin only
 */
export async function resendInvitation(
	invitationId: number
): Promise<ApiResponse<{ invitation: TeamInvitation }>> {
	return ApiClient.post(`/recruiter/team/invitations/${invitationId}/resend/`, {});
}

/**
 * Cancel pending invitation
 * Admin only
 */
export async function cancelInvitation(invitationId: number): Promise<ApiResponse> {
	return ApiClient.delete(`/recruiter/team/invitations/${invitationId}/cancel/`);
}

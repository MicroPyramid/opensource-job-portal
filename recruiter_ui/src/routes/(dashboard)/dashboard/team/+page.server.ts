/**
 * Team Management Page - Server Load & Actions
 * Allows company admins to manage team members and invitations
 */

import type { PageServerLoad, Actions } from './$types';
import { redirect, fail } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config/env';

export const load: PageServerLoad = async ({ parent, fetch }) => {
	// Get user data from parent layout
	const { user } = await parent();

	// Check if user is part of a company
	if (!user?.company) {
		throw redirect(302, '/dashboard/');
	}

	// Fetch team members and invitations in parallel
	try {
		const [teamResponse, invitationsResponse] = await Promise.all([
			fetch(`${API_BASE_URL}/recruiter/team/`),
			user.is_admin ? fetch(`${API_BASE_URL}/recruiter/team/invitations/`) : null
		]);

		const teamData = teamResponse.ok ? await teamResponse.json() : null;
		const invitationsData =
			invitationsResponse && invitationsResponse.ok ? await invitationsResponse.json() : null;

		return {
			user,
			team: teamData || { company: null, members: [], total_members: 0 },
			invitations: invitationsData || { invitations: [], total: 0, pending_count: 0 },
			error: !teamResponse.ok ? 'Failed to load team data' : null
		};
	} catch (error) {
		console.error('Error loading team data:', error);
		return {
			user,
			team: { company: null, members: [], total_members: 0 },
			invitations: { invitations: [], total: 0, pending_count: 0 },
			error: 'Failed to load team data'
		};
	}
};

export const actions: Actions = {
	// Invite new team member
	inviteMember: async ({ request, fetch }) => {
		const formData = await request.formData();

		const inviteData = {
			email: formData.get('email')?.toString(),
			job_title: formData.get('job_title')?.toString() || '',
			message: formData.get('message')?.toString() || ''
		};

		try {
			const response = await fetch(`${API_BASE_URL}/recruiter/team/invite/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(inviteData)
			});

			const result = await response.json();

			if (response.ok) {
				return {
					action: 'invite',
					success: true,
					message: result.message || 'Invitation sent successfully',
					invitation: result.invitation
				};
			} else {
				return fail(400, {
					action: 'invite',
					success: false,
					error: result.error || 'Failed to send invitation',
					errors: result
				});
			}
		} catch (error) {
			console.error('Error sending invitation:', error);
			return fail(500, {
				action: 'invite',
				success: false,
				error: 'An error occurred while sending the invitation'
			});
		}
	},

	// Update team member (role, admin status)
	updateMember: async ({ request, fetch }) => {
		const formData = await request.formData();
		const userId = formData.get('user_id')?.toString();

		if (!userId) {
			return fail(400, {
				action: 'update',
				success: false,
				error: 'User ID is required'
			});
		}

		const updateData: Record<string, any> = {};

		const jobTitle = formData.get('job_title')?.toString();
		if (jobTitle !== undefined && jobTitle !== null) {
			updateData.job_title = jobTitle;
		}

		const isAdmin = formData.get('is_admin')?.toString();
		if (isAdmin !== undefined && isAdmin !== null) {
			updateData.is_admin = isAdmin === 'true';
		}

		try {
			const response = await fetch(`${API_BASE_URL}/recruiter/team/${userId}/update/`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(updateData)
			});

			const result = await response.json();

			if (response.ok) {
				return {
					action: 'update',
					success: true,
					message: result.message || 'Team member updated successfully',
					user: result.user
				};
			} else {
				return fail(400, {
					action: 'update',
					success: false,
					error: result.error || 'Failed to update team member',
					errors: result
				});
			}
		} catch (error) {
			console.error('Error updating team member:', error);
			return fail(500, {
				action: 'update',
				success: false,
				error: 'An error occurred while updating the team member'
			});
		}
	},

	// Remove team member
	removeMember: async ({ request, fetch }) => {
		const formData = await request.formData();
		const userId = formData.get('user_id')?.toString();

		if (!userId) {
			return fail(400, {
				action: 'remove',
				success: false,
				error: 'User ID is required'
			});
		}

		try {
			const response = await fetch(`${API_BASE_URL}/recruiter/team/${userId}/remove/`, {
				method: 'DELETE'
			});

			const result = await response.json();

			if (response.ok) {
				return {
					action: 'remove',
					success: true,
					message: result.message || 'Team member removed successfully'
				};
			} else {
				return fail(400, {
					action: 'remove',
					success: false,
					error: result.error || 'Failed to remove team member'
				});
			}
		} catch (error) {
			console.error('Error removing team member:', error);
			return fail(500, {
				action: 'remove',
				success: false,
				error: 'An error occurred while removing the team member'
			});
		}
	},

	// Resend invitation
	resendInvitation: async ({ request, fetch }) => {
		const formData = await request.formData();
		const invitationId = formData.get('invitation_id')?.toString();

		if (!invitationId) {
			return fail(400, {
				action: 'resend',
				success: false,
				error: 'Invitation ID is required'
			});
		}

		try {
			const response = await fetch(
				`${API_BASE_URL}/recruiter/team/invitations/${invitationId}/resend/`,
				{
					method: 'POST'
				}
			);

			const result = await response.json();

			if (response.ok) {
				return {
					action: 'resend',
					success: true,
					message: result.message || 'Invitation resent successfully',
					invitation: result.invitation
				};
			} else {
				return fail(400, {
					action: 'resend',
					success: false,
					error: result.error || 'Failed to resend invitation'
				});
			}
		} catch (error) {
			console.error('Error resending invitation:', error);
			return fail(500, {
				action: 'resend',
				success: false,
				error: 'An error occurred while resending the invitation'
			});
		}
	},

	// Cancel invitation
	cancelInvitation: async ({ request, fetch }) => {
		const formData = await request.formData();
		const invitationId = formData.get('invitation_id')?.toString();

		if (!invitationId) {
			return fail(400, {
				action: 'cancel',
				success: false,
				error: 'Invitation ID is required'
			});
		}

		try {
			const response = await fetch(
				`${API_BASE_URL}/recruiter/team/invitations/${invitationId}/cancel/`,
				{
					method: 'DELETE'
				}
			);

			const result = await response.json();

			if (response.ok) {
				return {
					action: 'cancel',
					success: true,
					message: result.message || 'Invitation cancelled successfully'
				};
			} else {
				return fail(400, {
					action: 'cancel',
					success: false,
					error: result.error || 'Failed to cancel invitation'
				});
			}
		} catch (error) {
			console.error('Error cancelling invitation:', error);
			return fail(500, {
				action: 'cancel',
				success: false,
				error: 'An error occurred while cancelling the invitation'
			});
		}
	},

	// Toggle member active/inactive status
	toggleStatus: async ({ request, fetch }) => {
		const formData = await request.formData();
		const userId = formData.get('user_id')?.toString();

		if (!userId) {
			return fail(400, {
				action: 'toggleStatus',
				success: false,
				error: 'User ID is required'
			});
		}

		try {
			const response = await fetch(`${API_BASE_URL}/recruiter/team/${userId}/toggle-status/`, {
				method: 'POST'
			});

			const result = await response.json();

			if (response.ok) {
				return {
					action: 'toggleStatus',
					success: true,
					message: result.message || 'Member status updated successfully',
					user: result.user
				};
			} else {
				return fail(400, {
					action: 'toggleStatus',
					success: false,
					error: result.error || 'Failed to toggle member status'
				});
			}
		} catch (error) {
			console.error('Error toggling member status:', error);
			return fail(500, {
				action: 'toggleStatus',
				success: false,
				error: 'An error occurred while toggling member status'
			});
		}
	}
};

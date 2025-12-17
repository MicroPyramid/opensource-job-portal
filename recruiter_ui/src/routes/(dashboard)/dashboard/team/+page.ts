/**
 * TypeScript type definitions for Team Management
 */

export interface TeamMemberStats {
	jobs_posted: number;
	active_jobs: number;
	total_applicants: number;
}

export interface TeamMember {
	id: number;
	email: string;
	first_name: string;
	last_name: string | null;
	job_title: string | null;
	is_admin: boolean;
	date_joined: string;
	last_login: string | null;
	profile_pic: string | null;
	stats: TeamMemberStats;
}

export interface TeamInvitation {
	id: number;
	email: string;
	role_title: string;
	status: 'pending' | 'accepted' | 'expired' | 'cancelled';
	invited_by_name: string;
	invited_by_email: string;
	created_at: string;
	expires_at: string;
	days_remaining: number;
}

export interface CompanyBasic {
	id: number;
	name: string;
	slug: string;
	profile_pic: string | null;
	website: string | null;
	company_type: string;
	size: string;
}

export interface TeamData {
	company: CompanyBasic | null;
	members: TeamMember[];
	total_members: number;
}

export interface InvitationsData {
	invitations: TeamInvitation[];
	total: number;
	pending_count: number;
	expired_count?: number;
}

<script lang="ts">
	import {
		XCircle,
		Download,
		Mail,
		Phone,
		MapPin,
		Briefcase,
		Calendar,
		Award,
		GraduationCap,
		FileText,
		UserCheck,
		UserX,
		CheckCircle,
		Clock
	} from '@lucide/svelte';

	interface Props {
		applicant: any;
		jobId: number;
		onClose: () => void;
		onStatusUpdate: (applicantId: number, status: string, remarks?: string) => Promise<void>;
	}

	let { applicant, jobId, onClose, onStatusUpdate }: Props = $props();

	let activeTab = $state<'profile' | 'experience' | 'education' | 'skills'>('profile');
	let newStatus = $state(applicant.application?.status || 'Pending');
	let remarksText = $state(applicant.application?.remarks || '');
	let isUpdating = $state(false);

	async function handleStatusUpdate() {
		if (!applicant.application) return;

		isUpdating = true;
		try {
			await onStatusUpdate(applicant.application.id, newStatus, remarksText);
		} finally {
			isUpdating = false;
		}
	}

	function getStatusBadgeClass(status: string): string {
		switch (status) {
			case 'Pending':
				return 'bg-yellow-100 text-yellow-800';
			case 'Shortlisted':
				return 'bg-blue-100 text-blue-800';
			case 'Hired':
			case 'Selected':
				return 'bg-green-100 text-green-800';
			case 'Rejected':
				return 'bg-red-100 text-red-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}

	function formatDate(dateStr: string | null): string {
		if (!dateStr) return 'Present';
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
	}
</script>

<div
	class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
	onclick={onClose}
>
	<div
		class="bg-white rounded-lg max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col"
		onclick={(e) => e.stopPropagation()}
	>
		<!-- Header -->
		<div class="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-6 text-white">
			<div class="flex items-start justify-between mb-4">
				<div class="flex items-center gap-4">
					<div class="w-16 h-16 rounded-full bg-white flex items-center justify-center">
						{#if applicant.profile_pic}
							<img
								src={applicant.profile_pic}
								alt={`${applicant.first_name} ${applicant.last_name}`}
								class="w-full h-full rounded-full object-cover"
							/>
						{:else}
							<span class="text-2xl font-semibold text-blue-600">
								{applicant.first_name?.charAt(0).toUpperCase() || 'U'}
							</span>
						{/if}
					</div>
					<div>
						<h2 class="text-2xl font-bold">
							{applicant.first_name} {applicant.last_name}
						</h2>
						<p class="text-blue-100 mt-1">
							{applicant.experience?.display || 'Fresher'}
						</p>
					</div>
				</div>
				<button
					onclick={onClose}
					class="p-2 hover:bg-white/10 rounded-lg transition-colors"
				>
					<XCircle class="w-6 h-6" />
				</button>
			</div>

			<!-- Contact Info -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
				<div class="flex items-center gap-2">
					<Mail class="w-4 h-4" />
					{applicant.email}
				</div>
				{#if applicant.mobile}
					<div class="flex items-center gap-2">
						<Phone class="w-4 h-4" />
						{applicant.mobile}
					</div>
				{/if}
				{#if applicant.location?.current_city}
					<div class="flex items-center gap-2">
						<MapPin class="w-4 h-4" />
						{applicant.location.current_city}, {applicant.location.current_state || ''}
					</div>
				{/if}
			</div>
		</div>

		<!-- Tabs -->
		<div class="border-b border-gray-200 px-6">
			<div class="flex gap-6">
				{#each [
					{ id: 'profile', label: 'Profile' },
					{ id: 'experience', label: 'Experience' },
					{ id: 'education', label: 'Education' },
					{ id: 'skills', label: 'Skills' }
				] as tab}
					<button
						onclick={() => (activeTab = tab.id)}
						class="py-3 px-2 border-b-2 font-medium text-sm transition-colors {activeTab === tab.id
							? 'border-blue-600 text-blue-600'
							: 'border-transparent text-gray-600 hover:text-gray-900'}"
					>
						{tab.label}
					</button>
				{/each}
			</div>
		</div>

		<!-- Content -->
		<div class="flex-1 overflow-y-auto p-6">
			{#if activeTab === 'profile'}
				<div class="space-y-6">
					<!-- Application Status -->
					<div class="bg-gray-50 rounded-lg p-4">
						<h3 class="text-sm font-semibold text-gray-900 mb-3">Application Status</h3>
						{#if applicant.application}
							<div class="space-y-4">
								<div>
									<label class="block text-sm font-medium text-gray-700 mb-2">
										Current Status
									</label>
									<select
										bind:value={newStatus}
										class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									>
										<option value="Pending">Pending</option>
										<option value="Shortlisted">Shortlisted</option>
										<option value="Hired">Hired</option>
										<option value="Rejected">Rejected</option>
									</select>
								</div>

								<div>
									<label class="block text-sm font-medium text-gray-700 mb-2">
										Recruiter Remarks
									</label>
									<textarea
										bind:value={remarksText}
										rows="3"
										placeholder="Add notes about this candidate..."
										class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									></textarea>
								</div>

								<button
									onclick={handleStatusUpdate}
									disabled={isUpdating}
									class="w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
								>
									<CheckCircle class="w-4 h-4" />
									{isUpdating ? 'Updating...' : 'Update Status'}
								</button>

								<div class="text-xs text-gray-500">
									Applied on {new Date(applicant.application.applied_on).toLocaleDateString()}
								</div>
							</div>
						{/if}
					</div>

					<!-- Profile Description -->
					{#if applicant.profile_description}
						<div>
							<h3 class="text-sm font-semibold text-gray-900 mb-2">About</h3>
							<p class="text-gray-700 leading-relaxed">{applicant.profile_description}</p>
						</div>
					{/if}

					<!-- Basic Info -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						{#if applicant.current_salary}
							<div>
								<h4 class="text-sm font-medium text-gray-500 mb-1">Current Salary</h4>
								<p class="text-gray-900">{applicant.current_salary}</p>
							</div>
						{/if}
						{#if applicant.expected_salary}
							<div>
								<h4 class="text-sm font-medium text-gray-500 mb-1">Expected Salary</h4>
								<p class="text-gray-900">{applicant.expected_salary}</p>
							</div>
						{/if}
						{#if applicant.notice_period}
							<div>
								<h4 class="text-sm font-medium text-gray-500 mb-1">Notice Period</h4>
								<p class="text-gray-900">{applicant.notice_period}</p>
							</div>
						{/if}
						<div>
							<h4 class="text-sm font-medium text-gray-500 mb-1">Open to Relocation</h4>
							<p class="text-gray-900">{applicant.relocation ? 'Yes' : 'No'}</p>
						</div>
					</div>

					<!-- Resume -->
					{#if applicant.resume}
						<div>
							<a
								href={applicant.resume}
								target="_blank"
								class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
							>
								<Download class="w-4 h-4" />
								Download Resume
							</a>
						</div>
					{/if}
				</div>
			{:else if activeTab === 'experience'}
				<div class="space-y-4">
					{#if applicant.employment_history && applicant.employment_history.length > 0}
						{#each applicant.employment_history as job}
							<div class="bg-gray-50 rounded-lg p-4">
								<div class="flex items-start gap-3">
									<div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
										<Briefcase class="w-5 h-5 text-blue-600" />
									</div>
									<div class="flex-1">
										<h4 class="font-semibold text-gray-900">{job.designation}</h4>
										<p class="text-gray-700">{job.company}</p>
										<div class="flex items-center gap-2 text-sm text-gray-500 mt-1">
											<Calendar class="w-3 h-3" />
											{formatDate(job.from_date)} - {job.current_job
												? 'Present'
												: formatDate(job.to_date)}
										</div>
										{#if job.job_profile}
											<p class="text-sm text-gray-600 mt-2">{job.job_profile}</p>
										{/if}
									</div>
								</div>
							</div>
						{/each}
					{:else}
						<p class="text-gray-500 text-center py-8">No employment history added</p>
					{/if}
				</div>
			{:else if activeTab === 'education'}
				<div class="space-y-4">
					{#if applicant.education && applicant.education.length > 0}
						{#each applicant.education as edu}
							<div class="bg-gray-50 rounded-lg p-4">
								<div class="flex items-start gap-3">
									<div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
										<GraduationCap class="w-5 h-5 text-purple-600" />
									</div>
									<div class="flex-1">
										<h4 class="font-semibold text-gray-900">{edu.degree || 'Degree'}</h4>
										{#if edu.specialization}
											<p class="text-gray-700">{edu.specialization}</p>
										{/if}
										<p class="text-gray-600">{edu.institute || 'Institute'}</p>
										<div class="flex items-center gap-4 text-sm text-gray-500 mt-1">
											<div class="flex items-center gap-1">
												<Calendar class="w-3 h-3" />
												{formatDate(edu.from_date)} - {edu.current_education
													? 'Present'
													: formatDate(edu.to_date)}
											</div>
											{#if edu.score}
												<div>Score: {edu.score}</div>
											{/if}
										</div>
									</div>
								</div>
							</div>
						{/each}
					{:else}
						<p class="text-gray-500 text-center py-8">No education details added</p>
					{/if}

					<!-- Certifications -->
					{#if applicant.certifications && applicant.certifications.length > 0}
						<div class="mt-8">
							<h3 class="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
								<Award class="w-4 h-4" />
								Certifications
							</h3>
							<div class="space-y-3">
								{#each applicant.certifications as cert}
									<div class="bg-gray-50 rounded-lg p-4">
										<h4 class="font-semibold text-gray-900">{cert.name}</h4>
										<p class="text-gray-700 text-sm">{cert.organization}</p>
										{#if cert.credential_id}
											<p class="text-gray-600 text-sm mt-1">
												Credential ID: {cert.credential_id}
											</p>
										{/if}
										<div class="text-xs text-gray-500 mt-1">
											Issued: {formatDate(cert.issued_date)}
											{#if !cert.does_not_expire && cert.expiry_date}
												- Expires: {formatDate(cert.expiry_date)}
											{/if}
										</div>
										{#if cert.credential_url}
											<a
												href={cert.credential_url}
												target="_blank"
												class="text-blue-600 hover:text-blue-700 text-sm mt-2 inline-block"
											>
												View Credential →
											</a>
										{/if}
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{:else if activeTab === 'skills'}
				<div class="space-y-6">
					{#if applicant.skills && applicant.skills.length > 0}
						<div>
							<h3 class="text-sm font-semibold text-gray-900 mb-4">Technical Skills</h3>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
								{#each applicant.skills as skill}
									<div
										class="bg-gray-50 rounded-lg p-3 {skill.is_major
											? 'border-2 border-blue-200'
											: ''}"
									>
										<div class="flex items-center justify-between mb-2">
											<h4 class="font-medium text-gray-900">{skill.name}</h4>
											{#if skill.is_major}
												<span class="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
													Primary
												</span>
											{/if}
										</div>
										<div class="text-sm text-gray-600 space-y-1">
											{#if skill.years || skill.months}
												<div>
													Experience: {skill.years || 0}y {skill.months || 0}m
												</div>
											{/if}
											{#if skill.proficiency}
												<div>Proficiency: {skill.proficiency}</div>
											{/if}
											{#if skill.last_used}
												<div>Last used: {formatDate(skill.last_used)}</div>
											{/if}
										</div>
									</div>
								{/each}
							</div>
						</div>
					{:else}
						<p class="text-gray-500 text-center py-8">No skills added</p>
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>

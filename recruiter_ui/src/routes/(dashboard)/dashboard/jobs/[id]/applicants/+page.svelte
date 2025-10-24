<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { enhance } from '$app/forms';
	import {
		Search,
		Filter,
		Users,
		ArrowLeft,
		Download,
		Mail,
		Phone,
		MapPin,
		Briefcase,
		UserCheck,
		UserX,
		Clock,
		CheckCircle,
		XCircle,
		Eye
	} from '@lucide/svelte';
	import { invalidateAll } from '$app/navigation';
	import { API_BASE_URL } from '$lib/config/env';
	import ApplicantDetailModal from '$lib/components/recruiter/ApplicantDetailModal.svelte';

	let { data } = $props();

	let searchQuery = $state(data.filters.search);
	let selectedFilter = $state(data.filters.status);
	let selectedApplicant = $state<any>(null);
	let showDetailModal = $state(false);
	let submittingAction = $state<number | null>(null);
	let remarksText = $state('');

	const statusFilters = [
		{ value: 'all', label: 'All Applicants', count: data.totalApplicants },
		{ value: 'Pending', label: 'Pending', count: data.stats.pending },
		{ value: 'Shortlisted', label: 'Shortlisted', count: data.stats.shortlisted },
		{ value: 'Hired', label: 'Hired', count: data.stats.selected },
		{ value: 'Rejected', label: 'Rejected', count: data.stats.rejected }
	];

	function updateFilters() {
		const params = new URLSearchParams();

		if (selectedFilter !== 'all') {
			params.set('status', selectedFilter);
		}

		if (searchQuery.trim()) {
			params.set('search', searchQuery.trim());
		}

		goto(`?${params.toString()}`, { keepFocus: true, noScroll: true });
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

	function getStatusIcon(status: string) {
		switch (status) {
			case 'Pending':
				return Clock;
			case 'Shortlisted':
				return UserCheck;
			case 'Hired':
			case 'Selected':
				return CheckCircle;
			case 'Rejected':
				return UserX;
			default:
				return Users;
		}
	}

	async function viewApplicantDetail(applicantId: number) {
		// Fetch detailed applicant profile
		const accessToken = document.cookie
			.split('; ')
			.find((row) => row.startsWith('access_token='))
			?.split('=')[1];

		try {
			const response = await fetch(
				`${API_BASE_URL}/recruiter/jobs/${data.job.id}/applicants/${applicantId}/`,
				{
					headers: {
						Authorization: `Bearer ${accessToken}`
					}
				}
			);

			if (response.ok) {
				selectedApplicant = await response.json();
				showDetailModal = true;
			} else {
				console.error('Failed to fetch applicant details');
				alert('Failed to load applicant details');
			}
		} catch (err) {
			console.error('Failed to fetch applicant details:', err);
			alert('Failed to load applicant details');
		}
	}

	function closeDetailModal() {
		showDetailModal = false;
		selectedApplicant = null;
		remarksText = '';
	}

	async function updateApplicantStatus(applicantId: number, newStatus: string, remarks?: string) {
		submittingAction = applicantId;

		const formData = new FormData();
		formData.append('applicantId', applicantId.toString());
		formData.append('status', newStatus);
		if (remarks) {
			formData.append('remarks', remarks);
		}

		try {
			const response = await fetch('?/updateStatus', {
				method: 'POST',
				body: formData
			});

			if (response.ok) {
				await invalidateAll();
				closeDetailModal();
			} else {
				alert('Failed to update applicant status');
			}
		} catch (err) {
			console.error('Failed to update status:', err);
			alert('Failed to update applicant status');
		} finally {
			submittingAction = null;
		}
	}
</script>

<svelte:head>
	<title>Applicants - {data.job.title} - PeelJobs</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div class="flex items-center gap-4">
			<a
				href="/dashboard/jobs/"
				class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
				title="Back to Jobs"
			>
				<ArrowLeft class="w-5 h-5" />
			</a>
			<div>
				<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Applicants</h1>
				<p class="text-gray-600 mt-1">{data.job.title}</p>
			</div>
		</div>
		<div class="flex items-center gap-2 text-sm text-gray-600">
			<Users class="w-4 h-4" />
			<span class="font-medium">{data.totalApplicants} total applicants</span>
		</div>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
		{#each statusFilters.slice(1) as filter}
			<button
				onclick={() => {
					selectedFilter = filter.value;
					updateFilters();
				}}
				class="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow text-left {selectedFilter ===
				filter.value
					? 'ring-2 ring-blue-500'
					: ''}"
			>
				<div class="flex items-center justify-between mb-2">
					<span class="text-sm text-gray-600">{filter.label}</span>
					<svelte:component this={getStatusIcon(filter.value)} class="w-4 h-4 text-gray-400" />
				</div>
				<div class="text-2xl font-bold text-gray-900">{filter.count}</div>
			</button>
		{/each}
	</div>

	<!-- Filters -->
	<div class="bg-white rounded-lg border border-gray-200 p-4">
		<form
			onsubmit={(e) => {
				e.preventDefault();
				updateFilters();
			}}
			class="flex flex-col md:flex-row gap-4"
		>
			<!-- Search -->
			<div class="flex-1 relative">
				<Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
				<input
					type="text"
					bind:value={searchQuery}
					onchange={updateFilters}
					placeholder="Search applicants by name or email..."
					class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<!-- Status Filter -->
			<div class="relative">
				<Filter class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
				<select
					bind:value={selectedFilter}
					onchange={updateFilters}
					class="pl-9 pr-8 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none cursor-pointer"
				>
					{#each statusFilters as option}
						<option value={option.value}>{option.label} ({option.count})</option>
					{/each}
				</select>
			</div>
		</form>
	</div>

	<!-- Applicants List -->
	{#if data.applications.length === 0}
		<div class="bg-white rounded-lg border border-gray-200 p-12 text-center">
			<Users class="w-12 h-12 text-gray-400 mx-auto mb-4" />
			<h3 class="text-lg font-semibold text-gray-900 mb-2">No applicants found</h3>
			<p class="text-gray-600">
				{searchQuery || selectedFilter !== 'all'
					? 'Try adjusting your filters'
					: 'No one has applied to this job yet'}
			</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-4">
			{#each data.applications as application}
				{@const applicant = application.applicant}
				<div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
					<div class="flex items-start justify-between gap-4">
						<!-- Applicant Info -->
						<div class="flex items-start gap-4 flex-1">
							<!-- Avatar -->
							<div class="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
								{#if applicant.profile_pic}
									<img
										src={applicant.profile_pic}
										alt={applicant.name}
										class="w-full h-full rounded-full object-cover"
									/>
								{:else}
									<span class="text-xl font-semibold text-blue-600">
										{applicant.name.charAt(0).toUpperCase()}
									</span>
								{/if}
							</div>

							<!-- Details -->
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-3 mb-2">
									<h3 class="text-lg font-semibold text-gray-900">{applicant.name}</h3>
									<span class="px-2 py-1 text-xs font-medium rounded {getStatusBadgeClass(application.status)}">
										{application.status}
									</span>
								</div>

								<div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600 mb-3">
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
									<div class="flex items-center gap-2">
										<Briefcase class="w-4 h-4" />
										{applicant.experience}
									</div>
									{#if applicant.current_location}
										<div class="flex items-center gap-2">
											<MapPin class="w-4 h-4" />
											{applicant.current_location}
										</div>
									{/if}
								</div>

								<div class="text-xs text-gray-500">
									Applied {application.applied_time_ago}
								</div>

								{#if application.remarks}
									<div class="mt-3 p-3 bg-gray-50 rounded-lg">
										<p class="text-sm text-gray-700"><strong>Remarks:</strong> {application.remarks}</p>
									</div>
								{/if}
							</div>
						</div>

						<!-- Actions -->
						<div class="flex flex-col gap-2">
							<button
								onclick={() => viewApplicantDetail(application.id)}
								class="inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
							>
								<Eye class="w-4 h-4" />
								View Profile
							</button>

							{#if applicant.resume_url}
								<a
									href={applicant.resume_url}
									target="_blank"
									class="inline-flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
								>
									<Download class="w-4 h-4" />
									Resume
								</a>
							{/if}

							{#if application.status === 'Pending'}
								<button
									onclick={() => updateApplicantStatus(application.id, 'Shortlisted')}
									disabled={submittingAction === application.id}
									class="inline-flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium disabled:opacity-50"
								>
									<UserCheck class="w-4 h-4" />
									Shortlist
								</button>

								<button
									onclick={() => updateApplicantStatus(application.id, 'Rejected')}
									disabled={submittingAction === application.id}
									class="inline-flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium disabled:opacity-50"
								>
									<UserX class="w-4 h-4" />
									Reject
								</button>
							{/if}

							{#if application.status === 'Shortlisted'}
								<button
									onclick={() => updateApplicantStatus(application.id, 'Hired')}
									disabled={submittingAction === application.id}
									class="inline-flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium disabled:opacity-50"
								>
									<CheckCircle class="w-4 h-4" />
									Mark Hired
								</button>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Detail Modal -->
{#if showDetailModal && selectedApplicant}
	<ApplicantDetailModal
		applicant={selectedApplicant}
		jobId={data.job.id}
		onClose={closeDetailModal}
		onStatusUpdate={updateApplicantStatus}
	/>
{/if}

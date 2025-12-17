<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/stores';
	import { enhance } from '$app/forms';
	import {
		Plus,
		Search,
		Filter,
		Eye,
		Users,
		Edit,
		XCircle,
		ExternalLink,
		Calendar,
		MapPin,
		Briefcase,
		Send,
		Archive,
		Copy
	} from '@lucide/svelte';
	import type { JobStatus } from '$lib/types';

	// Get data from server-side load function
	let { data } = $props();

	let searchQuery = $state(data.filters.search);
	let selectedFilter = $state<JobStatus | 'all'>(data.filters.status as JobStatus | 'all');
	let viewMode = $state<'grid' | 'list'>('list');
	let submittingAction = $state<number | null>(null);

	const filterOptions = [
		{ value: 'all', label: 'All Jobs' },
		{ value: 'Live', label: 'Active' },
		{ value: 'Draft', label: 'Drafts' },
		{ value: 'Disabled', label: 'Closed' },
		{ value: 'Expired', label: 'Expired' }
	];

	// Update URL when filters change
	function updateFilters() {
		const params = new URLSearchParams();
		params.set('page', '1'); // Reset to page 1 on filter change

		if (selectedFilter !== 'all') {
			params.set('status', selectedFilter);
		}

		if (searchQuery.trim()) {
			params.set('search', searchQuery.trim());
		}

		goto(`?${params.toString()}`, { keepFocus: true, noScroll: true });
	}

	// Navigate to page
	function goToPage(pageNum: number) {
		const params = new URLSearchParams($page.url.searchParams);
		params.set('page', pageNum.toString());
		goto(`?${params.toString()}`, { keepFocus: true, noScroll: true });
	}

	function formatDate(dateString?: string): string {
		if (!dateString) return 'N/A';
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function getStatusBadgeClass(status: JobStatus): string {
		switch (status) {
			case 'Live':
				return 'bg-green-100 text-green-800';
			case 'Draft':
				return 'bg-gray-100 text-gray-800';
			case 'Disabled':
				return 'bg-red-100 text-red-800';
			case 'Expired':
				return 'bg-orange-100 text-orange-800';
			default:
				return 'bg-blue-100 text-blue-800';
		}
	}

	async function handleDelete(jobId: number, jobTitle: string) {
		if (!confirm(`Are you sure you want to delete "${jobTitle}"?`)) {
			return;
		}

		submittingAction = jobId;

		// Use fetch to submit delete action
		const formData = new FormData();
		formData.append('jobId', jobId.toString());

		try {
			const response = await fetch('?/delete', {
				method: 'POST',
				body: formData
			});

			const result = await response.json();

			if (result.type === 'success') {
				// Refresh the page data
				await invalidateAll();
			} else {
				alert(result.data?.error || 'Failed to delete job');
			}
		} catch (err: any) {
			alert(err.message || 'Failed to delete job');
		} finally {
			submittingAction = null;
		}
	}
</script>

<svelte:head>
	<title>Jobs - PeelJobs Recruiter</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Jobs</h1>
			<p class="text-gray-600 mt-1">Manage your job postings</p>
		</div>
		<div class="flex gap-3">
			<a
				href="/dashboard/jobs/inactive/"
				class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
			>
				<Archive class="w-4 h-4" />
				Inactive Jobs
			</a>
			<a
				href="/dashboard/jobs/new/"
				class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
			>
				<Plus class="w-4 h-4" />
				Post New Job
			</a>
		</div>
	</div>

	<!-- Filters and Search -->
	<div class="bg-white rounded-lg border border-gray-200 p-4">
		<form onsubmit={(e) => { e.preventDefault(); updateFilters(); }} class="flex flex-col md:flex-row gap-4">
			<!-- Search -->
			<div class="flex-1 relative">
				<Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
				<input
					type="text"
					bind:value={searchQuery}
					onchange={updateFilters}
					placeholder="Search jobs by title..."
					class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<!-- Filter -->
			<div class="flex items-center gap-3">
				<div class="relative">
					<Filter class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
					<select
						bind:value={selectedFilter}
						onchange={updateFilters}
						class="pl-9 pr-8 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none cursor-pointer"
					>
						{#each filterOptions as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<div class="flex border border-gray-300 rounded-lg overflow-hidden">
					<button
						type="button"
						onclick={() => (viewMode = 'list')}
						class="px-3 py-2 {viewMode === 'list' ? 'bg-gray-100' : 'bg-white'} hover:bg-gray-50"
						aria-label="List view"
					>
						<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
								clip-rule="evenodd"
							/>
						</svg>
					</button>
					<button
						type="button"
						onclick={() => (viewMode = 'grid')}
						class="px-3 py-2 {viewMode === 'grid' ? 'bg-gray-100' : 'bg-white'} hover:bg-gray-50"
						aria-label="Grid view"
					>
						<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
							<path
								d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM13 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2h-2z"
							/>
						</svg>
					</button>
				</div>
			</div>
		</form>
	</div>

	<!-- Empty State -->
	{#if data.jobs.length === 0}
		<div class="bg-white rounded-lg border border-gray-200 p-12 text-center">
			<Briefcase class="w-12 h-12 text-gray-400 mx-auto mb-4" />
			<h3 class="text-lg font-semibold text-gray-900 mb-2">No jobs found</h3>
			<p class="text-gray-600 mb-6">
				{searchQuery || selectedFilter !== 'all'
					? 'Try adjusting your filters or search query'
					: 'Get started by posting your first job'}
			</p>
			<a
				href="/dashboard/jobs/new/"
				class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				<Plus class="w-4 h-4" />
				Post New Job
			</a>
		</div>
	{:else if viewMode === 'list'}
		<!-- List View -->
		<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead class="bg-gray-50 border-b border-gray-200">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Job Details
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Status
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Posted
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Expires
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Performance
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Actions
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-200">
						{#each data.jobs as job}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4">
									<div class="flex items-start gap-3">
										<div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
											<Briefcase class="w-5 h-5 text-blue-600" />
										</div>
										<div>
											<a
												href="/dashboard/jobs/{job.id}/{job.status === 'Draft' ? '' : 'applicants/'}"
												class="font-medium text-gray-900 hover:text-blue-600"
											>
												{job.title}
											</a>
											<div class="flex items-center gap-3 mt-1 text-sm text-gray-500">
												<span>{job.company_name}</span>
												<span>•</span>
												<span class="flex items-center gap-1">
													<MapPin class="w-3 h-3" />
													{job.location_display}
												</span>
												<span>•</span>
												<span>{job.job_type}</span>
											</div>
											{#if job.is_expiring_soon}
												<span class="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-orange-100 text-orange-800 text-xs font-medium rounded">
													<Calendar class="w-3 h-3" />
													Expires in {job.days_until_expiry} days
												</span>
											{/if}
										</div>
									</div>
								</td>
								<td class="px-6 py-4">
									<span class="inline-flex px-2 py-1 text-xs font-medium rounded {getStatusBadgeClass(job.status)}">
										{job.status}
									</span>
								</td>
								<td class="px-6 py-4 text-sm text-gray-600">
									{job.time_ago}
								</td>
								<td class="px-6 py-4 text-sm text-gray-600">
									{#if job.days_until_expiry !== null && job.days_until_expiry !== undefined}
										{job.days_until_expiry} days left
									{:else}
										Expired
									{/if}
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-4 text-sm">
										<div class="flex items-center gap-1 text-gray-600">
											<Eye class="w-4 h-4" />
											{job.views_count.toLocaleString()}
										</div>
										<a
											href="/dashboard/jobs/{job.id}/applicants/"
											class="flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium"
										>
											<Users class="w-4 h-4" />
											{job.applicants_count}
										</a>
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-2">
										{#if job.status === 'Draft'}
											<form method="POST" action="?/publish" use:enhance={() => {
												submittingAction = job.id;
												return async ({ update }) => {
													await update();
													submittingAction = null;
												};
											}}>
												<input type="hidden" name="jobId" value={job.id} />
												<button
													type="submit"
													disabled={submittingAction === job.id}
													class="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors disabled:opacity-50"
													title="Publish"
												>
													<Send class="w-4 h-4" />
												</button>
											</form>
										{/if}
										{#if job.status === 'Live'}
											<form method="POST" action="?/close" use:enhance={() => {
												submittingAction = job.id;
												return async ({ update }) => {
													await update();
													submittingAction = null;
												};
											}}>
												<input type="hidden" name="jobId" value={job.id} />
												<button
													type="submit"
													disabled={submittingAction === job.id}
													class="p-2 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors disabled:opacity-50"
													title="Close"
												>
													<Archive class="w-4 h-4" />
												</button>
											</form>
										{/if}
										{#if job.status === 'Draft'}
											<a
												href="/dashboard/jobs/{job.id}/edit/"
												class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
												title="Edit"
											>
												<Edit class="w-4 h-4" />
											</a>
										{/if}
										<a
											href="/dashboard/jobs/{job.id}/"
											class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
											title="View"
										>
											<ExternalLink class="w-4 h-4" />
										</a>
										<a
											href="/dashboard/jobs/new/?copy_from={job.id}"
											class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
											title="Copy Job"
										>
											<Copy class="w-4 h-4" />
										</a>
										{#if job.status === 'Draft'}
											<button
												onclick={() => handleDelete(job.id, job.title)}
												disabled={submittingAction === job.id}
												class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
												title="Delete"
											>
												<XCircle class="w-4 h-4" />
											</button>
										{/if}
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{:else}
		<!-- Grid View -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each data.jobs as job}
				<div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
					<div class="flex items-start justify-between mb-4">
						<div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
							<Briefcase class="w-6 h-6 text-blue-600" />
						</div>
						<span class="px-2 py-1 text-xs font-medium rounded {getStatusBadgeClass(job.status)}">
							{job.status}
						</span>
					</div>

					<a
						href="/dashboard/jobs/{job.id}/{job.status === 'Draft' ? '' : 'applicants/'}"
						class="block mb-3"
					>
						<h3 class="text-lg font-semibold text-gray-900 hover:text-blue-600 line-clamp-2">
							{job.title}
						</h3>
					</a>

					<div class="space-y-2 text-sm text-gray-600 mb-4">
						<div class="flex items-center gap-2">
							<MapPin class="w-4 h-4" />
							{job.location_display}
						</div>
						<div class="flex items-center gap-2">
							<Calendar class="w-4 h-4" />
							Posted {job.time_ago}
						</div>
					</div>

					{#if job.is_expiring_soon}
						<div class="mb-4">
							<span class="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-800 text-xs font-medium rounded">
								<Calendar class="w-3 h-3" />
								Expires in {job.days_until_expiry} days
							</span>
						</div>
					{/if}

					<div class="flex items-center justify-between mb-4 pt-4 border-t border-gray-200">
						<div class="flex items-center gap-1 text-sm text-gray-600">
							<Eye class="w-4 h-4" />
							{job.views_count.toLocaleString()}
						</div>
						<a
							href="/dashboard/jobs/{job.id}/applicants/"
							class="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 font-medium"
						>
							<Users class="w-4 h-4" />
							{job.applicants_count} applicants
						</a>
					</div>

					<div class="flex items-center gap-2">
						{#if job.status === 'Draft'}
							<form method="POST" action="?/publish" use:enhance class="flex-1">
								<input type="hidden" name="jobId" value={job.id} />
								<button
									type="submit"
									class="w-full inline-flex items-center justify-center gap-2 px-3 py-2 bg-green-600 rounded-lg text-sm font-medium text-white hover:bg-green-700 transition-colors"
								>
									<Send class="w-4 h-4" />
									Publish
								</button>
							</form>
						{:else if job.status === 'Live'}
							<form method="POST" action="?/close" use:enhance class="flex-1">
								<input type="hidden" name="jobId" value={job.id} />
								<button
									type="submit"
									class="w-full inline-flex items-center justify-center gap-2 px-3 py-2 bg-orange-600 rounded-lg text-sm font-medium text-white hover:bg-orange-700 transition-colors"
								>
									<Archive class="w-4 h-4" />
									Close
								</button>
							</form>
						{/if}
						{#if job.status === 'Draft'}
							<a
								href="/dashboard/jobs/{job.id}/edit/"
								class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
							>
								<Edit class="w-4 h-4" />
								Edit
							</a>
						{/if}
						<a
							href="/dashboard/jobs/{job.id}/"
							class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
						>
							View
						</a>
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Pagination -->
	{#if data.jobs.length > 0 && (data.next || data.previous)}
		<div class="flex items-center justify-between bg-white rounded-lg border border-gray-200 px-6 py-4">
			<div class="text-sm text-gray-600">
				Showing {data.jobs.length} of {data.count} jobs
			</div>
			<div class="flex items-center gap-2">
				<button
					onclick={() => goToPage(data.currentPage - 1)}
					disabled={!data.previous}
					class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
				>
					Previous
				</button>
				<span class="text-sm text-gray-600">Page {data.currentPage}</span>
				<button
					onclick={() => goToPage(data.currentPage + 1)}
					disabled={!data.next}
					class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
				>
					Next
				</button>
			</div>
		</div>
	{/if}
</div>

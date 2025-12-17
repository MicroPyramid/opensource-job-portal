<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/stores';
	import { enhance } from '$app/forms';
	import {
		Search,
		Filter,
		Eye,
		Users,
		Archive,
		XCircle,
		Calendar,
		MapPin,
		Briefcase,
		RotateCcw,
		Trash2,
		ArrowLeft,
		AlertCircle
	} from '@lucide/svelte';
	import type { JobStatus } from '$lib/types';

	let { data } = $props();

	let searchQuery = $state(data.filters.search);
	let selectedFilter = $state(data.filters.status);
	let submittingAction = $state<number | null>(null);

	const filterOptions = [
		{ value: 'all', label: 'All Inactive' },
		{ value: 'Disabled', label: 'Closed' },
		{ value: 'Expired', label: 'Expired' }
	];

	function updateFilters() {
		const params = new URLSearchParams();
		params.set('page', '1');

		if (selectedFilter !== 'all') {
			params.set('status', selectedFilter);
		}

		if (searchQuery.trim()) {
			params.set('search', searchQuery.trim());
		}

		goto(`?${params.toString()}`, { keepFocus: true, noScroll: true });
	}

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
			case 'Disabled':
				return 'bg-red-100 text-red-800';
			case 'Expired':
				return 'bg-orange-100 text-orange-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}
</script>

<svelte:head>
	<title>Inactive Jobs - PeelJobs</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div class="flex items-center gap-4">
			<a
				href="/dashboard/jobs/"
				class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
				title="Back to All Jobs"
			>
				<ArrowLeft class="w-5 h-5" />
			</a>
			<div>
				<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Inactive Jobs</h1>
				<p class="text-gray-600 mt-1">Closed and expired job postings</p>
			</div>
		</div>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
					<Archive class="w-5 h-5 text-gray-600" />
				</div>
				<div>
					<div class="text-2xl font-bold text-gray-900">{data.stats.total}</div>
					<div class="text-sm text-gray-600">Total Inactive</div>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
					<XCircle class="w-5 h-5 text-red-600" />
				</div>
				<div>
					<div class="text-2xl font-bold text-gray-900">{data.stats.disabled}</div>
					<div class="text-sm text-gray-600">Closed</div>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
					<AlertCircle class="w-5 h-5 text-orange-600" />
				</div>
				<div>
					<div class="text-2xl font-bold text-gray-900">{data.stats.expired}</div>
					<div class="text-sm text-gray-600">Expired</div>
				</div>
			</div>
		</div>
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
					placeholder="Search inactive jobs..."
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
					{#each filterOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>
		</form>
	</div>

	<!-- Jobs List -->
	{#if data.jobs.length === 0}
		<div class="bg-white rounded-lg border border-gray-200 p-12 text-center">
			<Archive class="w-12 h-12 text-gray-400 mx-auto mb-4" />
			<h3 class="text-lg font-semibold text-gray-900 mb-2">No inactive jobs found</h3>
			<p class="text-gray-600">
				{searchQuery || selectedFilter !== 'all'
					? 'Try adjusting your filters'
					: 'All your closed and expired jobs will appear here'}
			</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-4">
			{#each data.jobs as job}
				<div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
					<div class="flex items-start justify-between gap-4">
						<!-- Job Info -->
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-3 mb-2">
								<h3 class="text-lg font-semibold text-gray-900 truncate">{job.title}</h3>
								<span class="px-2 py-1 text-xs font-medium rounded {getStatusBadgeClass(job.status)}">
									{job.status}
								</span>
							</div>

							<div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-gray-600 mb-3">
								<div class="flex items-center gap-2">
									<Briefcase class="w-4 h-4" />
									<span class="capitalize">{job.job_type.replace('-', ' ')}</span>
								</div>
								<div class="flex items-center gap-2">
									<MapPin class="w-4 h-4" />
									<span>{job.location_display || 'Remote'}</span>
								</div>
								<div class="flex items-center gap-2">
									<Calendar class="w-4 h-4" />
									<span>Posted {formatDate(job.published_on)}</span>
								</div>
							</div>

							<div class="flex items-center gap-4 text-sm">
								<div class="flex items-center gap-2">
									<Users class="w-4 h-4 text-gray-400" />
									<span class="text-gray-600">{job.applicants_count} applicants</span>
								</div>
								<div class="flex items-center gap-2">
									<Eye class="w-4 h-4 text-gray-400" />
									<span class="text-gray-600">{job.views_count} views</span>
								</div>
							</div>
						</div>

						<!-- Actions -->
						<div class="flex flex-col gap-2">
							<a
								href="/dashboard/jobs/{job.id}/"
								class="inline-flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
							>
								<Eye class="w-4 h-4" />
								View
							</a>

							<form
								method="POST"
								action="?/reactivate"
								use:enhance={() => {
									submittingAction = job.id;
									return async ({ result }) => {
										submittingAction = null;
										if (result.type === 'success') {
											await invalidateAll();
										}
									};
								}}
							>
								<input type="hidden" name="jobId" value={job.id} />
								<button
									type="submit"
									disabled={submittingAction === job.id}
									class="w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium disabled:opacity-50"
								>
									<RotateCcw class="w-4 h-4" />
									Reactivate
								</button>
							</form>

							<form
								method="POST"
								action="?/delete"
								use:enhance={() => {
									if (!confirm('Are you sure you want to permanently delete this job?')) {
										return () => {};
									}
									submittingAction = job.id;
									return async ({ result }) => {
										submittingAction = null;
										if (result.type === 'success') {
											await invalidateAll();
										}
									};
								}}
							>
								<input type="hidden" name="jobId" value={job.id} />
								<button
									type="submit"
									disabled={submittingAction === job.id}
									class="w-full inline-flex items-center justify-center gap-2 px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium disabled:opacity-50"
								>
									<Trash2 class="w-4 h-4" />
									Delete
								</button>
							</form>
						</div>
					</div>
				</div>
			{/each}
		</div>

		<!-- Pagination -->
		{#if data.count > 20}
			<div class="flex items-center justify-between bg-white rounded-lg border border-gray-200 px-4 py-3">
				<div class="text-sm text-gray-700">
					Showing page <span class="font-medium">{data.currentPage}</span> of
					<span class="font-medium">{Math.ceil(data.count / 20)}</span>
				</div>

				<div class="flex gap-2">
					{#if data.previous}
						<button
							onclick={() => goToPage(data.currentPage - 1)}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm"
						>
							Previous
						</button>
					{/if}

					{#if data.next}
						<button
							onclick={() => goToPage(data.currentPage + 1)}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm"
						>
							Next
						</button>
					{/if}
				</div>
			</div>
		{/if}
	{/if}
</div>

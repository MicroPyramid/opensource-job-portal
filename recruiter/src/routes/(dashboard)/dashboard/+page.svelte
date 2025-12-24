<script lang="ts">
	import {
		Briefcase,
		Users,
		Clock,
		AlertCircle,
		FileText,
		Plus,
		TrendingUp,
		TrendingDown,
		CheckCircle
	} from '@lucide/svelte';
	import type { PageData } from './$types';

	export let data: PageData;

	// Build stats array with NEW metrics
	$: stats = data.stats
		? [
				{
					label: 'Active Jobs',
					value: data.stats.live_jobs.toString(),
					icon: Briefcase,
					trend: `${data.stats.draft_jobs} drafts`,
					trendPositive: true
				},
				{
					label: 'Total Applicants',
					value: data.stats.total_applicants.toString(),
					icon: Users,
					trend: `${data.stats.new_applicants} new (30d)`,
					trendPositive: true,
					change: data.stats.applicants_trend
				},
				{
					label: 'Pending Review',
					value: data.pipeline ? data.pipeline.pending.toString() : '0',
					icon: Clock,
					trend: 'Need action',
					trendPositive: false
				},
				{
					label: 'Hired',
					value: data.pipeline ? data.pipeline.hired.toString() : '0',
					icon: CheckCircle,
					trend: data.pipeline ? `${data.pipeline.conversion_rate}% conversion` : '0%',
					trendPositive: true
				}
			]
		: [];

	// Map recent jobs with new fields
	$: topJobs = (data.recentJobs || []).map((job: any) => ({
		id: job.id,
		title: job.title,
		applications: job.applicants_count || 0,
		newApplications: job.new_applicants || 0,
		pendingReview: job.pending_review || 0,
		status: job.status
	}));

	function getJobStatusColor(status: string): string {
		const colors: Record<string, string> = {
			Live: 'bg-green-100 text-green-800',
			Draft: 'bg-gray-100 text-gray-800',
			Disabled: 'bg-red-100 text-red-800',
			Expired: 'bg-orange-100 text-orange-800'
		};
		return colors[status] || 'bg-gray-100 text-gray-800';
	}
</script>

<svelte:head>
	<title>Dashboard - PeelJobs Recruiter</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Dashboard</h1>
			<p class="text-gray-600 mt-1">Welcome back! Here's what's happening today.</p>
		</div>
		<a
			href="/dashboard/jobs/new/"
			class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
		>
			<Plus class="w-4 h-4" />
			Post New Job
		</a>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
		{#each stats as stat}
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<div class="flex items-start justify-between">
					<div class="flex-1">
						<p class="text-sm font-medium text-gray-600">{stat.label}</p>
						<p class="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
						<div class="flex items-center gap-1 mt-2">
							{#if stat.change}
								{#if stat.change.startsWith('+')}
									<TrendingUp class="w-4 h-4 text-green-600" />
									<span class="text-xs font-medium text-green-600">{stat.change}</span>
								{:else if stat.change.startsWith('-')}
									<TrendingDown class="w-4 h-4 text-red-600" />
									<span class="text-xs font-medium text-red-600">{stat.change}</span>
								{:else}
									<span class="text-xs font-medium text-gray-600">{stat.change}</span>
								{/if}
							{:else}
								<p class="text-xs {stat.trendPositive ? 'text-green-600' : 'text-orange-600'} font-medium">
									{stat.trend}
								</p>
							{/if}
						</div>
					</div>
					<div class="w-12 h-12 rounded-lg {stat.trendPositive ? 'bg-blue-100' : 'bg-orange-100'} flex items-center justify-center">
						<stat.icon class="w-6 h-6 {stat.trendPositive ? 'text-blue-600' : 'text-orange-600'}" />
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Hiring Pipeline Overview -->
	{#if data.pipeline}
		<div class="bg-white rounded-lg border border-gray-200 p-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Hiring Pipeline</h2>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
				<div class="text-center">
					<div class="text-3xl font-bold text-blue-600">{data.pipeline.pending}</div>
					<div class="text-sm text-gray-600 mt-1">Pending Review</div>
				</div>
				<div class="text-center">
					<div class="text-3xl font-bold text-purple-600">{data.pipeline.shortlisted}</div>
					<div class="text-sm text-gray-600 mt-1">Shortlisted</div>
				</div>
				<div class="text-center">
					<div class="text-3xl font-bold text-green-600">{data.pipeline.hired}</div>
					<div class="text-sm text-gray-600 mt-1">Hired</div>
				</div>
				<div class="text-center">
					<div class="text-3xl font-bold text-gray-600">{data.pipeline.rejected}</div>
					<div class="text-sm text-gray-600 mt-1">Rejected</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Recent Jobs -->
	<div class="bg-white rounded-lg border border-gray-200">
		<div class="p-6 border-b border-gray-200">
			<div class="flex items-center justify-between">
				<h2 class="text-lg font-semibold text-gray-900">Recent Jobs</h2>
				<a href="/dashboard/jobs/" class="text-sm text-blue-600 hover:text-blue-700 font-medium">
					View all jobs
				</a>
			</div>
		</div>
		{#if topJobs.length > 0}
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead class="bg-gray-50 border-b border-gray-200">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Job Title
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Applications
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								New (7d)
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Pending
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Status
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-200">
						{#each topJobs as job}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4">
									<a href="/dashboard/jobs/{job.id}/" class="text-sm font-medium text-blue-600 hover:text-blue-700">
										{job.title}
									</a>
								</td>
								<td class="px-6 py-4 text-sm text-gray-600">
									<div class="flex items-center gap-2">
										<FileText class="w-4 h-4 text-gray-400" />
										{job.applications}
									</div>
								</td>
								<td class="px-6 py-4 text-sm">
									{#if job.newApplications > 0}
										<span class="inline-flex items-center gap-1 text-green-600 font-medium">
											<TrendingUp class="w-4 h-4" />
											{job.newApplications}
										</span>
									{:else}
										<span class="text-gray-400">-</span>
									{/if}
								</td>
								<td class="px-6 py-4 text-sm">
									{#if job.pendingReview > 0}
										<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-orange-100 text-orange-800 font-medium">
											<Clock class="w-3 h-3" />
											{job.pendingReview}
										</span>
									{:else}
										<span class="text-gray-400">-</span>
									{/if}
								</td>
								<td class="px-6 py-4 text-sm">
									<span class="px-3 py-1 rounded-full text-xs font-medium {getJobStatusColor(job.status)}">
										{job.status}
									</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{:else}
			<div class="p-12 text-center">
				<Briefcase class="w-12 h-12 text-gray-400 mx-auto mb-3" />
				<p class="text-gray-600 mb-4">No jobs posted yet</p>
				<a
					href="/dashboard/jobs/new/"
					class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
				>
					<Plus class="w-4 h-4" />
					Post Your First Job
				</a>
			</div>
		{/if}
	</div>
</div>

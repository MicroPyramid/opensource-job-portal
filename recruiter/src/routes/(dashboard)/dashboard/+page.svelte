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
	import { Button, Card, Badge } from '$lib/components/ui';
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

	function getJobStatusVariant(status: string): 'success' | 'warning' | 'error' | 'neutral' {
		const variants: Record<string, 'success' | 'warning' | 'error' | 'neutral'> = {
			Live: 'success',
			Draft: 'neutral',
			Disabled: 'error',
			Expired: 'warning'
		};
		return variants[status] || 'neutral';
	}
</script>

<svelte:head>
	<title>Dashboard - PeelJobs Recruiter</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl md:text-3xl font-bold text-black">Dashboard</h1>
			<p class="text-muted mt-1">Welcome back! Here's what's happening today.</p>
		</div>
		<Button href="/dashboard/jobs/new/">
			<Plus class="w-4 h-4" />
			Post New Job
		</Button>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
		{#each stats as stat}
			<Card padding="md">
				<div class="flex items-start justify-between">
					<div class="flex-1">
						<p class="text-sm font-medium text-muted">{stat.label}</p>
						<p class="text-3xl font-bold text-black mt-2">{stat.value}</p>
						<div class="flex items-center gap-1 mt-2">
							{#if stat.change}
								{#if stat.change.startsWith('+')}
									<TrendingUp class="w-4 h-4 text-success" />
									<span class="text-xs font-medium text-success">{stat.change}</span>
								{:else if stat.change.startsWith('-')}
									<TrendingDown class="w-4 h-4 text-error" />
									<span class="text-xs font-medium text-error">{stat.change}</span>
								{:else}
									<span class="text-xs font-medium text-muted">{stat.change}</span>
								{/if}
							{:else}
								<p class="text-xs {stat.trendPositive ? 'text-success' : 'text-warning'} font-medium">
									{stat.trend}
								</p>
							{/if}
						</div>
					</div>
					<div class="w-12 h-12 rounded-lg {stat.trendPositive ? 'bg-primary/10' : 'bg-warning-light'} flex items-center justify-center">
						<stat.icon class="w-6 h-6 {stat.trendPositive ? 'text-primary' : 'text-warning'}" />
					</div>
				</div>
			</Card>
		{/each}
	</div>

	<!-- Hiring Pipeline Overview -->
	{#if data.pipeline}
		<Card padding="md">
			<h2 class="text-lg font-semibold text-black mb-4">Hiring Pipeline</h2>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
				<div class="text-center p-4 rounded-lg bg-primary/5">
					<div class="text-3xl font-bold text-primary">{data.pipeline.pending}</div>
					<div class="text-sm text-muted mt-1">Pending Review</div>
				</div>
				<div class="text-center p-4 rounded-lg bg-purple-50">
					<div class="text-3xl font-bold text-purple-600">{data.pipeline.shortlisted}</div>
					<div class="text-sm text-muted mt-1">Shortlisted</div>
				</div>
				<div class="text-center p-4 rounded-lg bg-success-light">
					<div class="text-3xl font-bold text-success">{data.pipeline.hired}</div>
					<div class="text-sm text-muted mt-1">Hired</div>
				</div>
				<div class="text-center p-4 rounded-lg bg-surface">
					<div class="text-3xl font-bold text-muted">{data.pipeline.rejected}</div>
					<div class="text-sm text-muted mt-1">Rejected</div>
				</div>
			</div>
		</Card>
	{/if}

	<!-- Recent Jobs -->
	<Card padding="none">
		<div class="p-6 border-b border-border">
			<div class="flex items-center justify-between">
				<h2 class="text-lg font-semibold text-black">Recent Jobs</h2>
				<a href="/dashboard/jobs/" class="text-sm text-primary hover:text-primary-hover font-medium transition-colors">
					View all jobs
				</a>
			</div>
		</div>
		{#if topJobs.length > 0}
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead class="bg-surface border-b border-border">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
								Job Title
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
								Applications
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
								New (7d)
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
								Pending
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
								Status
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-border">
						{#each topJobs as job}
							<tr class="hover:bg-surface transition-colors">
								<td class="px-6 py-4">
									<a href="/dashboard/jobs/{job.id}/" class="text-sm font-medium text-primary hover:text-primary-hover transition-colors">
										{job.title}
									</a>
								</td>
								<td class="px-6 py-4 text-sm text-muted">
									<div class="flex items-center gap-2">
										<FileText class="w-4 h-4" />
										{job.applications}
									</div>
								</td>
								<td class="px-6 py-4 text-sm">
									{#if job.newApplications > 0}
										<span class="inline-flex items-center gap-1 text-success font-medium">
											<TrendingUp class="w-4 h-4" />
											{job.newApplications}
										</span>
									{:else}
										<span class="text-muted">-</span>
									{/if}
								</td>
								<td class="px-6 py-4 text-sm">
									{#if job.pendingReview > 0}
										<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-warning-light text-warning font-medium">
											<Clock class="w-3 h-3" />
											{job.pendingReview}
										</span>
									{:else}
										<span class="text-muted">-</span>
									{/if}
								</td>
								<td class="px-6 py-4 text-sm">
									<Badge variant={getJobStatusVariant(job.status)}>
										{job.status}
									</Badge>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{:else}
			<div class="p-12 text-center">
				<Briefcase class="w-12 h-12 text-muted mx-auto mb-3" />
				<p class="text-muted mb-4">No jobs posted yet</p>
				<Button href="/dashboard/jobs/new/">
					<Plus class="w-4 h-4" />
					Post Your First Job
				</Button>
			</div>
		{/if}
	</Card>
</div>

<script lang="ts">
	import { goto } from '$app/navigation';
	import {
		TrendingUp,
		TrendingDown,
		Users,
		Briefcase,
		Clock,
		Target,
		Download,
		CheckCircle,
		UserCheck,
		XCircle
	} from '@lucide/svelte';
	import type { PageData } from './$types';

	export let data: PageData;

	const { analytics, period } = data;

	const periodOptions = [
		{ value: '7d', label: 'Last 7 days' },
		{ value: '30d', label: 'Last 30 days' },
		{ value: '90d', label: 'Last 90 days' }
	];

	function changePeriod(newPeriod: string) {
		goto(`/dashboard/analytics/?period=${newPeriod}`);
	}

	// Build overview metrics from real data
	$: overviewMetrics = [
		{
			label: 'Total Applications',
			value: analytics.overview.total_applications.toLocaleString(),
			change: analytics.overview.trend,
			isPositive: analytics.overview.trend.startsWith('+'),
			icon: Users
		},
		{
			label: 'Active Jobs',
			value: analytics.overview.total_jobs.toString(),
			change: `${analytics.overview.avg_per_day} apps/day`,
			isPositive: true,
			icon: Briefcase
		},
		{
			label: 'Hired',
			value: analytics.pipeline.hired.toString(),
			change: `${analytics.pipeline.conversion_rate}% conversion`,
			isPositive: true,
			icon: CheckCircle
		},
		{
			label: 'Pending Review',
			value: analytics.pipeline.pending.toString(),
			change: 'Need attention',
			isPositive: false,
			icon: Clock
		}
	];

	// Pipeline metrics with percentages
	$: pipelineMetrics = [
		{
			stage: 'New Applications',
			count: analytics.overview.total_applications,
			percentage: 100
		},
		{
			stage: 'Shortlisted',
			count: analytics.pipeline.shortlisted,
			percentage: Math.round((analytics.pipeline.shortlisted / analytics.overview.total_applications) * 100)
		},
		{
			stage: 'Hired',
			count: analytics.pipeline.hired,
			percentage: Math.round((analytics.pipeline.hired / analytics.overview.total_applications) * 100)
		},
		{
			stage: 'Rejected',
			count: analytics.pipeline.rejected,
			percentage: Math.round((analytics.pipeline.rejected / analytics.overview.total_applications) * 100)
		}
	];

	// Sort peak days
	const dayOrder = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
	$: peakDaysArray = dayOrder.map(day => ({
		day: day.charAt(0).toUpperCase() + day.slice(1),
		count: analytics.peak_days[day] || 0
	}));
</script>

<svelte:head>
	<title>Analytics - PeelJobs Recruiter</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl md:text-3xl font-bold text-black">Application Analytics</h1>
			<p class="text-muted mt-1">Track your hiring performance and insights</p>
		</div>
		<div class="flex items-center gap-3">
			<select
				value={period}
				onchange={(e) => changePeriod(e.currentTarget.value)}
				class="px-4 py-2 border border-border rounded-lg bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary"
			>
				{#each periodOptions as option}
					<option value={option.value}>{option.label}</option>
				{/each}
			</select>
			<button
				class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-border rounded-lg text-sm font-medium text-muted hover:bg-surface transition-colors"
			>
				<Download class="w-4 h-4" />
				Export Report
			</button>
		</div>
	</div>

	<!-- Overview Metrics -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
		{#each overviewMetrics as metric}
			<div class="bg-white rounded-lg border border-border p-6">
				<div class="flex items-start justify-between">
					<div class="flex-1">
						<p class="text-sm font-medium text-muted">{metric.label}</p>
						<p class="text-3xl font-bold text-black mt-2">{metric.value}</p>
						<div class="flex items-center gap-1 mt-2">
							{#if metric.isPositive && metric.change.includes('%')}
								<TrendingUp class="w-4 h-4 text-success" />
								<span class="text-sm font-medium text-success">{metric.change}</span>
							{:else if !metric.isPositive && metric.change.includes('%')}
								<TrendingDown class="w-4 h-4 text-error" />
								<span class="text-sm font-medium text-error">{metric.change}</span>
							{:else}
								<span class="text-sm text-muted">{metric.change}</span>
							{/if}
						</div>
					</div>
					<div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
						<metric.icon class="w-6 h-6 text-primary" />
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Job Performance -->
	<div class="bg-white rounded-lg border border-border">
		<div class="p-6 border-b border-border">
			<h2 class="text-lg font-semibold text-black">Job Performance</h2>
		</div>
		{#if analytics.job_performance.length > 0}
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
								Pending
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
								Shortlisted
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
								Hired
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
								Conversion
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
								Avg/Day
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-border">
						{#each analytics.job_performance as job}
							<tr class="hover:bg-surface">
								<td class="px-6 py-4">
									<a href="/dashboard/jobs/{job.job_id}/" class="text-sm font-medium text-primary hover:text-primary">
										{job.job_title}
									</a>
								</td>
								<td class="px-6 py-4 text-sm text-black font-medium">
									{job.total_applications}
								</td>
								<td class="px-6 py-4 text-sm text-muted">
									{job.pending}
								</td>
								<td class="px-6 py-4 text-sm text-muted">
									{job.shortlisted}
								</td>
								<td class="px-6 py-4 text-sm text-success font-medium">
									{job.hired}
								</td>
								<td class="px-6 py-4 text-sm">
									<div class="flex items-center gap-2">
										<Target class="w-4 h-4 text-success" />
										{job.conversion_rate}%
									</div>
								</td>
								<td class="px-6 py-4 text-sm text-muted">
									{job.avg_applications_per_day}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{:else}
			<div class="p-12 text-center">
				<Briefcase class="w-12 h-12 text-muted mx-auto mb-3" />
				<p class="text-muted">No active jobs in this period</p>
			</div>
		{/if}
	</div>

	<!-- Pipeline & Peak Days Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Application Pipeline -->
		<div class="bg-white rounded-lg border border-border">
			<div class="p-6 border-b border-border">
				<h2 class="text-lg font-semibold text-black">Application Pipeline</h2>
			</div>
			<div class="p-6">
				<div class="space-y-4">
					{#each pipelineMetrics as stage}
						<div>
							<div class="flex items-center justify-between mb-2">
								<span class="text-sm font-medium text-black">{stage.stage}</span>
								<span class="text-sm text-muted">{stage.count}</span>
							</div>
							<div class="w-full bg-surface rounded-full h-2">
								<div
									class="bg-primary h-2 rounded-full transition-all"
									style="width: {stage.percentage}%"
								></div>
							</div>
							<div class="text-xs text-muted mt-1">{stage.percentage}% of total</div>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Peak Days -->
		<div class="bg-white rounded-lg border border-border">
			<div class="p-6 border-b border-border">
				<h2 class="text-lg font-semibold text-black">Applications by Day of Week</h2>
			</div>
			<div class="p-6">
				<div class="space-y-4">
					{#each peakDaysArray as day}
						{@const maxCount = Math.max(...peakDaysArray.map(d => d.count))}
						{@const percentage = maxCount > 0 ? (day.count / maxCount) * 100 : 0}
						<div>
							<div class="flex items-center justify-between mb-2">
								<span class="text-sm font-medium text-black">{day.day}</span>
								<span class="text-sm text-muted">{day.count}</span>
							</div>
							<div class="w-full bg-surface rounded-full h-2">
								<div
									class="bg-success h-2 rounded-full transition-all"
									style="width: {percentage}%"
								></div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>

	<!-- Key Insights -->
	<div class="bg-white rounded-lg border border-border">
		<div class="p-6 border-b border-border">
			<h2 class="text-lg font-semibold text-black">Key Insights</h2>
		</div>
		<div class="p-6">
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				{#if analytics.pipeline.pending > 0}
					<div class="flex gap-4">
						<div class="w-12 h-12 rounded-lg bg-warning-light flex items-center justify-center flex-shrink-0">
							<Clock class="w-6 h-6 text-warning" />
						</div>
						<div>
							<h3 class="font-semibold text-black mb-1">Action Required</h3>
							<p class="text-sm text-muted">
								{analytics.pipeline.pending} applications are pending review.
							</p>
						</div>
					</div>
				{/if}

				{#if analytics.pipeline.conversion_rate > 3}
					<div class="flex gap-4">
						<div class="w-12 h-12 rounded-lg bg-success-light flex items-center justify-center flex-shrink-0">
							<Target class="w-6 h-6 text-success" />
						</div>
						<div>
							<h3 class="font-semibold text-black mb-1">Strong Conversion Rate</h3>
							<p class="text-sm text-muted">
								{analytics.pipeline.conversion_rate}% conversion rate from applications to hires.
							</p>
						</div>
					</div>
				{/if}

				{#if analytics.overview.avg_per_day > 0}
					<div class="flex gap-4">
						<div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
							<TrendingUp class="w-6 h-6 text-primary" />
						</div>
						<div>
							<h3 class="font-semibold text-black mb-1">Application Velocity</h3>
							<p class="text-sm text-muted">
								Receiving an average of {analytics.overview.avg_per_day} applications per day.
							</p>
						</div>
					</div>
				{/if}

				{#if analytics.pipeline.shortlisted > 0}
					<div class="flex gap-4">
						<div class="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
							<UserCheck class="w-6 h-6 text-purple-600" />
						</div>
						<div>
							<h3 class="font-semibold text-black mb-1">Active Pipeline</h3>
							<p class="text-sm text-muted">
								{analytics.pipeline.shortlisted} qualified candidates in your pipeline.
							</p>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>

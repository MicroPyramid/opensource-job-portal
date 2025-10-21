<script lang="ts">
	import {
		TrendingUp,
		TrendingDown,
		Eye,
		Users,
		Briefcase,
		Clock,
		Target,
		Download,
		Calendar
	} from '@lucide/svelte';

	let selectedPeriod = $state('30d');

	const periodOptions = [
		{ value: '7d', label: 'Last 7 days' },
		{ value: '30d', label: 'Last 30 days' },
		{ value: '90d', label: 'Last 90 days' },
		{ value: 'custom', label: 'Custom range' }
	];

	// Mock data
	const overviewMetrics = [
		{
			label: 'Total Job Views',
			value: '15,234',
			change: '+12.5%',
			isPositive: true,
			icon: Eye
		},
		{
			label: 'Total Applications',
			value: '1,248',
			change: '+8.3%',
			isPositive: true,
			icon: Users
		},
		{
			label: 'Active Jobs',
			value: '12',
			change: '+2',
			isPositive: true,
			icon: Briefcase
		},
		{
			label: 'Avg. Time to Fill',
			value: '18 days',
			change: '-3 days',
			isPositive: true,
			icon: Clock
		}
	];

	const jobPerformance = [
		{
			title: 'Senior Frontend Developer',
			views: 1240,
			applications: 45,
			conversion: 3.6,
			status: 'Active',
			daysActive: 15
		},
		{
			title: 'Product Manager',
			views: 980,
			applications: 38,
			conversion: 3.9,
			status: 'Active',
			daysActive: 12
		},
		{
			title: 'UI/UX Designer',
			views: 756,
			applications: 28,
			conversion: 3.7,
			status: 'Active',
			daysActive: 10
		},
		{
			title: 'Backend Developer',
			views: 645,
			applications: 22,
			conversion: 3.4,
			status: 'Active',
			daysActive: 8
		},
		{
			title: 'DevOps Engineer',
			views: 523,
			applications: 19,
			conversion: 3.6,
			status: 'Active',
			daysActive: 5
		}
	];

	const pipelineMetrics = [
		{ stage: 'New Applications', count: 248, percentage: 100 },
		{ stage: 'In Review', count: 186, percentage: 75 },
		{ stage: 'Shortlisted', count: 92, percentage: 37 },
		{ stage: 'Interviewed', count: 45, percentage: 18 },
		{ stage: 'Hired', count: 12, percentage: 5 }
	];

	const topSources = [
		{ source: 'Direct Application', count: 512, percentage: 41 },
		{ source: 'LinkedIn', count: 384, count: 31 },
		{ source: 'Indeed', count: 192, percentage: 15 },
		{ source: 'Referral', count: 96, percentage: 8 },
		{ source: 'Other', count: 64, percentage: 5 }
	];

	const locationInsights = [
		{ location: 'San Francisco, CA', applicants: 245 },
		{ location: 'New York, NY', applicants: 198 },
		{ location: 'Austin, TX', applicants: 156 },
		{ location: 'Seattle, WA', applicants: 134 },
		{ location: 'Remote', applicants: 289 }
	];
</script>

<svelte:head>
	<title>Analytics - PeelJobs Recruiter</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Analytics</h1>
			<p class="text-gray-600 mt-1">Track your hiring performance and insights</p>
		</div>
		<div class="flex items-center gap-3">
			<select
				bind:value={selectedPeriod}
				class="px-4 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
			>
				{#each periodOptions as option}
					<option value={option.value}>{option.label}</option>
				{/each}
			</select>
			<button
				class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
			>
				<Download class="w-4 h-4" />
				Export Report
			</button>
		</div>
	</div>

	<!-- Overview Metrics -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
		{#each overviewMetrics as metric}
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<div class="flex items-start justify-between">
					<div class="flex-1">
						<p class="text-sm font-medium text-gray-600">{metric.label}</p>
						<p class="text-3xl font-bold text-gray-900 mt-2">{metric.value}</p>
						<div class="flex items-center gap-1 mt-2">
							{#if metric.isPositive}
								<TrendingUp class="w-4 h-4 text-green-600" />
								<span class="text-sm font-medium text-green-600">{metric.change}</span>
							{:else}
								<TrendingDown class="w-4 h-4 text-red-600" />
								<span class="text-sm font-medium text-red-600">{metric.change}</span>
							{/if}
							<span class="text-sm text-gray-600">vs last period</span>
						</div>
					</div>
					<div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
						<metric.icon class="w-6 h-6 text-blue-600" />
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Job Performance -->
	<div class="bg-white rounded-lg border border-gray-200">
		<div class="p-6 border-b border-gray-200">
			<h2 class="text-lg font-semibold text-gray-900">Job Performance</h2>
		</div>
		<div class="overflow-x-auto">
			<table class="w-full">
				<thead class="bg-gray-50 border-b border-gray-200">
					<tr>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Job Title
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Views
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Applications
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Conversion Rate
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Days Active
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Status
						</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-200">
					{#each jobPerformance as job}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4 text-sm font-medium text-gray-900">{job.title}</td>
							<td class="px-6 py-4 text-sm text-gray-600">
								<div class="flex items-center gap-2">
									<Eye class="w-4 h-4 text-gray-400" />
									{job.views.toLocaleString()}
								</div>
							</td>
							<td class="px-6 py-4 text-sm text-gray-600">
								<div class="flex items-center gap-2">
									<Users class="w-4 h-4 text-gray-400" />
									{job.applications}
								</div>
							</td>
							<td class="px-6 py-4 text-sm text-gray-600">
								<div class="flex items-center gap-2">
									<Target class="w-4 h-4 text-green-600" />
									{job.conversion}%
								</div>
							</td>
							<td class="px-6 py-4 text-sm text-gray-600">
								<div class="flex items-center gap-2">
									<Calendar class="w-4 h-4 text-gray-400" />
									{job.daysActive} days
								</div>
							</td>
							<td class="px-6 py-4">
								<span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
									{job.status}
								</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>

	<!-- Pipeline & Sources Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Application Pipeline -->
		<div class="bg-white rounded-lg border border-gray-200">
			<div class="p-6 border-b border-gray-200">
				<h2 class="text-lg font-semibold text-gray-900">Application Pipeline</h2>
			</div>
			<div class="p-6">
				<div class="space-y-4">
					{#each pipelineMetrics as stage}
						<div>
							<div class="flex items-center justify-between mb-2">
								<span class="text-sm font-medium text-gray-900">{stage.stage}</span>
								<span class="text-sm text-gray-600">{stage.count}</span>
							</div>
							<div class="w-full bg-gray-200 rounded-full h-2">
								<div
									class="bg-blue-600 h-2 rounded-full transition-all"
									style="width: {stage.percentage}%"
								></div>
							</div>
							<div class="text-xs text-gray-500 mt-1">{stage.percentage}% conversion</div>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Top Sources -->
		<div class="bg-white rounded-lg border border-gray-200">
			<div class="p-6 border-b border-gray-200">
				<h2 class="text-lg font-semibold text-gray-900">Application Sources</h2>
			</div>
			<div class="p-6">
				<div class="space-y-4">
					{#each topSources as source}
						<div>
							<div class="flex items-center justify-between mb-2">
								<span class="text-sm font-medium text-gray-900">{source.source}</span>
								<span class="text-sm text-gray-600">{source.count}</span>
							</div>
							<div class="w-full bg-gray-200 rounded-full h-2">
								<div
									class="bg-green-600 h-2 rounded-full transition-all"
									style="width: {source.percentage}%"
								></div>
							</div>
							<div class="text-xs text-gray-500 mt-1">{source.percentage}%</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>

	<!-- Location Insights -->
	<div class="bg-white rounded-lg border border-gray-200">
		<div class="p-6 border-b border-gray-200">
			<h2 class="text-lg font-semibold text-gray-900">Top Applicant Locations</h2>
		</div>
		<div class="p-6">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
				{#each locationInsights as location}
					<div class="text-center">
						<div
							class="w-20 h-20 mx-auto rounded-full bg-blue-100 flex items-center justify-center mb-3"
						>
							<span class="text-2xl font-bold text-blue-600">{location.applicants}</span>
						</div>
						<p class="text-sm font-medium text-gray-900">{location.location}</p>
						<p class="text-xs text-gray-600 mt-1">applicants</p>
					</div>
				{/each}
			</div>
		</div>
	</div>

	<!-- Key Insights -->
	<div class="bg-white rounded-lg border border-gray-200">
		<div class="p-6 border-b border-gray-200">
			<h2 class="text-lg font-semibold text-gray-900">Key Insights</h2>
		</div>
		<div class="p-6">
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div class="flex gap-4">
					<div class="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
						<TrendingUp class="w-6 h-6 text-green-600" />
					</div>
					<div>
						<h3 class="font-semibold text-gray-900 mb-1">Strong Application Rate</h3>
						<p class="text-sm text-gray-600">
							Your jobs are receiving 23% more applications than the industry average.
						</p>
					</div>
				</div>

				<div class="flex gap-4">
					<div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
						<Target class="w-6 h-6 text-blue-600" />
					</div>
					<div>
						<h3 class="font-semibold text-gray-900 mb-1">High Conversion Rate</h3>
						<p class="text-sm text-gray-600">
							3.7% average conversion rate from views to applications is above average.
						</p>
					</div>
				</div>

				<div class="flex gap-4">
					<div class="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
						<Users class="w-6 h-6 text-purple-600" />
					</div>
					<div>
						<h3 class="font-semibold text-gray-900 mb-1">Remote Popularity</h3>
						<p class="text-sm text-gray-600">
							Remote positions receive 45% more applications than on-site roles.
						</p>
					</div>
				</div>

				<div class="flex gap-4">
					<div class="w-12 h-12 rounded-lg bg-orange-100 flex items-center justify-center flex-shrink-0">
						<Clock class="w-6 h-6 text-orange-600" />
					</div>
					<div>
						<h3 class="font-semibold text-gray-900 mb-1">Quick Response Needed</h3>
						<p class="text-sm text-gray-600">
							18 applications are pending review for more than 48 hours.
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

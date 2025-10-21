<script lang="ts">
	import {
		Briefcase,
		Users,
		Clock,
		AlertCircle,
		TrendingUp,
		Eye,
		FileText,
		Plus,
		UserCheck,
		Calendar
	} from '@lucide/svelte';

	// Mock data - will be replaced with API calls
	const stats = [
		{
			label: 'Active Jobs',
			value: '12',
			icon: Briefcase,
			trend: '+2 this month',
			trendPositive: true
		},
		{
			label: 'Total Applicants',
			value: '248',
			icon: Users,
			trend: '+34 this week',
			trendPositive: true
		},
		{
			label: 'Pending Reviews',
			value: '18',
			icon: Clock,
			trend: '6 urgent',
			trendPositive: false
		},
		{
			label: 'Expiring Soon',
			value: '3',
			icon: AlertCircle,
			trend: 'Next 7 days',
			trendPositive: false
		}
	];

	const recentApplicants = [
		{
			id: 1,
			name: 'John Smith',
			jobTitle: 'Senior Frontend Developer',
			appliedDate: '2 hours ago',
			status: 'New'
		},
		{
			id: 2,
			name: 'Sarah Johnson',
			jobTitle: 'Product Manager',
			appliedDate: '4 hours ago',
			status: 'New'
		},
		{
			id: 3,
			name: 'Michael Chen',
			jobTitle: 'UI/UX Designer',
			appliedDate: '1 day ago',
			status: 'In Review'
		},
		{
			id: 4,
			name: 'Emma Davis',
			jobTitle: 'Backend Developer',
			appliedDate: '1 day ago',
			status: 'Shortlisted'
		},
		{
			id: 5,
			name: 'James Wilson',
			jobTitle: 'Senior Frontend Developer',
			appliedDate: '2 days ago',
			status: 'In Review'
		}
	];

	const topJobs = [
		{ title: 'Senior Frontend Developer', views: 1240, applications: 45, conversion: '3.6%' },
		{ title: 'Product Manager', views: 980, applications: 38, conversion: '3.9%' },
		{ title: 'UI/UX Designer', views: 756, applications: 28, conversion: '3.7%' },
		{ title: 'Backend Developer', views: 645, applications: 22, conversion: '3.4%' }
	];

	const recentActivity = [
		{ action: 'Sarah reviewed John Smith for Senior Frontend Developer', time: '10 min ago' },
		{ action: 'New application received for Product Manager', time: '25 min ago' },
		{ action: 'Interview scheduled with Emma Davis', time: '1 hour ago' },
		{ action: 'Job posted: DevOps Engineer', time: '2 hours ago' },
		{ action: 'Michael Chen moved to Shortlisted', time: '3 hours ago' }
	];

	function getStatusColor(status: string): string {
		const colors: Record<string, string> = {
			New: 'bg-blue-100 text-blue-800',
			'In Review': 'bg-yellow-100 text-yellow-800',
			Shortlisted: 'bg-green-100 text-green-800',
			Interviewed: 'bg-purple-100 text-purple-800',
			Rejected: 'bg-red-100 text-red-800'
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
		<div class="flex gap-3">
			<a
				href="/dashboard/applicants/"
				class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
			>
				<UserCheck class="w-4 h-4" />
				Review Applicants
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

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
		{#each stats as stat}
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<div class="flex items-start justify-between">
					<div class="flex-1">
						<p class="text-sm font-medium text-gray-600">{stat.label}</p>
						<p class="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
						<p
							class="text-xs mt-2 {stat.trendPositive
								? 'text-green-600'
								: 'text-orange-600'} font-medium"
						>
							{stat.trend}
						</p>
					</div>
					<div
						class="w-12 h-12 rounded-lg {stat.trendPositive
							? 'bg-blue-100'
							: 'bg-orange-100'} flex items-center justify-center"
					>
						<stat.icon class="w-6 h-6 {stat.trendPositive ? 'text-blue-600' : 'text-orange-600'}" />
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Main Content Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Recent Applicants -->
		<div class="lg:col-span-2 bg-white rounded-lg border border-gray-200">
			<div class="p-6 border-b border-gray-200">
				<div class="flex items-center justify-between">
					<h2 class="text-lg font-semibold text-gray-900">Recent Applicants</h2>
					<a href="/dashboard/applicants/" class="text-sm text-blue-600 hover:text-blue-700 font-medium">
						View all
					</a>
				</div>
			</div>
			<div class="divide-y divide-gray-200">
				{#each recentApplicants as applicant}
					<a
						href="/dashboard/applicants/{applicant.id}/"
						class="block p-6 hover:bg-gray-50 transition-colors"
					>
						<div class="flex items-start justify-between gap-4">
							<div class="flex items-start gap-4 flex-1 min-w-0">
								<div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
									<Users class="w-5 h-5 text-gray-600" />
								</div>
								<div class="flex-1 min-w-0">
									<p class="font-medium text-gray-900 truncate">{applicant.name}</p>
									<p class="text-sm text-gray-600 truncate">{applicant.jobTitle}</p>
									<p class="text-xs text-gray-500 mt-1">{applicant.appliedDate}</p>
								</div>
							</div>
							<span
								class="px-3 py-1 rounded-full text-xs font-medium flex-shrink-0 {getStatusColor(
									applicant.status
								)}"
							>
								{applicant.status}
							</span>
						</div>
					</a>
				{/each}
			</div>
		</div>

		<!-- Activity Feed -->
		<div class="bg-white rounded-lg border border-gray-200">
			<div class="p-6 border-b border-gray-200">
				<h2 class="text-lg font-semibold text-gray-900">Recent Activity</h2>
			</div>
			<div class="p-6">
				<div class="space-y-4">
					{#each recentActivity as activity}
						<div class="flex gap-3">
							<div class="w-2 h-2 rounded-full bg-blue-600 mt-2 flex-shrink-0"></div>
							<div class="flex-1 min-w-0">
								<p class="text-sm text-gray-900">{activity.action}</p>
								<p class="text-xs text-gray-500 mt-1">{activity.time}</p>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>

	<!-- Job Performance -->
	<div class="bg-white rounded-lg border border-gray-200">
		<div class="p-6 border-b border-gray-200">
			<div class="flex items-center justify-between">
				<h2 class="text-lg font-semibold text-gray-900">Top Performing Jobs</h2>
				<a href="/dashboard/analytics/jobs/" class="text-sm text-blue-600 hover:text-blue-700 font-medium">
					View analytics
				</a>
			</div>
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
							Conversion
						</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-200">
					{#each topJobs as job}
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
									<FileText class="w-4 h-4 text-gray-400" />
									{job.applications}
								</div>
							</td>
							<td class="px-6 py-4 text-sm text-gray-600">
								<div class="flex items-center gap-2">
									<TrendingUp class="w-4 h-4 text-green-600" />
									{job.conversion}
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>

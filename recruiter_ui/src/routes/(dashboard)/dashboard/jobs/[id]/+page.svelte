<script lang="ts">
	import {
		ArrowLeft,
		Briefcase,
		MapPin,
		Calendar,
		DollarSign,
		Users,
		Eye,
		Clock,
		Building,
		Globe,
		Mail,
		Edit,
		Share2,
		ExternalLink,
		TrendingUp,
		Target
	} from '@lucide/svelte';

	let { data } = $props();

	function formatDate(dateString?: string): string {
		if (!dateString) return 'N/A';
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function formatSalary(min: number, max: number, type: string): string {
		if (!min && !max) return 'Not disclosed';
		const minStr = min ? `₹${(min / 100000).toFixed(1)}L` : '';
		const maxStr = max ? `₹${(max / 100000).toFixed(1)}L` : '';
		const range = minStr && maxStr ? `${minStr} - ${maxStr}` : minStr || maxStr;
		return `${range} per ${type === 'Month' ? 'month' : 'year'}`;
	}

	function getStatusBadgeClass(status: string): string {
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
</script>

<svelte:head>
	<title>{data.job.title} - Job Details - PeelJobs</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex items-center gap-4">
		<a
			href="/dashboard/jobs/"
			class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
			title="Back to Jobs"
		>
			<ArrowLeft class="w-5 h-5" />
		</a>
		<div class="flex-1">
			<div class="flex items-center gap-3 mb-2">
				<h1 class="text-2xl md:text-3xl font-bold text-gray-900">{data.job.title}</h1>
				<span class="px-3 py-1 text-sm font-medium rounded {getStatusBadgeClass(data.job.status)}">
					{data.job.status}
				</span>
			</div>
			<p class="text-gray-600">{data.job.company_name || 'Your Company'}</p>
		</div>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
					<Users class="w-5 h-5 text-blue-600" />
				</div>
				<div>
					<div class="text-2xl font-bold text-gray-900">{data.totalApplicants}</div>
					<div class="text-sm text-gray-600">Total Applicants</div>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
					<Clock class="w-5 h-5 text-yellow-600" />
				</div>
				<div>
					<div class="text-2xl font-bold text-gray-900">{data.applicantsStats.pending}</div>
					<div class="text-sm text-gray-600">Pending</div>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
					<Users class="w-5 h-5 text-blue-600" />
				</div>
				<div>
					<div class="text-2xl font-bold text-gray-900">{data.applicantsStats.shortlisted}</div>
					<div class="text-sm text-gray-600">Shortlisted</div>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg border border-gray-200 p-4">
			<div class="flex items-center gap-3">
				<div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
					<Users class="w-5 h-5 text-green-600" />
				</div>
				<div>
					<div class="text-2xl font-bold text-gray-900">{data.applicantsStats.selected}</div>
					<div class="text-sm text-gray-600">Hired</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Analytics Section (30-day period) -->
	{#if data.analytics}
		<div class="bg-white rounded-lg border border-gray-200 p-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Application Analytics (Last 30 Days)</h2>
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<div class="text-center">
					<div class="text-2xl font-bold text-blue-600">{data.analytics.metrics.total_applications}</div>
					<div class="text-sm text-gray-600 mt-1">Total Applications</div>
				</div>
				<div class="text-center">
					<div class="text-2xl font-bold text-purple-600">{data.analytics.pipeline.pending}</div>
					<div class="text-sm text-gray-600 mt-1">Pending Review</div>
				</div>
				<div class="text-center">
					<div class="text-2xl font-bold text-green-600">{data.analytics.pipeline.hired}</div>
					<div class="text-sm text-gray-600 mt-1">Hired</div>
				</div>
				<div class="text-center">
					<div class="flex items-center justify-center gap-1">
						<Target class="w-5 h-5 text-green-600" />
						<div class="text-2xl font-bold text-green-600">{data.analytics.pipeline.conversion_rate}%</div>
					</div>
					<div class="text-sm text-gray-600 mt-1">Conversion Rate</div>
				</div>
			</div>

			{#if data.analytics.metrics.avg_per_day > 0}
				<div class="mt-4 pt-4 border-t border-gray-200">
					<div class="flex items-center justify-center gap-2 text-sm text-gray-600">
						<TrendingUp class="w-4 h-4 text-blue-600" />
						<span>Average <span class="font-semibold text-gray-900">{data.analytics.metrics.avg_per_day}</span> applications per day</span>
					</div>
				</div>
			{/if}
		</div>
	{/if}

	<!-- Action Buttons -->
	<div class="flex flex-wrap gap-3">
		<a
			href="/dashboard/jobs/{data.job.id}/applicants/"
			class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
		>
			<Users class="w-4 h-4" />
			View Applicants
		</a>

		{#if data.job.status === 'Draft'}
			<a
				href="/dashboard/jobs/{data.job.id}/edit/"
				class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
			>
				<Edit class="w-4 h-4" />
				Edit Job
			</a>
		{/if}

		<button
			class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
		>
			<Share2 class="w-4 h-4" />
			Share Job
		</button>

		<a
			href="/jobs/{data.job.id}/"
			target="_blank"
			class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
		>
			<ExternalLink class="w-4 h-4" />
			View Public Page
		</a>
	</div>

	<!-- Job Details -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Main Content -->
		<div class="lg:col-span-2 space-y-6">
			<!-- Job Information -->
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Job Information</h2>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<div class="text-sm font-medium text-gray-500 mb-1">Job Type</div>
						<div class="text-gray-900 capitalize">{data.job.job_type.replace('-', ' ')}</div>
					</div>

					<div>
						<div class="text-sm font-medium text-gray-500 mb-1">Work Mode</div>
						<div class="text-gray-900 capitalize">{data.job.work_mode.replace('-', ' ')}</div>
					</div>

					<div>
						<div class="text-sm font-medium text-gray-500 mb-1">Experience</div>
						<div class="text-gray-900">
							{#if data.job.fresher}
								Fresher
							{:else}
								{data.job.min_year}-{data.job.max_year} years
							{/if}
						</div>
					</div>

					<div>
						<div class="text-sm font-medium text-gray-500 mb-1">Vacancies</div>
						<div class="text-gray-900">{data.job.vacancies}</div>
					</div>

					<div>
						<div class="text-sm font-medium text-gray-500 mb-1">Salary</div>
						<div class="text-gray-900">
							{formatSalary(data.job.min_salary, data.job.max_salary, data.job.salary_type)}
						</div>
					</div>

					{#if data.job.seniority_level}
						<div>
							<div class="text-sm font-medium text-gray-500 mb-1">Seniority Level</div>
							<div class="text-gray-900 capitalize">{data.job.seniority_level}</div>
						</div>
					{/if}
				</div>
			</div>

			<!-- Description -->
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Job Description</h2>
				<div class="prose prose-sm max-w-none text-gray-700">
					{@html data.job.description}
				</div>
			</div>

			<!-- Skills -->
			{#if data.job.skills && data.job.skills.length > 0}
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h2 class="text-lg font-semibold text-gray-900 mb-4">Required Skills</h2>
					<div class="flex flex-wrap gap-2">
						{#each data.job.skills as skill}
							<span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
								{skill.name}
							</span>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Qualifications -->
			{#if data.job.qualifications && data.job.qualifications.length > 0}
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h2 class="text-lg font-semibold text-gray-900 mb-4">Educational Qualifications</h2>
					<div class="flex flex-wrap gap-2">
						{#each data.job.qualifications as qual}
							<span class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
								{qual.name}
							</span>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Benefits -->
			{#if data.job.benefits && data.job.benefits.length > 0}
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h2 class="text-lg font-semibold text-gray-900 mb-4">Benefits & Perks</h2>
					<ul class="space-y-2">
						{#each data.job.benefits as benefit}
							<li class="flex items-center gap-2 text-gray-700">
								<div class="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
								{benefit}
							</li>
						{/each}
					</ul>
				</div>
			{/if}
		</div>

		<!-- Sidebar -->
		<div class="space-y-6">
			<!-- Job Status -->
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<h3 class="text-sm font-semibold text-gray-900 mb-4">Job Status</h3>
				<div class="space-y-3 text-sm">
					<div class="flex items-center justify-between">
						<span class="text-gray-600">Status</span>
						<span class="px-2 py-1 text-xs font-medium rounded {getStatusBadgeClass(data.job.status)}">
							{data.job.status}
						</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-gray-600">Posted</span>
						<span class="text-gray-900">{data.job.time_ago}</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-gray-600">Expires</span>
						<span class="text-gray-900">{formatDate(data.job.last_date)}</span>
					</div>
					{#if data.job.days_until_expiry !== null}
						<div class="flex items-center justify-between">
							<span class="text-gray-600">Days Left</span>
							<span class="text-gray-900 font-medium">{data.job.days_until_expiry}</span>
						</div>
					{/if}
				</div>
			</div>

			<!-- Locations -->
			{#if data.job.locations && data.job.locations.length > 0}
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h3 class="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
						<MapPin class="w-4 h-4" />
						Job Locations
					</h3>
					<div class="space-y-2">
						{#each data.job.locations as location}
							<div class="text-sm text-gray-700">
								{location.name}, {location.state || ''}
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Industries -->
			{#if data.job.industries && data.job.industries.length > 0}
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h3 class="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
						<Building class="w-4 h-4" />
						Industries
					</h3>
					<div class="flex flex-wrap gap-2">
						{#each data.job.industries as industry}
							<span class="text-sm px-2 py-1 bg-gray-100 text-gray-700 rounded">
								{industry.name}
							</span>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Company Info -->
			{#if data.job.company_description}
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h3 class="text-sm font-semibold text-gray-900 mb-4">About Company</h3>
					<p class="text-sm text-gray-700 leading-relaxed">{data.job.company_description}</p>
				</div>
			{/if}
		</div>
	</div>
</div>

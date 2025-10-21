<script lang="ts">
	import {
		Plus,
		Search,
		Filter,
		Eye,
		Users,
		MoreVertical,
		Edit,
		Copy,
		XCircle,
		ExternalLink,
		Calendar,
		MapPin,
		Briefcase
	} from '@lucide/svelte';

	let searchQuery = $state('');
	let selectedFilter = $state('all');
	let viewMode = $state<'grid' | 'list'>('list');

	// Mock data
	const jobs = [
		{
			id: 1,
			title: 'Senior Frontend Developer',
			department: 'Engineering',
			location: 'San Francisco, CA',
			employmentType: 'Full-time',
			postedDate: '2025-10-15',
			expiryDate: '2025-11-15',
			status: 'Published',
			views: 1240,
			applicants: 45,
			isExpiringSoon: false
		},
		{
			id: 2,
			title: 'Product Manager',
			department: 'Product',
			location: 'Remote',
			employmentType: 'Full-time',
			postedDate: '2025-10-12',
			expiryDate: '2025-10-28',
			status: 'Published',
			views: 980,
			applicants: 38,
			isExpiringSoon: true
		},
		{
			id: 3,
			title: 'UI/UX Designer',
			department: 'Design',
			location: 'New York, NY',
			employmentType: 'Full-time',
			postedDate: '2025-10-10',
			expiryDate: '2025-11-10',
			status: 'Published',
			views: 756,
			applicants: 28,
			isExpiringSoon: false
		},
		{
			id: 4,
			title: 'Backend Developer',
			department: 'Engineering',
			location: 'Austin, TX',
			employmentType: 'Contract',
			postedDate: '2025-10-08',
			expiryDate: '2025-11-08',
			status: 'Published',
			views: 645,
			applicants: 22,
			isExpiringSoon: false
		},
		{
			id: 5,
			title: 'DevOps Engineer',
			department: 'Engineering',
			location: 'Remote',
			employmentType: 'Full-time',
			postedDate: '2025-10-05',
			expiryDate: '2025-10-25',
			status: 'Published',
			views: 523,
			applicants: 19,
			isExpiringSoon: true
		}
	];

	const filterOptions = [
		{ value: 'all', label: 'All Jobs' },
		{ value: 'active', label: 'Active' },
		{ value: 'draft', label: 'Drafts' },
		{ value: 'closed', label: 'Closed' },
		{ value: 'expiring', label: 'Expiring Soon' }
	];

	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function getDaysUntilExpiry(expiryDate: string): number {
		const today = new Date();
		const expiry = new Date(expiryDate);
		const diffTime = expiry.getTime() - today.getTime();
		return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
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
		<a
			href="/dashboard/jobs/new/"
			class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
		>
			<Plus class="w-4 h-4" />
			Post New Job
		</a>
	</div>

	<!-- Filters and Search -->
	<div class="bg-white rounded-lg border border-gray-200 p-4">
		<div class="flex flex-col md:flex-row gap-4">
			<!-- Search -->
			<div class="flex-1 relative">
				<Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
				<input
					type="text"
					bind:value={searchQuery}
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
						class="pl-9 pr-8 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none cursor-pointer"
					>
						{#each filterOptions as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<div class="flex border border-gray-300 rounded-lg overflow-hidden">
					<button
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
		</div>
	</div>

	<!-- Jobs List -->
	{#if viewMode === 'list'}
		<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead class="bg-gray-50 border-b border-gray-200">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Job Details
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
						{#each jobs as job}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4">
									<div class="flex items-start gap-3">
										<div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
											<Briefcase class="w-5 h-5 text-blue-600" />
										</div>
										<div>
											<a href="/dashboard/jobs/{job.id}/" class="font-medium text-gray-900 hover:text-blue-600">
												{job.title}
											</a>
											<div class="flex items-center gap-3 mt-1 text-sm text-gray-500">
												<span>{job.department}</span>
												<span>•</span>
												<span class="flex items-center gap-1">
													<MapPin class="w-3 h-3" />
													{job.location}
												</span>
												<span>•</span>
												<span>{job.employmentType}</span>
											</div>
											{#if job.isExpiringSoon}
												<span class="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-orange-100 text-orange-800 text-xs font-medium rounded">
													<Calendar class="w-3 h-3" />
													Expires in {getDaysUntilExpiry(job.expiryDate)} days
												</span>
											{/if}
										</div>
									</div>
								</td>
								<td class="px-6 py-4 text-sm text-gray-600">
									{formatDate(job.postedDate)}
								</td>
								<td class="px-6 py-4 text-sm text-gray-600">
									{formatDate(job.expiryDate)}
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-4 text-sm">
										<div class="flex items-center gap-1 text-gray-600">
											<Eye class="w-4 h-4" />
											{job.views.toLocaleString()}
										</div>
										<div class="flex items-center gap-1 text-gray-600">
											<Users class="w-4 h-4" />
											{job.applicants}
										</div>
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-2">
										<a
											href="/dashboard/jobs/{job.id}/edit/"
											class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
											title="Edit"
										>
											<Edit class="w-4 h-4" />
										</a>
										<a
											href="/dashboard/jobs/{job.id}/"
											class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
											title="View"
										>
											<ExternalLink class="w-4 h-4" />
										</a>
										<button
											class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
											title="More options"
										>
											<MoreVertical class="w-4 h-4" />
										</button>
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
			{#each jobs as job}
				<div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
					<div class="flex items-start justify-between mb-4">
						<div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
							<Briefcase class="w-6 h-6 text-blue-600" />
						</div>
						<button class="p-1 text-gray-400 hover:text-gray-600">
							<MoreVertical class="w-5 h-5" />
						</button>
					</div>

					<a href="/dashboard/jobs/{job.id}/" class="block mb-3">
						<h3 class="text-lg font-semibold text-gray-900 hover:text-blue-600 line-clamp-2">
							{job.title}
						</h3>
					</a>

					<div class="space-y-2 text-sm text-gray-600 mb-4">
						<div class="flex items-center gap-2">
							<MapPin class="w-4 h-4" />
							{job.location}
						</div>
						<div class="flex items-center gap-2">
							<Calendar class="w-4 h-4" />
							Posted {formatDate(job.postedDate)}
						</div>
					</div>

					{#if job.isExpiringSoon}
						<div class="mb-4">
							<span class="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-800 text-xs font-medium rounded">
								<Calendar class="w-3 h-3" />
								Expires in {getDaysUntilExpiry(job.expiryDate)} days
							</span>
						</div>
					{/if}

					<div class="flex items-center justify-between mb-4 pt-4 border-t border-gray-200">
						<div class="flex items-center gap-1 text-sm text-gray-600">
							<Eye class="w-4 h-4" />
							{job.views.toLocaleString()}
						</div>
						<div class="flex items-center gap-1 text-sm text-gray-600">
							<Users class="w-4 h-4" />
							{job.applicants} applicants
						</div>
					</div>

					<div class="flex items-center gap-2">
						<a
							href="/dashboard/jobs/{job.id}/edit/"
							class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
						>
							<Edit class="w-4 h-4" />
							Edit
						</a>
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
</div>

<script lang="ts">
	import {
		Search,
		Filter,
		Download,
		Mail,
		MoreVertical,
		Star,
		Tag,
		Grid,
		List,
		User,
		MapPin,
		Briefcase,
		Calendar,
		Eye
	} from '@lucide/svelte';

	let searchQuery = $state('');
	let selectedStatus = $state('all');
	let viewMode = $state<'grid' | 'list'>('list');
	let selectedApplicants = $state<number[]>([]);

	// Mock data
	const applicants = [
		{
			id: 1,
			name: 'John Smith',
			email: 'john.smith@example.com',
			phone: '+1 (555) 123-4567',
			jobTitle: 'Senior Frontend Developer',
			appliedDate: '2025-10-18',
			status: 'New',
			rating: 0,
			tags: ['React', 'TypeScript'],
			experience: '5 years',
			location: 'San Francisco, CA',
			avatar: null
		},
		{
			id: 2,
			name: 'Sarah Johnson',
			email: 'sarah.j@example.com',
			phone: '+1 (555) 234-5678',
			jobTitle: 'Product Manager',
			appliedDate: '2025-10-18',
			status: 'In Review',
			rating: 4,
			tags: ['Product Strategy', 'Agile'],
			experience: '7 years',
			location: 'New York, NY',
			avatar: null
		},
		{
			id: 3,
			name: 'Michael Chen',
			email: 'mchen@example.com',
			phone: '+1 (555) 345-6789',
			jobTitle: 'UI/UX Designer',
			appliedDate: '2025-10-17',
			status: 'Shortlisted',
			rating: 5,
			tags: ['Figma', 'User Research'],
			experience: '4 years',
			location: 'Austin, TX',
			avatar: null
		},
		{
			id: 4,
			name: 'Emma Davis',
			email: 'emma.davis@example.com',
			phone: '+1 (555) 456-7890',
			jobTitle: 'Backend Developer',
			appliedDate: '2025-10-17',
			status: 'Interviewed',
			rating: 4,
			tags: ['Python', 'Django', 'PostgreSQL'],
			experience: '6 years',
			location: 'Seattle, WA',
			avatar: null
		},
		{
			id: 5,
			name: 'James Wilson',
			email: 'jwilson@example.com',
			phone: '+1 (555) 567-8901',
			jobTitle: 'Senior Frontend Developer',
			appliedDate: '2025-10-16',
			status: 'New',
			rating: 0,
			tags: ['Vue.js', 'JavaScript'],
			experience: '8 years',
			location: 'Remote',
			avatar: null
		},
		{
			id: 6,
			name: 'Lisa Anderson',
			email: 'l.anderson@example.com',
			phone: '+1 (555) 678-9012',
			jobTitle: 'Product Manager',
			appliedDate: '2025-10-15',
			status: 'Rejected',
			rating: 2,
			tags: ['Product Management'],
			experience: '3 years',
			location: 'Boston, MA',
			avatar: null
		}
	];

	const statusOptions = [
		{ value: 'all', label: 'All Applicants', count: applicants.length },
		{ value: 'new', label: 'New', count: 2 },
		{ value: 'in-review', label: 'In Review', count: 1 },
		{ value: 'shortlisted', label: 'Shortlisted', count: 1 },
		{ value: 'interviewed', label: 'Interviewed', count: 1 },
		{ value: 'rejected', label: 'Rejected', count: 1 },
		{ value: 'hired', label: 'Hired', count: 0 }
	];

	function getStatusColor(status: string): string {
		const colors: Record<string, string> = {
			New: 'bg-blue-100 text-blue-800',
			'In Review': 'bg-yellow-100 text-yellow-800',
			Shortlisted: 'bg-green-100 text-green-800',
			Interviewed: 'bg-purple-100 text-purple-800',
			Rejected: 'bg-red-100 text-red-800',
			Hired: 'bg-emerald-100 text-emerald-800'
		};
		return colors[status] || 'bg-gray-100 text-gray-800';
	}

	function toggleSelectApplicant(id: number) {
		if (selectedApplicants.includes(id)) {
			selectedApplicants = selectedApplicants.filter((a) => a !== id);
		} else {
			selectedApplicants = [...selectedApplicants, id];
		}
	}

	function selectAllApplicants() {
		if (selectedApplicants.length === applicants.length) {
			selectedApplicants = [];
		} else {
			selectedApplicants = applicants.map((a) => a.id);
		}
	}

	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function renderStars(rating: number): string {
		return '★'.repeat(rating) + '☆'.repeat(5 - rating);
	}
</script>

<svelte:head>
	<title>Applicants - PeelJobs Recruiter</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Applicants</h1>
			<p class="text-gray-600 mt-1">Review and manage job applicants</p>
		</div>
		{#if selectedApplicants.length > 0}
			<div class="flex items-center gap-3">
				<span class="text-sm text-gray-600">{selectedApplicants.length} selected</span>
				<button
					class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
				>
					<Mail class="w-4 h-4" />
					Send Email
				</button>
				<button
					class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
				>
					<Tag class="w-4 h-4" />
					Add Tag
				</button>
			</div>
		{/if}
	</div>

	<!-- Status Tabs -->
	<div class="bg-white rounded-lg border border-gray-200">
		<div class="overflow-x-auto">
			<div class="flex border-b border-gray-200">
				{#each statusOptions as status}
					<button
						onclick={() => (selectedStatus = status.value)}
						class="flex-shrink-0 px-6 py-3 text-sm font-medium transition-colors border-b-2 {selectedStatus ===
						status.value
							? 'border-blue-600 text-blue-600'
							: 'border-transparent text-gray-600 hover:text-gray-900'}"
					>
						{status.label}
						<span
							class="ml-2 px-2 py-0.5 rounded-full text-xs {selectedStatus === status.value
								? 'bg-blue-100 text-blue-600'
								: 'bg-gray-100 text-gray-600'}"
						>
							{status.count}
						</span>
					</button>
				{/each}
			</div>
		</div>
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
					placeholder="Search by name, email, or skills..."
					class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<!-- Actions -->
			<div class="flex items-center gap-3">
				<button
					class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
				>
					<Filter class="w-4 h-4" />
					Filters
				</button>

				<button
					class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
				>
					<Download class="w-4 h-4" />
					Export
				</button>

				<div class="flex border border-gray-300 rounded-lg overflow-hidden">
					<button
						onclick={() => (viewMode = 'list')}
						class="px-3 py-2 {viewMode === 'list' ? 'bg-gray-100' : 'bg-white'} hover:bg-gray-50"
						aria-label="List view"
					>
						<List class="w-4 h-4" />
					</button>
					<button
						onclick={() => (viewMode = 'grid')}
						class="px-3 py-2 {viewMode === 'grid' ? 'bg-gray-100' : 'bg-white'} hover:bg-gray-50"
						aria-label="Grid view"
					>
						<Grid class="w-4 h-4" />
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Applicants List/Grid -->
	{#if viewMode === 'list'}
		<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead class="bg-gray-50 border-b border-gray-200">
						<tr>
							<th class="px-6 py-3 text-left">
								<input
									type="checkbox"
									checked={selectedApplicants.length === applicants.length}
									onchange={selectAllApplicants}
									class="w-4 h-4 text-blue-600 rounded"
								/>
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Candidate
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Applied For
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Applied Date
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Rating
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Status
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Actions
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-200">
						{#each applicants as applicant}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4">
									<input
										type="checkbox"
										checked={selectedApplicants.includes(applicant.id)}
										onchange={() => toggleSelectApplicant(applicant.id)}
										class="w-4 h-4 text-blue-600 rounded"
									/>
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-3">
										<div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
											<User class="w-5 h-5 text-gray-600" />
										</div>
										<div>
											<a
												href="/dashboard/applicants/{applicant.id}/"
												class="font-medium text-gray-900 hover:text-blue-600"
											>
												{applicant.name}
											</a>
											<p class="text-sm text-gray-600">{applicant.email}</p>
										</div>
									</div>
								</td>
								<td class="px-6 py-4">
									<div>
										<p class="text-sm font-medium text-gray-900">{applicant.jobTitle}</p>
										<p class="text-xs text-gray-500 flex items-center gap-1 mt-1">
											<MapPin class="w-3 h-3" />
											{applicant.location}
										</p>
									</div>
								</td>
								<td class="px-6 py-4 text-sm text-gray-600">
									{formatDate(applicant.appliedDate)}
								</td>
								<td class="px-6 py-4">
									<div class="text-yellow-400 text-sm">
										{renderStars(applicant.rating)}
									</div>
								</td>
								<td class="px-6 py-4">
									<span class="px-3 py-1 rounded-full text-xs font-medium {getStatusColor(applicant.status)}">
										{applicant.status}
									</span>
								</td>
								<td class="px-6 py-4">
									<div class="flex items-center gap-2">
										<a
											href="/dashboard/applicants/{applicant.id}/"
											class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
											title="View"
										>
											<Eye class="w-4 h-4" />
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
			{#each applicants as applicant}
				<div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
					<div class="flex items-start justify-between mb-4">
						<div class="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
							<User class="w-6 h-6 text-gray-600" />
						</div>
						<div class="flex items-center gap-2">
							<input
								type="checkbox"
								checked={selectedApplicants.includes(applicant.id)}
								onchange={() => toggleSelectApplicant(applicant.id)}
								class="w-4 h-4 text-blue-600 rounded"
							/>
							<button class="p-1 text-gray-400 hover:text-gray-600">
								<MoreVertical class="w-5 h-5" />
							</button>
						</div>
					</div>

					<a href="/dashboard/applicants/{applicant.id}/" class="block mb-2">
						<h3 class="text-lg font-semibold text-gray-900 hover:text-blue-600">{applicant.name}</h3>
					</a>
					<p class="text-sm text-gray-600 mb-1">{applicant.email}</p>
					<p class="text-sm text-gray-600 mb-4">{applicant.phone}</p>

					<div class="space-y-2 mb-4">
						<div class="flex items-center gap-2 text-sm text-gray-600">
							<Briefcase class="w-4 h-4" />
							{applicant.jobTitle}
						</div>
						<div class="flex items-center gap-2 text-sm text-gray-600">
							<MapPin class="w-4 h-4" />
							{applicant.location}
						</div>
						<div class="flex items-center gap-2 text-sm text-gray-600">
							<Calendar class="w-4 h-4" />
							Applied {formatDate(applicant.appliedDate)}
						</div>
					</div>

					{#if applicant.tags.length > 0}
						<div class="flex flex-wrap gap-1 mb-4">
							{#each applicant.tags as tag}
								<span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">{tag}</span>
							{/each}
						</div>
					{/if}

					<div class="flex items-center justify-between pt-4 border-t border-gray-200">
						<div class="text-yellow-400 text-sm">
							{renderStars(applicant.rating)}
						</div>
						<span class="px-3 py-1 rounded-full text-xs font-medium {getStatusColor(applicant.status)}">
							{applicant.status}
						</span>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

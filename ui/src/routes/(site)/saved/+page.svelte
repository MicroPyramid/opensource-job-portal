<script lang="ts">
	import {
		Bookmark,
		Calendar,
		Building2,
		ExternalLink,
		Trash2,
		ChevronRight,
		MapPin,
		DollarSign,
		Clock,
		Search,
		Heart
	} from '@lucide/svelte';

	interface SavedJob {
		id: number;
		title: string;
		company: string;
		companyLogo: string | null;
		location: string;
		type: string;
		salary: string;
		posted: string;
		deadline: string | null;
	}

	// Mock saved jobs data
	let savedJobs = $state<SavedJob[]>([
		{
			id: 1,
			title: 'Frontend Developer',
			company: 'TechCorp',
			companyLogo: null,
			location: 'Remote',
			type: 'Full-time',
			salary: '$80k - $120k',
			posted: '2 days ago',
			deadline: '2025-05-15'
		},
		{
			id: 2,
			title: 'Senior React Engineer',
			company: 'StartupXYZ',
			companyLogo: null,
			location: 'San Francisco',
			type: 'Full-time',
			salary: '$120k - $160k',
			posted: '3 days ago',
			deadline: null
		},
		{
			id: 3,
			title: 'UI/UX Designer',
			company: 'Designify',
			companyLogo: null,
			location: 'Mumbai',
			type: 'Contract',
			salary: '$60k - $80k',
			posted: '5 days ago',
			deadline: '2025-04-30'
		},
		{
			id: 4,
			title: 'Full Stack Developer',
			company: 'WebSolutions',
			companyLogo: null,
			location: 'Bangalore',
			type: 'Full-time',
			salary: '$90k - $130k',
			posted: '1 week ago',
			deadline: null
		}
	]);

	let searchQuery = $state('');

	const filteredJobs = $derived(
		savedJobs.filter(
			(job) =>
				searchQuery === '' ||
				job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
				job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
				job.location.toLowerCase().includes(searchQuery.toLowerCase())
		)
	);

	function handleRemove(jobId: number) {
		if (confirm('Are you sure you want to remove this job from your saved list?')) {
			savedJobs = savedJobs.filter((job) => job.id !== jobId);
		}
	}
</script>

<svelte:head>
	<title>Saved Jobs - PeelJobs</title>
	<meta name="description" content="View all your saved jobs in one place" />
</svelte:head>

<!-- Hero Section -->
<section class="bg-gray-900 text-white py-12 lg:py-16 relative overflow-hidden">
	<!-- Decorative Elements -->
	<div class="absolute inset-0 overflow-hidden">
		<div class="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl"></div>
		<div class="absolute bottom-0 right-1/4 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl"></div>
	</div>

	<div class="max-w-7xl mx-auto px-4 lg:px-8 relative">
		<!-- Breadcrumb -->
		<nav class="mb-6" aria-label="Breadcrumb">
			<ol class="flex items-center gap-2 text-sm text-gray-400">
				<li>
					<a href="/jobseeker-dashboard/" class="hover:text-white transition-colors">Dashboard</a>
				</li>
				<li class="flex items-center gap-2">
					<ChevronRight size={14} />
					<span class="text-white font-medium">Saved Jobs</span>
				</li>
			</ol>
		</nav>

		<div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
			<div class="flex items-center gap-4">
				<div
					class="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center animate-fade-in-up"
					style="opacity: 0;"
				>
					<Bookmark size={28} class="text-primary-300" />
				</div>
				<div>
					<h1
						class="text-3xl lg:text-4xl font-bold tracking-tight mb-1 animate-fade-in-up"
						style="opacity: 0; animation-delay: 100ms;"
					>
						Saved Jobs
					</h1>
					<p
						class="text-gray-300 animate-fade-in-up"
						style="opacity: 0; animation-delay: 150ms;"
					>
						Keep track of jobs you're interested in
					</p>
				</div>
			</div>

			<!-- Stats -->
			<div
				class="flex items-center gap-3 animate-fade-in-up"
				style="opacity: 0; animation-delay: 200ms;"
			>
				<div class="bg-white/10 rounded-full px-4 py-2 backdrop-blur-sm">
					<span class="text-sm text-gray-300">Saved:</span>
					<span class="text-lg font-bold ml-1">{savedJobs.length}</span>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- Main Content -->
<section class="py-8 lg:py-12 bg-surface-50 min-h-[60vh]">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<!-- Search Bar -->
		<div
			class="bg-white rounded-2xl p-4 lg:p-5 elevation-1 border border-gray-100 mb-6 animate-fade-in-up"
			style="opacity: 0;"
		>
			<div class="relative">
				<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
					<Search size={18} class="text-gray-400" />
				</div>
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Search saved jobs by title, company, or location..."
					class="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
				/>
			</div>
		</div>

		<!-- Jobs Grid -->
		{#if filteredJobs.length === 0}
			<div
				class="bg-white rounded-2xl p-12 elevation-1 border border-gray-100 text-center animate-fade-in-up"
				style="opacity: 0; animation-delay: 100ms;"
			>
				<div
					class="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-6"
				>
					<Heart size={36} class="text-gray-400" />
				</div>
				<h3 class="text-xl font-semibold text-gray-900 mb-2">
					{searchQuery ? 'No jobs found' : 'No saved jobs yet'}
				</h3>
				<p class="text-gray-600 mb-6 max-w-md mx-auto">
					{searchQuery
						? 'Try adjusting your search to find what you are looking for.'
						: 'Browse jobs and save the ones you are interested in to review later.'}
				</p>
				<a
					href="/jobs/"
					class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-full hover:bg-primary-700 transition-colors elevation-1"
				>
					<Search size={18} />
					Browse Jobs
				</a>
			</div>
		{:else}
			<div class="grid md:grid-cols-2 gap-4 lg:gap-6">
				{#each filteredJobs as job, i}
					<div
						class="group bg-white rounded-2xl p-5 lg:p-6 elevation-1 hover:elevation-3 border border-gray-100 transition-all"
						style="animation: fade-in-up 0.5s ease forwards; animation-delay: {(i + 1) * 50}ms; opacity: 0;"
					>
						<div class="flex items-start gap-4">
							<!-- Company Logo -->
							<div
								class="w-14 h-14 rounded-xl bg-primary-50 flex items-center justify-center text-xl font-bold text-primary-600 flex-shrink-0"
							>
								{job.company.charAt(0)}
							</div>

							<!-- Job Info -->
							<div class="flex-1 min-w-0">
								<div class="flex items-start justify-between gap-2 mb-2">
									<h3
										class="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-1"
									>
										{job.title}
									</h3>
									<button
										onclick={() => handleRemove(job.id)}
										class="p-1.5 text-gray-400 hover:text-error-600 hover:bg-error-500/10 rounded-lg transition-colors flex-shrink-0"
										title="Remove from saved"
									>
										<Trash2 size={16} />
									</button>
								</div>

								<div class="flex items-center gap-2 text-sm text-gray-600 mb-3">
									<Building2 size={14} class="text-gray-400 flex-shrink-0" />
									<span class="truncate">{job.company}</span>
								</div>

								<!-- Meta Info -->
								<div class="flex flex-wrap items-center gap-3 text-sm text-gray-500 mb-4">
									<span class="flex items-center gap-1.5">
										<MapPin size={14} class="text-gray-400" />
										{job.location}
									</span>
									<span class="w-1 h-1 bg-gray-300 rounded-full"></span>
									<span>{job.type}</span>
								</div>

								<!-- Salary & Posted -->
								<div class="flex items-center justify-between mb-4">
									<span
										class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-success-500/10 text-success-600 text-sm font-medium rounded-full"
									>
										<DollarSign size={14} />
										{job.salary}
									</span>
									<span class="text-xs text-gray-500 flex items-center gap-1">
										<Clock size={12} />
										Posted {job.posted}
									</span>
								</div>

								{#if job.deadline}
									<div class="text-xs text-warning-600 bg-warning-500/10 px-3 py-1.5 rounded-lg mb-4">
										<Calendar size={12} class="inline mr-1" />
										Deadline: {new Date(job.deadline).toLocaleDateString('en-US', {
											month: 'short',
											day: 'numeric',
											year: 'numeric'
										})}
									</div>
								{/if}

								<!-- Actions -->
								<div class="flex items-center gap-2">
									<a
										href="/jobs/{job.id}/"
										class="flex-1 inline-flex items-center justify-center gap-1.5 px-4 py-2.5 bg-primary-600 text-white text-sm font-medium rounded-full hover:bg-primary-700 transition-colors"
									>
										<ExternalLink size={14} />
										View Job
									</a>
									<button
										class="px-4 py-2.5 text-sm font-medium text-primary-600 border border-primary-600 rounded-full hover:bg-primary-50 transition-colors"
									>
										Apply Now
									</button>
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}

		<!-- Summary Card -->
		{#if savedJobs.length > 0}
			<div
				class="mt-8 bg-primary-50 rounded-2xl p-5 lg:p-6 border border-primary-100 animate-fade-in-up"
				style="opacity: 0; animation-delay: 400ms;"
			>
				<div class="flex items-start gap-4">
					<div
						class="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center flex-shrink-0"
					>
						<Bookmark size={22} class="text-primary-600" />
					</div>
					<div>
						<h3 class="font-semibold text-gray-900 mb-1">
							{savedJobs.length} Job{savedJobs.length !== 1 ? 's' : ''} Saved
						</h3>
						<p class="text-sm text-gray-600">
							Don't miss out! Apply to your saved jobs before the deadlines.
							Jobs with upcoming deadlines are highlighted for your convenience.
						</p>
					</div>
				</div>
			</div>
		{/if}
	</div>
</section>

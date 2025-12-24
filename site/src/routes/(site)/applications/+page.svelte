<script lang="ts">
	import {
		FileText,
		Calendar,
		Building2,
		ExternalLink,
		XCircle,
		ChevronRight,
		Briefcase,
		MapPin,
		Clock,
		CheckCircle,
		Eye,
		Search,
		Filter,
		AlertCircle
	} from '@lucide/svelte';

	type ApplicationStatus = 'Under Review' | 'Interview' | 'Rejected' | 'Pending';

	interface Application {
		id: number;
		jobTitle: string;
		company: string;
		companyLogo: string | null;
		location: string;
		type: string;
		status: ApplicationStatus;
		applied: string;
	}

	// Mock applications data
	let applications = $state<Application[]>([
		{
			id: 1,
			jobTitle: 'Frontend Developer',
			company: 'TechCorp',
			companyLogo: null,
			location: 'Bangalore',
			type: 'Full-time',
			status: 'Under Review',
			applied: '2025-04-15'
		},
		{
			id: 2,
			jobTitle: 'Backend Engineer',
			company: 'DataSoft',
			companyLogo: null,
			location: 'Remote',
			type: 'Full-time',
			status: 'Interview',
			applied: '2025-04-10'
		},
		{
			id: 3,
			jobTitle: 'Full Stack Developer',
			company: 'WebSolutions',
			companyLogo: null,
			location: 'Mumbai',
			type: 'Contract',
			status: 'Pending',
			applied: '2025-04-08'
		},
		{
			id: 4,
			jobTitle: 'DevOps Engineer',
			company: 'CloudTech',
			companyLogo: null,
			location: 'Hyderabad',
			type: 'Full-time',
			status: 'Rejected',
			applied: '2025-04-05'
		}
	]);

	let filterStatus = $state<ApplicationStatus | 'All'>('All');
	let searchQuery = $state('');

	const statusConfig: Record<
		ApplicationStatus,
		{ icon: typeof AlertCircle; color: string; bgColor: string }
	> = {
		'Under Review': {
			icon: Eye,
			color: 'text-primary-600',
			bgColor: 'bg-primary-500/10'
		},
		Interview: {
			icon: CheckCircle,
			color: 'text-success-600',
			bgColor: 'bg-success-500/10'
		},
		Rejected: {
			icon: XCircle,
			color: 'text-error-600',
			bgColor: 'bg-error-500/10'
		},
		Pending: {
			icon: Clock,
			color: 'text-warning-600',
			bgColor: 'bg-warning-500/10'
		}
	};

	const filteredApplications = $derived(
		applications.filter((app) => {
			const matchesStatus = filterStatus === 'All' || app.status === filterStatus;
			const matchesSearch =
				searchQuery === '' ||
				app.jobTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
				app.company.toLowerCase().includes(searchQuery.toLowerCase());
			return matchesStatus && matchesSearch;
		})
	);

	const stats = $derived({
		total: applications.length,
		underReview: applications.filter((a) => a.status === 'Under Review').length,
		interview: applications.filter((a) => a.status === 'Interview').length,
		pending: applications.filter((a) => a.status === 'Pending').length
	});

	function handleWithdraw(appId: number) {
		if (confirm('Are you sure you want to withdraw this application?')) {
			applications = applications.filter((app) => app.id !== appId);
		}
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>My Applications - PeelJobs</title>
	<meta name="description" content="Track all your job applications in one place" />
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
					<span class="text-white font-medium">Applications</span>
				</li>
			</ol>
		</nav>

		<div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
			<div class="flex items-center gap-4">
				<div
					class="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center animate-fade-in-up"
					style="opacity: 0;"
				>
					<FileText size={28} class="text-primary-300" />
				</div>
				<div>
					<h1
						class="text-3xl lg:text-4xl font-bold tracking-tight mb-1 animate-fade-in-up"
						style="opacity: 0; animation-delay: 100ms;"
					>
						My Applications
					</h1>
					<p
						class="text-gray-300 animate-fade-in-up"
						style="opacity: 0; animation-delay: 150ms;"
					>
						Track the status of all your job applications
					</p>
				</div>
			</div>

			<!-- Stats Pills -->
			<div
				class="flex flex-wrap items-center gap-3 animate-fade-in-up"
				style="opacity: 0; animation-delay: 200ms;"
			>
				<div class="bg-white/10 rounded-full px-4 py-2 backdrop-blur-sm">
					<span class="text-sm text-gray-300">Total:</span>
					<span class="text-lg font-bold ml-1">{stats.total}</span>
				</div>
				<div class="bg-success-500/20 rounded-full px-4 py-2">
					<span class="text-sm text-success-300">Interviews:</span>
					<span class="text-lg font-bold ml-1">{stats.interview}</span>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- Main Content -->
<section class="py-8 lg:py-12 bg-surface-50 min-h-[60vh]">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<!-- Filters -->
		<div
			class="bg-white rounded-2xl p-4 lg:p-5 elevation-1 border border-gray-100 mb-6 animate-fade-in-up"
			style="opacity: 0;"
		>
			<div class="flex flex-col lg:flex-row gap-4">
				<!-- Search -->
				<div class="flex-1 relative">
					<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
						<Search size={18} class="text-gray-400" />
					</div>
					<input
						type="text"
						bind:value={searchQuery}
						placeholder="Search by job title or company..."
						class="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
					/>
				</div>

				<!-- Filter Tabs -->
				<div class="flex items-center gap-2 overflow-x-auto pb-1 lg:pb-0">
					<button
						onclick={() => (filterStatus = 'All')}
						class="px-4 py-2.5 rounded-full text-sm font-medium whitespace-nowrap transition-all {filterStatus ===
						'All'
							? 'bg-primary-600 text-white elevation-1'
							: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
					>
						All
					</button>
					<button
						onclick={() => (filterStatus = 'Under Review')}
						class="px-4 py-2.5 rounded-full text-sm font-medium whitespace-nowrap transition-all {filterStatus ===
						'Under Review'
							? 'bg-primary-600 text-white elevation-1'
							: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
					>
						Under Review
					</button>
					<button
						onclick={() => (filterStatus = 'Interview')}
						class="px-4 py-2.5 rounded-full text-sm font-medium whitespace-nowrap transition-all {filterStatus ===
						'Interview'
							? 'bg-primary-600 text-white elevation-1'
							: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
					>
						Interview
					</button>
					<button
						onclick={() => (filterStatus = 'Pending')}
						class="px-4 py-2.5 rounded-full text-sm font-medium whitespace-nowrap transition-all {filterStatus ===
						'Pending'
							? 'bg-primary-600 text-white elevation-1'
							: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
					>
						Pending
					</button>
				</div>
			</div>
		</div>

		<!-- Applications List -->
		{#if filteredApplications.length === 0}
			<div
				class="bg-white rounded-2xl p-12 elevation-1 border border-gray-100 text-center animate-fade-in-up"
				style="opacity: 0; animation-delay: 100ms;"
			>
				<div
					class="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-6"
				>
					<Briefcase size={36} class="text-gray-400" />
				</div>
				<h3 class="text-xl font-semibold text-gray-900 mb-2">
					{searchQuery || filterStatus !== 'All' ? 'No applications found' : 'No applications yet'}
				</h3>
				<p class="text-gray-600 mb-6 max-w-md mx-auto">
					{searchQuery || filterStatus !== 'All'
						? 'Try adjusting your search or filter to find what you are looking for.'
						: 'Start exploring jobs and apply to positions that match your skills.'}
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
			<div class="space-y-4">
				{#each filteredApplications as app, i}
					{@const config = statusConfig[app.status]}
					{@const StatusIcon = config.icon}
					<div
						class="group bg-white rounded-2xl p-5 lg:p-6 elevation-1 hover:elevation-3 border border-gray-100 transition-all"
						style="animation: fade-in-up 0.5s ease forwards; animation-delay: {(i + 1) * 50}ms; opacity: 0;"
					>
						<div class="flex flex-col lg:flex-row lg:items-center gap-4 lg:gap-6">
							<!-- Company Logo & Info -->
							<div class="flex items-start gap-4 flex-1 min-w-0">
								<div
									class="w-14 h-14 rounded-xl bg-primary-50 flex items-center justify-center text-xl font-bold text-primary-600 flex-shrink-0"
								>
									{app.company.charAt(0)}
								</div>

								<div class="flex-1 min-w-0">
									<h3
										class="text-lg font-semibold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors"
									>
										{app.jobTitle}
									</h3>
									<div class="flex items-center gap-2 text-sm text-gray-600 mb-2">
										<Building2 size={14} class="text-gray-400 flex-shrink-0" />
										<span class="truncate">{app.company}</span>
									</div>
									<div class="flex flex-wrap items-center gap-3 text-sm text-gray-500">
										<span class="flex items-center gap-1.5">
											<MapPin size={14} class="text-gray-400" />
											{app.location}
										</span>
										<span class="w-1 h-1 bg-gray-300 rounded-full"></span>
										<span>{app.type}</span>
									</div>
								</div>
							</div>

							<!-- Status & Actions -->
							<div class="flex flex-col lg:items-end gap-3">
								<!-- Status Badge -->
								<span
									class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium {config.bgColor} {config.color} w-fit"
								>
									<StatusIcon size={14} />
									{app.status}
								</span>

								<!-- Applied Date -->
								<div class="flex items-center gap-1.5 text-sm text-gray-500">
									<Calendar size={14} class="text-gray-400" />
									<span>Applied {formatDate(app.applied)}</span>
								</div>

								<!-- Action Buttons -->
								<div class="flex items-center gap-2">
									<a
										href="/jobs/{app.id}/"
										class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-primary-600 border border-primary-600 rounded-full hover:bg-primary-50 transition-colors"
									>
										<ExternalLink size={14} />
										<span>View Job</span>
									</a>
									{#if app.status !== 'Rejected'}
										<button
											onclick={() => handleWithdraw(app.id)}
											class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-error-600 border border-error-500 rounded-full hover:bg-error-500/10 transition-colors"
										>
											<XCircle size={14} />
											<span>Withdraw</span>
										</button>
									{/if}
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}

		<!-- Summary Card -->
		{#if applications.length > 0}
			<div
				class="mt-8 bg-primary-50 rounded-2xl p-5 lg:p-6 border border-primary-100 animate-fade-in-up"
				style="opacity: 0; animation-delay: 400ms;"
			>
				<div class="flex items-start gap-4">
					<div
						class="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center flex-shrink-0"
					>
						<FileText size={22} class="text-primary-600" />
					</div>
					<div>
						<h3 class="font-semibold text-gray-900 mb-1">Application Summary</h3>
						<p class="text-sm text-gray-600">
							You have {stats.total} application{stats.total !== 1 ? 's' : ''} in total.
							{#if stats.interview > 0}
								Congratulations on {stats.interview} interview{stats.interview !== 1
									? 's'
									: ''} scheduled!
							{/if}
							Keep your profile updated to increase your chances of getting hired.
						</p>
					</div>
				</div>
			</div>
		{/if}
	</div>
</section>

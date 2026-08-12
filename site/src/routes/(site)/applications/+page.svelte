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

	import type { AppliedJob, ApplicationStatus } from '$lib/types/jobs';

	let { data } = $props<{ data: { applications: AppliedJob[]; loadError?: string } }>();

	let filterStatus = $state<ApplicationStatus | 'All'>('All');
	let searchQuery = $state('');

	const applications = $derived(data.applications ?? []);
	const errorMessage = $derived(data.loadError ?? '');

	// Keys match POST_STATUS in peeldb.models — the recruiter sets these from
	// their applicants screen, so they are the only values that can arrive.
	const statusConfig: Record<
		ApplicationStatus,
		{ icon: typeof AlertCircle; color: string; bgColor: string; label: string }
	> = {
		Pending: {
			icon: Clock,
			color: 'text-warning',
			bgColor: 'bg-warning-light',
			label: 'Pending'
		},
		Shortlisted: {
			icon: Eye,
			color: 'text-primary',
			bgColor: 'bg-primary/10',
			label: 'Shortlisted'
		},
		Hired: {
			icon: CheckCircle,
			color: 'text-success',
			bgColor: 'bg-success-light',
			label: 'Hired'
		},
		Rejected: {
			icon: XCircle,
			color: 'text-error',
			bgColor: 'bg-error-light',
			label: 'Not selected'
		}
	};

	const filteredApplications = $derived(
		applications.filter((app: AppliedJob) => {
			const matchesStatus = filterStatus === 'All' || app.status === filterStatus;
			if (!matchesStatus) return false;
			if (searchQuery === '') return true;
			const q = searchQuery.toLowerCase();
			return (
				app.job.title.toLowerCase().includes(q) ||
				app.job.company_name?.toLowerCase().includes(q)
			);
		})
	);

	const stats = $derived({
		total: applications.length,
		shortlisted: applications.filter((a: AppliedJob) => a.status === 'Shortlisted').length,
		hired: applications.filter((a: AppliedJob) => a.status === 'Hired').length,
		pending: applications.filter((a: AppliedJob) => a.status === 'Pending').length
	});

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-IN', {
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
<section class="bg-[#1D2226] text-white py-12 lg:py-16 relative overflow-hidden">
	<!-- Decorative Elements -->
	<div class="absolute inset-0 overflow-hidden">
		<div class="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl"></div>
		<div class="absolute bottom-0 right-1/4 w-80 h-80 bg-primary/10 rounded-full blur-3xl"></div>
	</div>

	<div class="max-w-7xl mx-auto px-4 lg:px-8 relative">
		<!-- Breadcrumb -->
		<nav class="mb-6" aria-label="Breadcrumb">
			<ol class="flex items-center gap-2 text-sm text-muted">
				<li>
					<a href="/profile/" class="hover:text-white transition-colors">Dashboard</a>
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
					class="w-14 h-14 rounded-lg bg-white/10 flex items-center justify-center animate-fade-in-up"
					style="opacity: 0;"
				>
					<FileText size={28} class="text-white/80" />
				</div>
				<div>
					<h1
						class="text-3xl lg:text-4xl font-semibold tracking-tight mb-1 animate-fade-in-up"
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
					<span class="text-lg font-semibold ml-1">{stats.total}</span>
				</div>
				<div class="bg-primary/20 rounded-full px-4 py-2">
					<span class="text-sm text-gray-300">Shortlisted:</span>
					<span class="text-lg font-semibold ml-1">{stats.shortlisted}</span>
				</div>
				{#if stats.hired > 0}
					<div class="bg-success-light rounded-full px-4 py-2">
						<span class="text-sm text-success">Hired:</span>
						<span class="text-lg font-semibold ml-1">{stats.hired}</span>
					</div>
				{/if}
			</div>
		</div>
	</div>
</section>

<!-- Main Content -->
<section class="py-8 lg:py-12 bg-surface min-h-[60vh]">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<!-- Filters -->
		<div
			class="bg-white rounded-lg p-4 lg:p-5 shadow-sm border border-border mb-6 animate-fade-in-up"
			style="opacity: 0;"
		>
			<div class="flex flex-col lg:flex-row gap-4">
				<!-- Search -->
				<div class="flex-1 relative">
					<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
						<Search size={18} class="text-muted" />
					</div>
					<input
						type="text"
						bind:value={searchQuery}
						placeholder="Search by job title or company..."
						class="w-full pl-11 pr-4 py-3 border border-border rounded-xl bg-gray-50 text-black placeholder-muted focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none"
					/>
				</div>

				<!-- Filter Tabs -->
				<div class="flex items-center gap-2 overflow-x-auto pb-1 lg:pb-0">
					{#each ['All', 'Pending', 'Shortlisted', 'Hired', 'Rejected'] as const as tab (tab)}
						<button
							onclick={() => (filterStatus = tab)}
							class="px-4 py-2.5 rounded-full text-sm font-medium whitespace-nowrap transition-all {filterStatus ===
							tab
								? 'bg-primary text-white shadow-sm'
								: 'bg-gray-100 text-muted hover:bg-gray-200'}"
						>
							{tab === 'All' ? 'All' : statusConfig[tab].label}
						</button>
					{/each}
				</div>
			</div>
		</div>

		{#if errorMessage}
			<div
				class="bg-error-light border border-error/20 text-error rounded-lg p-4 mb-6 flex items-start gap-3"
				role="alert"
			>
				<AlertCircle size={18} class="flex-shrink-0 mt-0.5" />
				<div class="flex-1">
					<p class="font-medium">{errorMessage}</p>
				</div>
			</div>
		{/if}

		<!-- Applications List -->
		{#if filteredApplications.length === 0}
			<div
				class="bg-white rounded-lg p-12 shadow-sm border border-border text-center animate-fade-in-up"
				style="opacity: 0; animation-delay: 100ms;"
			>
				<div
					class="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-6"
				>
					<Briefcase size={36} class="text-muted" />
				</div>
				<h3 class="text-xl font-semibold text-black mb-2">
					{searchQuery || filterStatus !== 'All' ? 'No applications found' : 'No applications yet'}
				</h3>
				<p class="text-muted mb-6 max-w-md mx-auto">
					{searchQuery || filterStatus !== 'All'
						? 'Try adjusting your search or filter to find what you are looking for.'
						: 'Start exploring jobs and apply to positions that match your skills.'}
				</p>
				<a
					href="/jobs/"
					class="inline-flex items-center gap-2 px-6 py-3 bg-primary text-white font-medium rounded-full hover:bg-primary-hover transition-colors shadow-sm"
				>
					<Search size={18} />
					Browse Jobs
				</a>
			</div>
		{:else}
			<div class="space-y-4">
				{#each filteredApplications as app, i (app.id)}
					{@const config = statusConfig[app.status as ApplicationStatus]}
					{@const StatusIcon = config.icon}
					<div
						class="group bg-white rounded-lg p-5 lg:p-6 shadow-sm hover:shadow-lg border border-border transition-all"
						style="animation: fade-in-up 0.5s ease forwards; animation-delay: {(i + 1) * 50}ms; opacity: 0;"
					>
						<div class="flex flex-col lg:flex-row lg:items-center gap-4 lg:gap-6">
							<!-- Company Logo & Info -->
							<div class="flex items-start gap-4 flex-1 min-w-0">
								<div
									class="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center text-xl font-semibold text-primary flex-shrink-0 overflow-hidden"
								>
									{#if app.job.company_logo}
										<img
											src={app.job.company_logo}
											alt="{app.job.company_name} logo"
											class="w-full h-full object-cover"
										/>
									{:else}
										{app.job.company_name?.charAt(0) ?? '?'}
									{/if}
								</div>

								<div class="flex-1 min-w-0">
									<h3
										class="text-lg font-semibold text-black mb-1 group-hover:text-primary transition-colors"
									>
										{app.job.title}
									</h3>
									<div class="flex items-center gap-2 text-sm text-muted mb-2">
										<Building2 size={14} class="text-muted flex-shrink-0" />
										<span class="truncate">{app.job.company_name}</span>
									</div>
									<div class="flex flex-wrap items-center gap-3 text-sm text-muted">
										<span class="flex items-center gap-1.5">
											<MapPin size={14} class="text-muted" />
											{app.job.location_display}
										</span>
										<span class="w-1 h-1 bg-gray-300 rounded-full"></span>
										<span>{app.job.job_type}</span>
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
									{config.label}
								</span>

								<!-- Applied Date -->
								<div class="flex items-center gap-1.5 text-sm text-muted">
									<Calendar size={14} class="text-muted" />
									<span>Applied {formatDate(app.applied_on)}</span>
								</div>

								<!-- Action Buttons -->
								<div class="flex items-center gap-2">
									<a
										href="/jobs/{app.job.id}/"
										class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-primary border border-primary rounded-full hover:bg-primary/10 transition-colors"
									>
										<ExternalLink size={14} />
										<span>View Job</span>
									</a>
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
				class="mt-8 bg-primary/10 rounded-lg p-5 lg:p-6 border border-primary/20 animate-fade-in-up"
				style="opacity: 0; animation-delay: 400ms;"
			>
				<div class="flex items-start gap-4">
					<div
						class="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center flex-shrink-0"
					>
						<FileText size={22} class="text-primary" />
					</div>
					<div>
						<h3 class="font-semibold text-black mb-1">Application Summary</h3>
						<p class="text-sm text-muted">
							You have {stats.total} application{stats.total !== 1 ? 's' : ''} in total.
							{#if stats.hired > 0}
								Congratulations — you have been hired for {stats.hired} of them!
							{:else if stats.shortlisted > 0}
								{stats.shortlisted} of them {stats.shortlisted === 1 ? 'has' : 'have'} been
								shortlisted.
							{/if}
							Keep your profile updated to increase your chances of getting hired.
						</p>
					</div>
				</div>
			</div>
		{/if}
	</div>
</section>

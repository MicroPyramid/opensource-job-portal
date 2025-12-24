<script lang="ts">
	import {
		User,
		Briefcase,
		BookmarkIcon,
		Search,
		Bell,
		TrendingUp,
		Clock,
		CheckCircle,
		XCircle,
		AlertCircle,
		ChevronRight,
		FileText,
		MessageSquare,
		Eye,
		ArrowRight,
		Sparkles,
		Target,
		Calendar
	} from '@lucide/svelte';
	import type { PageData } from './$types';

	interface DashboardUser {
		name: string;
		profileCompletion: number;
		avatar: string;
		title: string;
		viewsThisWeek: number;
	}

	type JobStatus = 'pending' | 'reviewed' | 'interview' | 'rejected';

	interface AppliedJobSummary {
		id: number;
		title: string;
		company: string;
		status: JobStatus;
		appliedDate: string;
	}

	interface SavedJobSummary {
		id: number;
		title: string;
		company: string;
		location: string;
		salary: string;
	}

	const _: { data: PageData } = $props();
	void _;

	// Mock data - replace with actual data from your backend
	const user: DashboardUser = {
		name: 'John Doe',
		profileCompletion: 75,
		avatar: '/api/placeholder/80/80',
		title: 'Frontend Developer',
		viewsThisWeek: 24
	};

	const appliedJobs: AppliedJobSummary[] = [
		{
			id: 1,
			title: 'Frontend Developer',
			company: 'TechCorp',
			status: 'reviewed',
			appliedDate: '2024-01-15'
		},
		{
			id: 2,
			title: 'UX Designer',
			company: 'DesignStudio',
			status: 'pending',
			appliedDate: '2024-01-14'
		},
		{
			id: 3,
			title: 'Product Manager',
			company: 'StartupXYZ',
			status: 'rejected',
			appliedDate: '2024-01-10'
		},
		{
			id: 4,
			title: 'Full Stack Developer',
			company: 'WebSolutions',
			status: 'interview',
			appliedDate: '2024-01-12'
		}
	];

	const savedJobs: SavedJobSummary[] = [
		{
			id: 1,
			title: 'Senior React Developer',
			company: 'Meta',
			location: 'Remote',
			salary: '$120k - $150k'
		},
		{
			id: 2,
			title: 'Backend Engineer',
			company: 'Google',
			location: 'Mountain View',
			salary: '$140k - $180k'
		},
		{
			id: 3,
			title: 'DevOps Engineer',
			company: 'Amazon',
			location: 'Seattle',
			salary: '$130k - $160k'
		}
	];

	const statusConfig: Record<
		JobStatus,
		{ icon: typeof AlertCircle; color: string; bgColor: string }
	> = {
		pending: {
			icon: Clock,
			color: 'text-warning-600',
			bgColor: 'bg-warning-500/10'
		},
		reviewed: {
			icon: Eye,
			color: 'text-primary-600',
			bgColor: 'bg-primary-500/10'
		},
		interview: {
			icon: CheckCircle,
			color: 'text-success-600',
			bgColor: 'bg-success-500/10'
		},
		rejected: {
			icon: XCircle,
			color: 'text-error-600',
			bgColor: 'bg-error-500/10'
		}
	};

	const appliedJobsStats = $derived({
		total: appliedJobs.length,
		pending: appliedJobs.filter((job) => job.status === 'pending').length,
		reviewed: appliedJobs.filter((job) => job.status === 'reviewed').length,
		interview: appliedJobs.filter((job) => job.status === 'interview').length
	});

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>Dashboard - PeelJobs</title>
	<meta name="description" content="Manage your job search from your personalized dashboard" />
</svelte:head>

<!-- Hero Section -->
<section class="bg-gray-900 text-white py-12 lg:py-16 relative overflow-hidden">
	<!-- Decorative Elements -->
	<div class="absolute inset-0 overflow-hidden">
		<div class="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl"></div>
		<div class="absolute bottom-0 right-1/4 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl"></div>
	</div>

	<div class="max-w-7xl mx-auto px-4 lg:px-8 relative">
		<div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
			<!-- User Info -->
			<div class="flex items-center gap-5">
				<div class="relative">
					<img
						src={user.avatar}
						alt="Profile"
						class="w-16 h-16 lg:w-20 lg:h-20 rounded-full object-cover border-4 border-white/20"
					/>
					<div
						class="absolute -bottom-1 -right-1 w-6 h-6 bg-success-500 rounded-full border-2 border-gray-900 flex items-center justify-center"
					>
						<CheckCircle size={12} class="text-white" />
					</div>
				</div>
				<div>
					<h1
						class="text-2xl lg:text-3xl font-bold tracking-tight mb-1 animate-fade-in-up"
						style="opacity: 0;"
					>
						Welcome back, {user.name}!
					</h1>
					<p
						class="text-gray-300 text-base lg:text-lg animate-fade-in-up"
						style="opacity: 0; animation-delay: 100ms;"
					>
						{user.title}
					</p>
				</div>
			</div>

			<!-- Quick Stats -->
			<div
				class="flex items-center gap-4 animate-fade-in-up"
				style="opacity: 0; animation-delay: 200ms;"
			>
				<div class="bg-white/10 rounded-xl px-4 py-3 backdrop-blur-sm">
					<div class="flex items-center gap-2">
						<Eye size={18} class="text-primary-300" />
						<span class="text-sm text-gray-300">Profile Views</span>
					</div>
					<p class="text-2xl font-bold mt-1">{user.viewsThisWeek}</p>
				</div>
				<div class="bg-white/10 rounded-xl px-4 py-3 backdrop-blur-sm">
					<div class="flex items-center gap-2">
						<TrendingUp size={18} class="text-success-400" />
						<span class="text-sm text-gray-300">Applications</span>
					</div>
					<p class="text-2xl font-bold mt-1">{appliedJobsStats.total}</p>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- Main Content -->
<section class="py-8 lg:py-12 bg-surface-50">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<!-- Profile Completion Card -->
		{#if user.profileCompletion < 100}
			<div
				class="bg-white rounded-2xl p-6 elevation-1 mb-8 border border-gray-100 animate-fade-in-up"
				style="opacity: 0;"
			>
				<div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
					<div class="flex items-start gap-4">
						<div
							class="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center flex-shrink-0"
						>
							<Sparkles size={24} class="text-primary-600" />
						</div>
						<div>
							<h2 class="text-lg font-semibold text-gray-900 mb-1">Complete Your Profile</h2>
							<p class="text-sm text-gray-600">
								A complete profile gets 3x more views from recruiters
							</p>
						</div>
					</div>

					<div class="flex items-center gap-4 lg:gap-6">
						<div class="flex-1 lg:w-48">
							<div class="flex justify-between text-sm mb-2">
								<span class="text-gray-600">Progress</span>
								<span class="font-semibold text-primary-600">{user.profileCompletion}%</span>
							</div>
							<div class="w-full bg-gray-100 rounded-full h-2">
								<div
									class="bg-primary-600 rounded-full h-2 transition-all duration-500"
									style="width: {user.profileCompletion}%"
								></div>
							</div>
						</div>
						<a
							href="/profile/"
							class="px-5 py-2.5 bg-primary-600 text-white font-medium rounded-full hover:bg-primary-700 transition-colors elevation-1 flex items-center gap-2"
						>
							Update Profile
							<ArrowRight size={16} />
						</a>
					</div>
				</div>
			</div>
		{/if}

		<!-- Stats Grid -->
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
			<div
				class="bg-white rounded-2xl p-5 elevation-1 hover:elevation-3 transition-all border border-gray-100 animate-fade-in-up"
				style="opacity: 0; animation-delay: 100ms;"
			>
				<div class="flex items-center justify-between mb-4">
					<div class="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
						<Briefcase size={22} class="text-primary-600" />
					</div>
					<span class="text-3xl font-bold text-gray-900">{appliedJobsStats.total}</span>
				</div>
				<h3 class="font-medium text-gray-900">Applied Jobs</h3>
				<p class="text-sm text-gray-500 mt-0.5">Total applications</p>
			</div>

			<div
				class="bg-white rounded-2xl p-5 elevation-1 hover:elevation-3 transition-all border border-gray-100 animate-fade-in-up"
				style="opacity: 0; animation-delay: 150ms;"
			>
				<div class="flex items-center justify-between mb-4">
					<div class="w-12 h-12 rounded-xl bg-success-500/10 flex items-center justify-center">
						<Target size={22} class="text-success-600" />
					</div>
					<span class="text-3xl font-bold text-gray-900">{appliedJobsStats.interview}</span>
				</div>
				<h3 class="font-medium text-gray-900">Interviews</h3>
				<p class="text-sm text-gray-500 mt-0.5">Scheduled</p>
			</div>

			<div
				class="bg-white rounded-2xl p-5 elevation-1 hover:elevation-3 transition-all border border-gray-100 animate-fade-in-up"
				style="opacity: 0; animation-delay: 200ms;"
			>
				<div class="flex items-center justify-between mb-4">
					<div class="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center">
						<BookmarkIcon size={22} class="text-primary-600" />
					</div>
					<span class="text-3xl font-bold text-gray-900">{savedJobs.length}</span>
				</div>
				<h3 class="font-medium text-gray-900">Saved Jobs</h3>
				<p class="text-sm text-gray-500 mt-0.5">For later</p>
			</div>

			<div
				class="bg-white rounded-2xl p-5 elevation-1 hover:elevation-3 transition-all border border-gray-100 animate-fade-in-up"
				style="opacity: 0; animation-delay: 250ms;"
			>
				<div class="flex items-center justify-between mb-4">
					<div class="w-12 h-12 rounded-xl bg-warning-500/10 flex items-center justify-center">
						<Clock size={22} class="text-warning-600" />
					</div>
					<span class="text-3xl font-bold text-gray-900">{appliedJobsStats.pending}</span>
				</div>
				<h3 class="font-medium text-gray-900">Pending</h3>
				<p class="text-sm text-gray-500 mt-0.5">Under review</p>
			</div>
		</div>

		<!-- Main Grid -->
		<div class="grid lg:grid-cols-3 gap-6 lg:gap-8">
			<!-- Recent Applications -->
			<div class="lg:col-span-2">
				<div
					class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
					style="opacity: 0; animation-delay: 300ms;"
				>
					<div class="p-5 lg:p-6 border-b border-gray-100">
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div
									class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center"
								>
									<FileText size={20} class="text-primary-600" />
								</div>
								<h2 class="text-lg font-semibold text-gray-900">Recent Applications</h2>
							</div>
							<a
								href="/applications/"
								class="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center gap-1 group"
							>
								View All
								<ChevronRight
									size={16}
									class="group-hover:translate-x-0.5 transition-transform"
								/>
							</a>
						</div>
					</div>

					<div class="divide-y divide-gray-100">
						{#each appliedJobs.slice(0, 4) as job, i}
							{@const config = statusConfig[job.status]}
							<a
								href="/jobs/{job.id}/"
								class="group flex items-start justify-between p-5 lg:p-6 hover:bg-surface-50 transition-colors"
								style="animation: fade-in-up 0.5s ease forwards; animation-delay: {(i + 1) * 50 + 350}ms; opacity: 0;"
							>
								<div class="flex-1 min-w-0">
									<h3
										class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors mb-1"
									>
										{job.title}
									</h3>
									<p class="text-sm text-gray-600 mb-2">{job.company}</p>
									<div class="flex items-center gap-2 text-xs text-gray-500">
										<Calendar size={12} />
										<span>Applied {formatDate(job.appliedDate)}</span>
									</div>
								</div>
								<span
									class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium {config.bgColor} {config.color}"
								>
									<svelte:component this={config.icon} size={12} />
									{job.status.charAt(0).toUpperCase() + job.status.slice(1)}
								</span>
							</a>
						{/each}
					</div>

					{#if appliedJobs.length === 0}
						<div class="p-8 lg:p-12 text-center">
							<div
								class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4"
							>
								<Briefcase size={28} class="text-gray-400" />
							</div>
							<h3 class="text-lg font-semibold text-gray-900 mb-2">No applications yet</h3>
							<p class="text-sm text-gray-600 mb-4">
								Start exploring jobs and apply to your dream positions
							</p>
							<a
								href="/jobs/"
								class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white font-medium rounded-full hover:bg-primary-700 transition-colors"
							>
								<Search size={16} />
								Browse Jobs
							</a>
						</div>
					{/if}
				</div>
			</div>

			<!-- Sidebar -->
			<div class="space-y-6">
				<!-- Quick Actions -->
				<div
					class="bg-white rounded-2xl p-5 elevation-1 border border-gray-100 animate-fade-in-up"
					style="opacity: 0; animation-delay: 350ms;"
				>
					<h3 class="font-semibold text-gray-900 mb-4">Quick Actions</h3>
					<div class="space-y-2">
						<a
							href="/jobs/"
							class="group flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-primary-200 hover:bg-primary-50 transition-all"
						>
							<div
								class="w-10 h-10 rounded-xl bg-primary-50 group-hover:bg-primary-100 flex items-center justify-center transition-colors"
							>
								<Search size={18} class="text-primary-600" />
							</div>
							<span class="font-medium text-gray-900 group-hover:text-primary-600 transition-colors"
								>Search Jobs</span
							>
						</a>
						<a
							href="/profile/"
							class="group flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-success-200 hover:bg-success-50 transition-all"
						>
							<div
								class="w-10 h-10 rounded-xl bg-success-500/10 group-hover:bg-success-500/20 flex items-center justify-center transition-colors"
							>
								<User size={18} class="text-success-600" />
							</div>
							<span class="font-medium text-gray-900 group-hover:text-success-600 transition-colors"
								>Edit Profile</span
							>
						</a>
						<a
							href="/messages/"
							class="group flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-primary-200 hover:bg-primary-50 transition-all"
						>
							<div
								class="w-10 h-10 rounded-xl bg-primary-100 group-hover:bg-primary-200 flex items-center justify-center transition-colors"
							>
								<MessageSquare size={18} class="text-primary-600" />
							</div>
							<span class="font-medium text-gray-900 group-hover:text-primary-600 transition-colors"
								>Messages</span
							>
						</a>
						<a
							href="/resume/"
							class="group flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-primary-200 hover:bg-primary-50 transition-all"
						>
							<div
								class="w-10 h-10 rounded-xl bg-primary-50 group-hover:bg-primary-100 flex items-center justify-center transition-colors"
							>
								<FileText size={18} class="text-primary-600" />
							</div>
							<span class="font-medium text-gray-900 group-hover:text-primary-600 transition-colors"
								>My Resume</span
							>
						</a>
					</div>
				</div>

				<!-- Saved Jobs Preview -->
				<div
					class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
					style="opacity: 0; animation-delay: 400ms;"
				>
					<div class="p-5 border-b border-gray-100">
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div
									class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center"
								>
									<BookmarkIcon size={18} class="text-primary-600" />
								</div>
								<h3 class="font-semibold text-gray-900">Saved Jobs</h3>
							</div>
							<a
								href="/saved/"
								class="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center gap-1 group"
							>
								View All
								<ChevronRight
									size={14}
									class="group-hover:translate-x-0.5 transition-transform"
								/>
							</a>
						</div>
					</div>

					<div class="divide-y divide-gray-100">
						{#each savedJobs.slice(0, 3) as job, i}
							<a
								href="/jobs/{job.id}/"
								class="group block p-4 hover:bg-surface-50 transition-colors"
								style="animation: fade-in-up 0.5s ease forwards; animation-delay: {(i + 1) * 50 + 400}ms; opacity: 0;"
							>
								<h4
									class="font-medium text-gray-900 text-sm mb-1 group-hover:text-primary-600 transition-colors line-clamp-1"
								>
									{job.title}
								</h4>
								<p class="text-xs text-gray-600 mb-2">{job.company}</p>
								<div class="flex items-center justify-between">
									<span class="text-xs text-gray-500">{job.location}</span>
									<span class="text-xs font-medium text-success-600">{job.salary}</span>
								</div>
							</a>
						{/each}
					</div>

					{#if savedJobs.length === 0}
						<div class="p-6 text-center">
							<BookmarkIcon size={32} class="text-gray-300 mx-auto mb-2" />
							<p class="text-sm text-gray-500">No saved jobs yet</p>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</section>

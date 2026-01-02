<script lang="ts">
	import {
		MapPin,
		DollarSign,
		Clock,
		Building,
		Calendar,
		Users,
		Briefcase,
		GraduationCap,
		ArrowLeft,
		Eye,
		AlertCircle,
		CheckCircle2
	} from '@lucide/svelte';

	let { data } = $props();
	let job = $derived(data.job);

	function formatDate(dateString?: string): string {
		if (!dateString) return 'Not set';
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
	}

	function formatSalary(min: number, max: number, type: string): string {
		if (!min && !max) return 'Not disclosed';
		const formatAmount = (amount: number) => {
			if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)}Cr`;
			if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
			return `₹${(amount / 1000).toFixed(0)}K`;
		};
		const minStr = min ? formatAmount(min) : '';
		const maxStr = max ? formatAmount(max) : '';
		const range = minStr && maxStr ? `${minStr} - ${maxStr}` : minStr || maxStr;
		return `${range} per ${type === 'Month' ? 'month' : 'year'}`;
	}

	function formatExperience(minYear: number, maxYear: number, minMonth: number, maxMonth: number, fresher: boolean): string {
		if (fresher) return 'Fresher';
		if (!minYear && !maxYear) return 'Not specified';

		let exp = '';
		if (minYear === maxYear) {
			exp = `${minYear} year${minYear > 1 ? 's' : ''}`;
			if (minMonth || maxMonth) {
				const months = minMonth === maxMonth ? minMonth : `${minMonth}-${maxMonth}`;
				const monthsNum = typeof months === 'number' ? months : parseInt(months) || 0;
				exp += ` ${months} month${monthsNum > 1 ? 's' : ''}`;
			}
		} else {
			exp = `${minYear}-${maxYear} years`;
		}
		return exp;
	}

	function getStatusInfo(status: string) {
		switch (status) {
			case 'Live':
			case 'Published':
				return {
					color: 'bg-success-light border-success/30 text-success',
					icon: CheckCircle2,
					message: 'This job is currently live and visible to job seekers'
				};
			case 'Draft':
				return {
					color: 'bg-primary/10 border-primary/30 text-primary',
					icon: Eye,
					message: 'This is a preview of how your job will appear once published'
				};
			case 'Disabled':
				return {
					color: 'bg-error-light border-error/30 text-error',
					icon: AlertCircle,
					message: 'This job is currently closed and not accepting applications'
				};
			case 'Expired':
				return {
					color: 'bg-warning-light border-warning/30 text-warning',
					icon: AlertCircle,
					message: 'This job has expired and is no longer visible to job seekers'
				};
			default:
				return {
					color: 'bg-surface border-border text-black',
					icon: AlertCircle,
					message: 'Job preview'
				};
		}
	}

	let statusInfo = $derived(getStatusInfo(job.status));
	let StatusIcon = $derived(statusInfo.icon);
</script>

<svelte:head>
	<title>Preview: {job.title} - PeelJobs</title>
</svelte:head>

<div class="min-h-screen bg-surface">
	<!-- Preview Banner -->
	<div class="bg-white border-b border-border sticky top-0 z-10 shadow-sm">
		<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<div class="flex items-center justify-between gap-4">
				<div class="flex items-center gap-4">
					<a
						href="/dashboard/jobs/{job.id}/"
						class="p-2 hover:bg-surface rounded-lg transition-colors"
						title="Back to Job Details"
					>
						<ArrowLeft class="w-5 h-5" />
					</a>
					<div>
						<div class="flex items-center gap-2">
							<Eye class="w-5 h-5 text-primary" />
							<h1 class="text-lg font-semibold text-black">Job Preview</h1>
						</div>
						<p class="text-sm text-muted mt-0.5">How your job appears to candidates</p>
					</div>
				</div>
				<div class="flex gap-3">
					{#if job.status === 'Draft'}
						<a
							href="/dashboard/jobs/{job.id}/edit/"
							class="px-4 py-2 border border-border text-muted rounded-lg hover:bg-surface transition-colors text-sm font-medium"
						>
							Edit Job
						</a>
					{/if}
					<a
						href="/dashboard/jobs/{job.id}/"
						class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors text-sm font-medium"
					>
						Back to Dashboard
					</a>
				</div>
			</div>
		</div>
	</div>

	<!-- Status Info Banner -->
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
		<div class="border rounded-lg p-4 {statusInfo.color}">
			<div class="flex items-start gap-3">
				<StatusIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
				<div>
					<div class="font-medium">Preview Mode</div>
					<div class="text-sm mt-1">{statusInfo.message}</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Main Content - Mimics Public Job Page -->
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<div class="bg-white rounded-lg shadow-sm border border-border">
			<!-- Job Header -->
			<div class="p-6 border-b border-border">
				<div class="flex items-start justify-between gap-4 mb-4">
					<div class="flex-1">
						<h1 class="text-3xl font-bold text-black mb-2">{job.title}</h1>
						<div class="flex items-center gap-2 text-lg text-muted">
							<Building class="w-5 h-5" />
							<span>{job.company_name}</span>
						</div>
					</div>
				</div>

				<!-- Key Info Grid -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
					<div class="flex items-start gap-3">
						<div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
							<Briefcase class="w-5 h-5 text-primary" />
						</div>
						<div>
							<div class="text-sm text-muted">Job Type</div>
							<div class="font-medium text-black capitalize">
								{job.job_type.replace('-', ' ')}
							</div>
						</div>
					</div>

					<div class="flex items-start gap-3">
						<div class="w-10 h-10 bg-success-light rounded-lg flex items-center justify-center flex-shrink-0">
							<DollarSign class="w-5 h-5 text-success" />
						</div>
						<div>
							<div class="text-sm text-muted">Salary</div>
							<div class="font-medium text-black">
								{formatSalary(job.min_salary, job.max_salary, job.salary_type)}
							</div>
						</div>
					</div>

					<div class="flex items-start gap-3">
						<div class="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center flex-shrink-0">
							<Clock class="w-5 h-5 text-purple-600" />
						</div>
						<div>
							<div class="text-sm text-muted">Experience</div>
							<div class="font-medium text-black">
								{formatExperience(job.min_year, job.max_year, job.min_month, job.max_month, job.fresher)}
							</div>
						</div>
					</div>

					<div class="flex items-start gap-3">
						<div class="w-10 h-10 bg-warning-light rounded-lg flex items-center justify-center flex-shrink-0">
							<MapPin class="w-5 h-5 text-warning" />
						</div>
						<div>
							<div class="text-sm text-muted">Location</div>
							<div class="font-medium text-black">
								{job.location_display || 'Remote'}
							</div>
						</div>
					</div>
				</div>

				<!-- Additional Info -->
				<div class="flex flex-wrap gap-6 mt-6 pt-6 border-t border-border text-sm text-muted">
					{#if job.published_on}
						<div class="flex items-center gap-2">
							<Calendar class="w-4 h-4" />
							<span>Posted on {formatDate(job.published_on)}</span>
						</div>
					{/if}
					<div class="flex items-center gap-2">
						<Users class="w-4 h-4" />
						<span>{job.vacancies} {job.vacancies === 1 ? 'opening' : 'openings'}</span>
					</div>
					{#if job.work_mode}
						<div class="flex items-center gap-2">
							<Briefcase class="w-4 h-4" />
							<span class="capitalize">{job.work_mode.replace('-', ' ')}</span>
						</div>
					{/if}
				</div>
			</div>

			<!-- Job Description -->
			<div class="p-6 border-b border-border">
				<h2 class="text-xl font-semibold text-black mb-4">Job Description</h2>
				<div class="prose prose-sm max-w-none text-muted">
					{@html job.description || '<p class="text-muted">No description provided</p>'}
				</div>
			</div>

			<!-- Requirements -->
			<div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- Skills -->
				{#if job.skills && job.skills.length > 0}
					<div>
						<h3 class="text-lg font-semibold text-black mb-3 flex items-center gap-2">
							<CheckCircle2 class="w-5 h-5 text-success" />
							Required Skills
						</h3>
						<div class="flex flex-wrap gap-2">
							{#each job.skills as skill}
								<span class="px-3 py-1.5 bg-primary/10 text-primary rounded-full text-sm font-medium">
									{skill.name}
								</span>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Qualifications -->
				{#if job.qualifications && job.qualifications.length > 0}
					<div>
						<h3 class="text-lg font-semibold text-black mb-3 flex items-center gap-2">
							<GraduationCap class="w-5 h-5 text-purple-600" />
							Education
						</h3>
						<div class="flex flex-wrap gap-2">
							{#each job.qualifications as qual}
								<span class="px-3 py-1.5 bg-purple-50 text-purple-700 rounded-full text-sm font-medium">
									{qual.name}
								</span>
							{/each}
						</div>
					</div>
				{/if}
			</div>

			<!-- Company Info -->
			{#if job.company_description || job.company_address}
				<div class="p-6 border-t border-border bg-surface">
					<h2 class="text-xl font-semibold text-black mb-4">About {job.company_name}</h2>

					{#if job.company_description}
						<div class="prose prose-sm max-w-none text-muted mb-4">
							{@html job.company_description}
						</div>
					{/if}

					{#if job.company_address}
						<div class="flex items-start gap-2 text-sm text-muted">
							<MapPin class="w-4 h-4 mt-0.5" />
							<span>{job.company_address}</span>
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>

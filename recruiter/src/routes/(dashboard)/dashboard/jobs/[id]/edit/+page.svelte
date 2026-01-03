<script lang="ts">
	import {
		Briefcase,
		MapPin,
		FileText,
		DollarSign,
		Settings,
		Eye,
		ChevronRight,
		ChevronLeft,
		Save,
		Send,
		X,
		AlertCircle,
		CheckCircle
	} from '@lucide/svelte';
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import type { PageData, ActionData } from './$types';
	import type { WorkMode } from '$lib/types';

	// Receive data from server-side load function (Svelte 5 runes mode)
	let { data, form }: { data: PageData; form: ActionData | null | undefined } = $props();

	let currentStep = $state(1);
	const totalSteps = 6;

	// State for form submission
	let isSubmitting = $state(false);

	// Initialize form data from loaded job
	let formData = $state({
		// Step 1: Basics
		jobTitle: data.job.title || '',
		department: data.job.job_role || '',
		companyName: data.job.company_name || '',
		employmentType: data.job.job_type || 'full-time',
		experienceLevel: '',
		positions: data.job.vacancies || 1,

		// Step 2: Location
		country: '',
		state: '',
		city: '',
		workMode: (data.job.work_mode || 'in-office') as WorkMode,
		officeAddress: data.job.company_address || '',
		selectedLocationIds: data.job.locations?.map(loc => loc.id) || [],

		// Step 3: Details
		description: data.job.description || '',
		responsibilities: '',
		requirements: '',
		skills: data.job.skills?.map(s => s.name) || [],
		selectedSkillIds: data.job.skills?.map(s => s.id) || [],
		education: '',
		selectedQualificationIds: data.job.qualifications?.map(q => q.id) || [],
		selectedIndustryIds: data.job.industries?.map(i => i.id) || [],

		// Step 4: Compensation
		salaryMin: data.job.min_salary?.toString() || '',
		salaryMax: data.job.max_salary?.toString() || '',
		hideSalary: false,
		benefits: '',
		perks: '',

		// Step 5: Application Settings
		assignedRecruiters: [] as string[],
		autoReplyTemplate: ''
	});

	// Derive experience level from job data
	$effect(() => {
		if (data.job.fresher) {
			formData.experienceLevel = 'Fresher';
		} else if (data.job.min_year !== undefined && data.job.max_year !== undefined) {
			if (data.job.max_year <= 3) {
				formData.experienceLevel = '1-3 years';
			} else if (data.job.max_year <= 5) {
				formData.experienceLevel = '3-5 years';
			} else if (data.job.max_year <= 10) {
				formData.experienceLevel = '5-10 years';
			} else {
				formData.experienceLevel = '10+ years';
			}
		}
	});

	let newSkill = $state('');
	let searchSkill = $state('');

	// Filtered skills for searchable select
	let filteredSkills = $derived(
		data.metadata.skills.filter(skill =>
			skill.name.toLowerCase().includes(searchSkill.toLowerCase())
		).slice(0, 20)
	);

	const steps = [
		{ number: 1, title: 'Job Basics', icon: Briefcase },
		{ number: 2, title: 'Location', icon: MapPin },
		{ number: 3, title: 'Details', icon: FileText },
		{ number: 4, title: 'Compensation', icon: DollarSign },
		{ number: 5, title: 'Settings', icon: Settings },
		{ number: 6, title: 'Preview', icon: Eye }
	];

	const employmentTypes = ['Full-time', 'Part-time', 'Contract', 'Internship'];
	const experienceLevels = [
		'Fresher',
		'1-3 years',
		'3-5 years',
		'5-10 years',
		'10+ years'
	];
	const workModes: { value: WorkMode; label: string }[] = [
		{ value: 'in-office', label: 'In-Office' },
		{ value: 'remote', label: 'Remote' },
		{ value: 'hybrid', label: 'Hybrid' }
	];

	function nextStep() {
		if (currentStep < totalSteps) {
			currentStep++;
		}
	}

	function prevStep() {
		if (currentStep > 1) {
			currentStep--;
		}
	}

	function addSkill() {
		if (newSkill.trim()) {
			formData.skills = [...formData.skills, newSkill.trim()];
			newSkill = '';
		}
	}

	function removeSkill(index: number) {
		formData.skills = formData.skills.filter((_, i) => i !== index);
	}

	function toggleSkill(skillId: number) {
		if (formData.selectedSkillIds.includes(skillId)) {
			formData.selectedSkillIds = formData.selectedSkillIds.filter(id => id !== skillId);
		} else if (formData.selectedSkillIds.length < 8) {
			formData.selectedSkillIds = [...formData.selectedSkillIds, skillId];
		}
	}

	// Show success message and scroll to top
	$effect(() => {
		if (form?.success) {
			// Scroll to top to show success message
			window.scrollTo({ top: 0, behavior: 'smooth' });

			// Auto-dismiss success message after 5 seconds
			setTimeout(() => {
				form = null;
			}, 5000);
		}
	});
</script>

<svelte:head>
	<title>Edit Job - {data.job.title} - PeelJobs Recruiter</title>
</svelte:head>

<div class="max-w-5xl mx-auto space-y-6">
	<!-- Header -->
	<div>
		<h1 class="text-2xl md:text-3xl font-bold text-black">Edit Job</h1>
		<p class="text-muted mt-1">Update details for: {data.job.title}</p>
		<div class="mt-2 inline-flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/30 rounded-lg text-sm">
			<span class="font-medium text-primary">Status:</span>
			<span class="text-primary">{data.job.status}</span>
		</div>
	</div>

	<!-- Success/Error Messages -->
	{#if form?.success}
		<div class="bg-success-light border border-success/30 rounded-lg p-4 flex items-start gap-3">
			<CheckCircle class="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
			<div class="flex-1">
				<p class="text-sm font-medium text-success">{form.message || 'Job updated successfully!'}</p>
			</div>
			<button
				onclick={() => (form = null)}
				class="text-success hover:text-success transition-colors"
				aria-label="Dismiss"
			>
				<X class="w-4 h-4" />
			</button>
		</div>
	{/if}

	{#if form?.error}
		<div class="bg-error-light border border-error/30 rounded-lg p-4 flex items-start gap-3">
			<AlertCircle class="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
			<div class="flex-1">
				<p class="text-sm font-medium text-error">{form.error}</p>
			</div>
			<button
				onclick={() => (form = null)}
				class="text-error hover:text-error transition-colors"
				aria-label="Dismiss"
			>
				<X class="w-4 h-4" />
			</button>
		</div>
	{/if}

	<!-- Progress Steps -->
	<div class="bg-white rounded-lg border border-border p-6">
		<div class="flex items-center justify-between">
			{#each steps as step, index}
				<div class="flex items-center {index < steps.length - 1 ? 'flex-1' : ''}">
					<div class="flex flex-col items-center">
						<button
							type="button"
							onclick={() => (currentStep = step.number)}
							class="w-10 h-10 rounded-full flex items-center justify-center font-medium text-sm transition-colors {currentStep ===
							step.number
								? 'bg-primary text-white'
								: currentStep > step.number
									? 'bg-success text-white'
									: 'bg-surface text-muted'}"
						>
							{#if currentStep > step.number}
								✓
							{:else}
								{step.number}
							{/if}
						</button>
						<span
							class="text-xs mt-2 {currentStep === step.number
								? 'text-primary font-medium'
								: 'text-muted'} hidden md:block"
						>
							{step.title}
						</span>
					</div>
					{#if index < steps.length - 1}
						<div
							class="flex-1 h-0.5 mx-2 {currentStep > step.number ? 'bg-success' : 'bg-surface'}"
						></div>
					{/if}
				</div>
			{/each}
		</div>
	</div>

	<!-- Form -->
	<form
		method="POST"
		use:enhance={() => {
			isSubmitting = true;
			return async ({ result, update }) => {
				isSubmitting = false;
				await update();
			};
		}}
	>
		<!-- Hidden fields for all form data (needed because form fields are in conditional blocks) -->
		<!-- Step 1: Basics -->
		<input type="hidden" name="title" bind:value={formData.jobTitle} />
		<input type="hidden" name="job_role" bind:value={formData.department} />
		<input type="hidden" name="company_name" bind:value={formData.companyName} />
		<input type="hidden" name="job_type" bind:value={formData.employmentType} />
		<input type="hidden" name="vacancies" bind:value={formData.positions} />

		<!-- Step 2: Location & Work Mode -->
		<input type="hidden" name="work_mode" bind:value={formData.workMode} />
		{#each formData.selectedLocationIds as locationId}
			<input type="hidden" name="location_ids" value={locationId} />
		{/each}

		<!-- Step 3: Details -->
		<input type="hidden" name="description" bind:value={formData.description} />
		{#each formData.selectedSkillIds as skillId}
			<input type="hidden" name="skill_ids" value={skillId} />
		{/each}
		{#each formData.selectedIndustryIds as industryId}
			<input type="hidden" name="industry_ids" value={industryId} />
		{/each}
		{#each formData.selectedQualificationIds as qualificationId}
			<input type="hidden" name="qualification_ids" value={qualificationId} />
		{/each}

		<!-- Step 4: Compensation -->
		{#if formData.salaryMin}
			<input type="hidden" name="min_salary" value={formData.salaryMin} />
		{/if}
		{#if formData.salaryMax}
			<input type="hidden" name="max_salary" value={formData.salaryMax} />
		{/if}
		<input type="hidden" name="salary_type" value="Year" />

		<!-- Step 5: Application Settings -->

		<!-- Additional fields -->
		<input type="hidden" name="company_address" bind:value={formData.officeAddress} />
		<input type="hidden" name="company_description" bind:value={formData.benefits} />

		<!-- Form Content -->
		<div class="bg-white rounded-lg border border-border p-6 md:p-8">
			{#if currentStep === 1}
			<!-- Step 1: Job Basics -->
			<div class="space-y-6">
				<h2 class="text-xl font-semibold text-black flex items-center gap-2">
					<Briefcase class="w-6 h-6" />
					Job Basics
				</h2>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div class="md:col-span-2">
						<label for="edit-job-title" class="block text-sm font-medium text-muted mb-2">
							Job Title <span class="text-error">*</span>
						</label>
						<input
							id="edit-job-title"
							type="text"
							name="title"
							bind:value={formData.jobTitle}
							placeholder="e.g., Senior Frontend Developer"
							required
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						/>
					</div>

					<div>
						<label for="edit-company-name" class="block text-sm font-medium text-muted mb-2">
							Company Name <span class="text-error">*</span>
						</label>
						<input
							id="edit-company-name"
							type="text"
							name="company_name"
							bind:value={formData.companyName}
							placeholder="e.g., Acme Inc."
							required
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						/>
					</div>

					<div>
						<label for="edit-department" class="block text-sm font-medium text-muted mb-2">
							Department <span class="text-error">*</span>
						</label>
						<input
							id="edit-department"
							type="text"
							name="job_role"
							bind:value={formData.department}
							placeholder="e.g., Engineering"
							required
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						/>
					</div>

					<div>
						<label for="edit-employment-type" class="block text-sm font-medium text-muted mb-2">
							Employment Type <span class="text-error">*</span>
						</label>
						<select
							id="edit-employment-type"
							name="job_type"
							bind:value={formData.employmentType}
							required
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						>
							{#each employmentTypes as type}
								<option value={type.toLowerCase()}>{type}</option>
							{/each}
						</select>
					</div>

					<div>
						<label for="edit-experience-level" class="block text-sm font-medium text-muted mb-2">
							Experience Level <span class="text-error">*</span>
						</label>
						<select
							id="edit-experience-level"
							name="experience_level"
							bind:value={formData.experienceLevel}
							required
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						>
							<option value="">Select experience level</option>
							{#each experienceLevels as level}
								<option value={level}>{level}</option>
							{/each}
						</select>
					</div>

					<div>
						<label for="edit-positions" class="block text-sm font-medium text-muted mb-2">
							Number of Positions <span class="text-error">*</span>
						</label>
						<input
							id="edit-positions"
							type="number"
							name="vacancies"
							bind:value={formData.positions}
							min="1"
							required
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						/>
					</div>
				</div>
			</div>
		{:else if currentStep === 2}
			<!-- Step 2: Location & Work Mode -->
			<div class="space-y-6">
				<h2 class="text-xl font-semibold text-black flex items-center gap-2">
					<MapPin class="w-6 h-6" />
					Location & Work Mode
				</h2>

				<div>
					<label for="edit-work-mode" class="block text-sm font-medium text-muted mb-2">
						Work Mode <span class="text-error">*</span>
					</label>
					<div class="grid grid-cols-3 gap-3">
						{#each workModes as mode}
							<button
								type="button"
								onclick={() => (formData.workMode = mode.value)}
								class="px-4 py-3 rounded-lg border-2 font-medium text-sm transition-colors {formData.workMode ===
								mode.value
									? 'border-primary bg-primary/10 text-primary'
									: 'border-border text-muted hover:border-primary/50'}"
							>
								{mode.label}
							</button>
						{/each}
					</div>
				</div>

				<div>
					<label for="edit-current-locations" class="block text-sm font-medium text-muted mb-3">Current Locations</label>
					{#if data.job.locations && data.job.locations.length > 0}
						<div class="flex flex-wrap gap-2 mb-3">
							{#each data.job.locations as location}
								<span class="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
									{location.name}, {location.state}
								</span>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-muted mb-3">No locations set</p>
					{/if}
					<p class="text-xs text-muted">Note: Location editing coming soon. Please contact support to change locations.</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<div>
						<label for="edit-country" class="block text-sm font-medium text-muted mb-2">Country</label>
						<input
							id="edit-country"
							type="text"
							bind:value={formData.country}
							placeholder="e.g., United States"
							disabled
							class="w-full px-4 py-2 border border-border rounded-lg bg-surface"
						/>
					</div>

					<div>
						<label for="edit-state" class="block text-sm font-medium text-muted mb-2">State</label>
						<input
							id="edit-state"
							type="text"
							bind:value={formData.state}
							placeholder="e.g., California"
							disabled
							class="w-full px-4 py-2 border border-border rounded-lg bg-surface"
						/>
					</div>

					<div>
						<label for="edit-city" class="block text-sm font-medium text-muted mb-2">City</label>
						<input
							id="edit-city"
							type="text"
							bind:value={formData.city}
							placeholder="e.g., San Francisco"
							disabled
							class="w-full px-4 py-2 border border-border rounded-lg bg-surface"
						/>
					</div>
				</div>

				{#if formData.workMode !== 'remote'}
					<div>
						<label for="edit-office-address" class="block text-sm font-medium text-muted mb-2">Office Address</label>
						<textarea
							id="edit-office-address"
							bind:value={formData.officeAddress}
							rows="3"
							placeholder="Enter the full office address"
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						></textarea>
					</div>
				{/if}
			</div>
		{:else if currentStep === 3}
			<!-- Step 3: Job Details -->
			<div class="space-y-6">
				<h2 class="text-xl font-semibold text-black flex items-center gap-2">
					<FileText class="w-6 h-6" />
					Job Details
				</h2>

				<div>
					<label for="edit-description" class="block text-sm font-medium text-muted mb-2">
						Job Description <span class="text-error">*</span>
					</label>
					<textarea
						id="edit-description"
						name="description"
						bind:value={formData.description}
						rows="6"
						placeholder="Describe the role and what the candidate will be doing..."
						required
						class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
					></textarea>
				</div>

				<div>
					<label for="edit-responsibilities" class="block text-sm font-medium text-muted mb-2">Responsibilities</label>
					<textarea
						id="edit-responsibilities"
						bind:value={formData.responsibilities}
						rows="5"
						placeholder="List the key responsibilities (one per line)"
						class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
					></textarea>
				</div>

				<div>
					<label for="edit-requirements" class="block text-sm font-medium text-muted mb-2">
						Requirements <span class="text-error">*</span>
					</label>
					<textarea
						id="edit-requirements"
						bind:value={formData.requirements}
						rows="5"
						placeholder="List the requirements and qualifications (one per line)"
						class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
					></textarea>
				</div>

				<div>
					<label for="edit-search-skill" class="block text-sm font-medium text-muted mb-2">
						Key Skills <span class="text-muted text-xs">(Max 8)</span>
					</label>
					<div class="space-y-3">
						<input
							id="edit-search-skill"
							type="text"
							bind:value={searchSkill}
							placeholder="Search skills... (e.g., Python, React, AWS)"
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						/>

						{#if formData.selectedSkillIds.length > 0}
							<div class="flex flex-wrap gap-2">
								{#each formData.selectedSkillIds as skillId}
									{@const skill = data.metadata.skills.find(s => s.id === skillId)}
									{#if skill}
										<span class="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 text-primary rounded-lg text-sm">
											{skill.name}
											<button
												type="button"
												onclick={() => toggleSkill(skillId)}
												class="hover:text-primary-hover"
											>
												<X class="w-4 h-4" />
											</button>
										</span>
									{/if}
								{/each}
							</div>
						{/if}

						{#if searchSkill.length > 0}
							<div class="border border-border rounded-lg max-h-60 overflow-y-auto">
								{#each filteredSkills as skill}
									<button
										type="button"
										onclick={() => {
											if (formData.selectedSkillIds.length < 8 || formData.selectedSkillIds.includes(skill.id)) {
												toggleSkill(skill.id);
												searchSkill = '';
											}
										}}
										disabled={formData.selectedSkillIds.length >= 8 && !formData.selectedSkillIds.includes(skill.id)}
										class="w-full text-left px-4 py-2 hover:bg-surface flex items-center justify-between {formData.selectedSkillIds.includes(skill.id) ? 'bg-primary/10 text-primary' : ''} disabled:opacity-50 disabled:cursor-not-allowed"
									>
										<span class="text-sm">{skill.name}</span>
										{#if formData.selectedSkillIds.includes(skill.id)}
											<CheckCircle class="w-4 h-4 text-primary" />
										{/if}
									</button>
								{/each}
							</div>
						{/if}
					</div>
					<p class="text-xs text-muted mt-1">Select up to 8 key skills required for this role</p>
				</div>

				<div>
					<label for="edit-education" class="block text-sm font-medium text-muted mb-2">Education Requirements</label>
					<input
						id="edit-education"
						type="text"
						bind:value={formData.education}
						placeholder="e.g., Bachelor's degree in Computer Science or related field"
						class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
					/>
				</div>
			</div>
		{:else if currentStep === 4}
			<!-- Step 4: Compensation & Benefits -->
			<div class="space-y-6">
				<h2 class="text-xl font-semibold text-black flex items-center gap-2">
					<DollarSign class="w-6 h-6" />
					Compensation & Benefits
				</h2>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label for="edit-salary-min" class="block text-sm font-medium text-muted mb-2">Minimum Salary</label>
						<input
							id="edit-salary-min"
							type="number"
							bind:value={formData.salaryMin}
							placeholder="50000"
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						/>
					</div>

					<div>
						<label for="edit-salary-max" class="block text-sm font-medium text-muted mb-2">Maximum Salary</label>
						<input
							id="edit-salary-max"
							type="number"
							bind:value={formData.salaryMax}
							placeholder="80000"
							class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
						/>
					</div>
				</div>

				<div>
					<label for="edit-hide-salary" class="flex items-center gap-2 cursor-pointer">
						<input id="edit-hide-salary" type="checkbox" bind:checked={formData.hideSalary} class="w-4 h-4 text-primary rounded" />
						<span class="text-sm text-muted">Hide salary range from public job posting</span>
					</label>
				</div>

				<div>
					<label for="edit-benefits" class="block text-sm font-medium text-muted mb-2">Benefits</label>
					<textarea
						id="edit-benefits"
						bind:value={formData.benefits}
						rows="4"
						placeholder="List the benefits (e.g., Health insurance, 401k, etc.)"
						class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
					></textarea>
				</div>

				<div>
					<label for="edit-perks" class="block text-sm font-medium text-muted mb-2">Perks</label>
					<textarea
						id="edit-perks"
						bind:value={formData.perks}
						rows="4"
						placeholder="List additional perks (e.g., Flexible hours, Remote work, etc.)"
						class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
					></textarea>
				</div>
			</div>
		{:else if currentStep === 5}
			<!-- Step 5: Application Settings -->
			<div class="space-y-6">
				<h2 class="text-xl font-semibold text-black flex items-center gap-2">
					<Settings class="w-6 h-6" />
					Application Settings
				</h2>

				<div>
					<label for="edit-auto-reply" class="block text-sm font-medium text-muted mb-2">Auto-Reply Email Template</label>
					<textarea
						id="edit-auto-reply"
						bind:value={formData.autoReplyTemplate}
						rows="4"
						placeholder="Thank you for applying! We have received your application and will review it shortly..."
						class="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
					></textarea>
				</div>
			</div>
		{:else if currentStep === 6}
			<!-- Step 6: Preview -->
			<div class="space-y-6">
				<h2 class="text-xl font-semibold text-black flex items-center gap-2">
					<Eye class="w-6 h-6" />
					Preview & Update
				</h2>

				<div class="bg-surface rounded-lg p-6 space-y-4">
					<div>
						<h3 class="text-2xl font-bold text-black">{formData.jobTitle || 'Job Title'}</h3>
						<div class="flex flex-wrap gap-3 mt-2 text-sm text-muted">
							<span>{formData.department || 'Department'}</span>
							<span>•</span>
							<span>{formData.companyName || 'Company'}</span>
							<span>•</span>
							<span>{formData.employmentType}</span>
							<span>•</span>
							<span>{formData.workMode}</span>
						</div>
					</div>

					{#if formData.description}
						<div>
							<h4 class="font-semibold text-black mb-2">Description</h4>
							<p class="text-muted whitespace-pre-line">{formData.description}</p>
						</div>
					{/if}

					{#if formData.responsibilities}
						<div>
							<h4 class="font-semibold text-black mb-2">Responsibilities</h4>
							<p class="text-muted whitespace-pre-line">{formData.responsibilities}</p>
						</div>
					{/if}

					{#if formData.requirements}
						<div>
							<h4 class="font-semibold text-black mb-2">Requirements</h4>
							<p class="text-muted whitespace-pre-line">{formData.requirements}</p>
						</div>
					{/if}

					{#if data.job.skills && data.job.skills.length > 0}
						<div>
							<h4 class="font-semibold text-black mb-2">Required Skills</h4>
							<div class="flex flex-wrap gap-2">
								{#each data.job.skills as skill}
									<span class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">{skill.name}</span>
								{/each}
							</div>
						</div>
					{/if}

					{#if formData.salaryMin || formData.salaryMax}
						{#if !formData.hideSalary}
							<div>
								<h4 class="font-semibold text-black mb-2">Salary Range</h4>
								<p class="text-muted">
									${formData.salaryMin || '0'} - ${formData.salaryMax || '0'}
								</p>
							</div>
						{/if}
					{/if}
				</div>

				<div class="bg-primary/10 border border-primary/30 rounded-lg p-4">
					<p class="text-sm text-primary">
						<strong>Note:</strong> Changes will be saved to this job posting. If you publish, it will be visible to job seekers.
					</p>
				</div>
			</div>
		{/if}
	</div>

		<!-- Navigation Buttons -->
		<div class="flex items-center justify-between bg-white rounded-lg border border-border p-4">
			<button
				type="button"
				onclick={prevStep}
				disabled={currentStep === 1}
				class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-border rounded-lg text-sm font-medium text-muted hover:bg-surface disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
			>
				<ChevronLeft class="w-4 h-4" />
				Previous
			</button>

			<div class="flex items-center gap-3">
				<button
					type="submit"
					formaction="?/saveDraft"
					disabled={isSubmitting}
					class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-border rounded-lg text-sm font-medium text-muted hover:bg-surface disabled:opacity-50 transition-colors"
				>
					<Save class="w-4 h-4" />
					{isSubmitting ? 'Saving...' : 'Save Changes'}
				</button>

				{#if currentStep < totalSteps}
					<button
						type="button"
						onclick={nextStep}
						class="inline-flex items-center gap-2 px-6 py-2 bg-primary rounded-lg text-sm font-medium text-white hover:bg-primary-hover transition-colors"
					>
						Next
						<ChevronRight class="w-4 h-4" />
					</button>
				{:else}
					<button
						type="submit"
						formaction="?/publish"
						disabled={isSubmitting}
						class="inline-flex items-center gap-2 px-6 py-2 bg-success rounded-lg text-sm font-medium text-white hover:bg-success disabled:opacity-50 transition-colors"
					>
						<Send class="w-4 h-4" />
						{isSubmitting ? 'Publishing...' : data.job.status === 'Live' ? 'Update & Republish' : 'Update & Publish'}
					</button>
				{/if}
			</div>
		</div>
	</form>
</div>

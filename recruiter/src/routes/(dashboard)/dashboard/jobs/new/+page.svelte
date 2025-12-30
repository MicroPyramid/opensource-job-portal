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
		CheckCircle,
		Plus
	} from '@lucide/svelte';
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import type { PageData, ActionData } from './$types';
	import type { LanguageRequirement, SeniorityLevel, ApplicationMethod, LanguageProficiency, HiringTimeline, HiringPriority } from '$lib/types';

	// Receive data from server-side load function (Svelte 5 runes mode)
	let { data, form }: { data: PageData; form: ActionData | null | undefined } = $props();

	let currentStep = $state(1);
	const totalSteps = 7; // Increased from 6 to 7

	// State for form submission
	let isSubmitting = $state(false);
	let currentAction = $state<'saveDraft' | 'publish'>('publish');

	// Form data
	let formData = $state({
		// Step 1: Basics
		jobTitle: '',
		department: '',
		companyName: '',
		employmentType: 'full-time' as string,
		seniorityLevel: '' as SeniorityLevel | '',
		experienceLevel: '',
		positions: 1,

		// Step 2: Location
		selectedLocationIds: [] as number[],
		workMode: 'in-office' as string,
		officeAddress: '',
		searchCity: '',

		// Step 3: Details & Requirements
		description: '',
		selectedSkillIds: [] as number[],
		selectedIndustryIds: [] as number[],
		selectedQualificationIds: [] as number[],
		languages: [] as LanguageRequirement[],
		requiredCertifications: '',
		preferredCertifications: '',
		searchSkill: '',

		// Step 4: Compensation & Benefits
		salaryMin: '',
		salaryMax: '',
		salaryType: 'Year' as string,
		showSalary: true,
		benefits: [] as string[],

		// Step 5: Application Settings
		applicationMethod: 'portal' as ApplicationMethod,
		applicationUrl: '',
		deadline: '',

		// Step 6: Additional Settings
		relocationRequired: false,
		travelPercentage: '',
		hiringTimeline: '' as HiringTimeline | '',
		hiringPriority: 'Normal' as HiringPriority,

		// Experience mapping (computed from experienceLevel)
		minYear: 0,
		maxYear: 0,
		minMonth: 0,
		maxMonth: 0,
		fresher: false
	});

	// Initialize form with copied job data if copying
	$effect(() => {
		if (data.jobToCopy && data.isCopying) {
			const job = data.jobToCopy;

			// Step 1: Basics
			formData.jobTitle = job.title || '';
			formData.department = job.job_role || '';
			formData.companyName = job.company_name || '';
			formData.employmentType = job.job_type || 'full-time';
			formData.seniorityLevel = job.seniority_level || '';
			formData.positions = job.vacancies || 1;

			// Step 2: Location
			formData.selectedLocationIds = job.locations?.map((l: any) => l.id) || [];
			formData.workMode = job.work_mode || 'in-office';
			formData.officeAddress = job.company_address || '';

			// Step 3: Details
			formData.description = job.description || '';
			formData.selectedSkillIds = job.skills?.map((s: any) => s.id) || [];
			formData.selectedIndustryIds = job.industries?.map((i: any) => i.id) || [];
			formData.selectedQualificationIds = job.qualifications?.map((q: any) => q.id) || [];
			formData.languages = job.language_requirements || [];
			formData.requiredCertifications = job.required_certifications || '';
			formData.preferredCertifications = job.preferred_certifications || '';

			// Step 4: Compensation
			formData.salaryMin = job.min_salary?.toString() || '';
			formData.salaryMax = job.max_salary?.toString() || '';
			formData.salaryType = job.salary_type || 'Year';
			formData.showSalary = job.show_salary ?? true;
			formData.benefits = job.benefits || [];

			// Step 5: Application
			formData.applicationMethod = job.application_method || 'portal';
			formData.applicationUrl = job.application_url || '';

			// Step 6: Settings
			formData.relocationRequired = job.relocation_required || false;
			formData.travelPercentage = job.travel_percentage || '';
			formData.hiringTimeline = job.hiring_timeline || '';
			formData.hiringPriority = job.hiring_priority || 'Normal';

			// Experience
			formData.minYear = job.min_year || 0;
			formData.maxYear = job.max_year || 0;
			formData.minMonth = job.min_month || 0;
			formData.maxMonth = job.max_month || 0;
			formData.fresher = job.fresher || false;

			// Compute experience level string
			if (job.fresher) {
				formData.experienceLevel = 'Fresher';
			} else if (job.max_year >= 10) {
				formData.experienceLevel = '10+ years';
			} else if (job.max_year >= 5) {
				formData.experienceLevel = '5-10 years';
			} else if (job.max_year >= 3) {
				formData.experienceLevel = '3-5 years';
			} else {
				formData.experienceLevel = '1-3 years';
			}
		}
	});

	const steps = [
		{ number: 1, title: 'Basics', icon: Briefcase },
		{ number: 2, title: 'Location', icon: MapPin },
		{ number: 3, title: 'Details', icon: FileText },
		{ number: 4, title: 'Compensation', icon: DollarSign },
		{ number: 5, title: 'Application', icon: Send },
		{ number: 6, title: 'Settings', icon: Settings },
		{ number: 7, title: 'Preview', icon: Eye }
	];

	const employmentTypes = [
		{ value: 'full-time', label: 'Full-time' },
		{ value: 'permanent', label: 'Permanent' },
		{ value: 'contract', label: 'Contract' },
		{ value: 'part-time', label: 'Part-time' },
		{ value: 'internship', label: 'Internship' },
		{ value: 'freelance', label: 'Freelance' }
	];

	const seniorityLevels = [
		{ value: 'intern', label: 'Intern' },
		{ value: 'junior', label: 'Junior' },
		{ value: 'mid', label: 'Mid-Level' },
		{ value: 'senior', label: 'Senior' },
		{ value: 'lead', label: 'Lead' },
		{ value: 'manager', label: 'Manager' }
	];

	const experienceLevels = [
		'Fresher',
		'1-3 years',
		'3-5 years',
		'5-10 years',
		'10+ years'
	];

	const workModes = [
		{ value: 'in-office', label: 'In-Office' },
		{ value: 'remote', label: 'Remote' },
		{ value: 'hybrid', label: 'Hybrid' }
	];

	const benefitOptions = [
		'PF',
		'ESI',
		'Health Insurance',
		'Annual Bonus',
		'Food',
		'Cab',
		'Work From Home',
		'Flexible Hours'
	];

	const languageProficiencies: { value: LanguageProficiency; label: string }[] = [
		{ value: 'basic', label: 'Basic' },
		{ value: 'conversational', label: 'Conversational' },
		{ value: 'fluent', label: 'Fluent' }
	];

	const hiringTimelines: { value: HiringTimeline; label: string }[] = [
		{ value: '1-3days', label: '1-3 Days' },
		{ value: '1-2weeks', label: '1-2 Weeks' },
		{ value: '1month', label: '1 Month' },
		{ value: '1-3months', label: '1-3 Months' }
	];

	const hiringPriorities: { value: HiringPriority; label: string }[] = [
		{ value: 'Low', label: 'Low' },
		{ value: 'Normal', label: 'Normal' },
		{ value: 'High', label: 'High' }
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

	// Helper functions for managing selections
	function toggleSkill(skillId: number) {
		if (formData.selectedSkillIds.includes(skillId)) {
			formData.selectedSkillIds = formData.selectedSkillIds.filter(id => id !== skillId);
		} else {
			formData.selectedSkillIds = [...formData.selectedSkillIds, skillId];
		}
	}

	function toggleIndustry(industryId: number) {
		if (formData.selectedIndustryIds.includes(industryId)) {
			formData.selectedIndustryIds = formData.selectedIndustryIds.filter(id => id !== industryId);
		} else {
			formData.selectedIndustryIds = [...formData.selectedIndustryIds, industryId];
		}
	}

	function toggleQualification(qualId: number) {
		if (formData.selectedQualificationIds.includes(qualId)) {
			formData.selectedQualificationIds = formData.selectedQualificationIds.filter(id => id !== qualId);
		} else {
			formData.selectedQualificationIds = [...formData.selectedQualificationIds, qualId];
		}
	}

	function toggleLocation(cityId: number) {
		if (formData.selectedLocationIds.includes(cityId)) {
			formData.selectedLocationIds = formData.selectedLocationIds.filter(id => id !== cityId);
		} else {
			formData.selectedLocationIds = [...formData.selectedLocationIds, cityId];
		}
	}

	// Map experience level to min/max years
	$effect(() => {
		if (formData.experienceLevel === 'Fresher') {
			formData.minYear = 0;
			formData.maxYear = 0;
			formData.minMonth = 0;
			formData.maxMonth = 0;
			formData.fresher = true;
		} else if (formData.experienceLevel === '1-3 years') {
			formData.minYear = 1;
			formData.maxYear = 3;
			formData.minMonth = 0;
			formData.maxMonth = 0;
			formData.fresher = false;
		} else if (formData.experienceLevel === '3-5 years') {
			formData.minYear = 3;
			formData.maxYear = 5;
			formData.minMonth = 0;
			formData.maxMonth = 0;
			formData.fresher = false;
		} else if (formData.experienceLevel === '5-10 years') {
			formData.minYear = 5;
			formData.maxYear = 10;
			formData.minMonth = 0;
			formData.maxMonth = 0;
			formData.fresher = false;
		} else if (formData.experienceLevel === '10+ years') {
			formData.minYear = 10;
			formData.maxYear = 50; // Max cap
			formData.minMonth = 0;
			formData.maxMonth = 0;
			formData.fresher = false;
		}
	});

	// Filtered lists based on search
	let filteredCities = $derived(data.metadata.cities.filter(city =>
		city.name.toLowerCase().includes(formData.searchCity.toLowerCase())
	).slice(0, 20)); // Limit to 20 results

	let filteredSkills = $derived(data.metadata.skills.filter(skill =>
		skill.name.toLowerCase().includes(formData.searchSkill.toLowerCase())
	).slice(0, 20)); // Limit to 20 results

	function addLanguage() {
		formData.languages = [
			...formData.languages,
			{ language: '', proficiency: 'conversational' }
		];
	}

	function removeLanguage(index: number) {
		formData.languages = formData.languages.filter((_, i) => i !== index);
	}

	function toggleBenefit(benefit: string) {
		if (formData.benefits.includes(benefit)) {
			formData.benefits = formData.benefits.filter(b => b !== benefit);
		} else {
			formData.benefits = [...formData.benefits, benefit];
		}
	}

	// Handle form action results
	$effect(() => {
		if (form?.success && form?.jobId) {
			goto(`/dashboard/jobs/`);
		}
	});
</script>

<svelte:head>
	<title>Post New Job - PeelJobs Recruiter</title>
</svelte:head>

<div class="max-w-5xl mx-auto space-y-6">
	<!-- Header -->
	<div>
		<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Post New Job</h1>
		<p class="text-gray-600 mt-1">Fill in the details to create a new job posting</p>
	</div>

	<!-- Success/Error Messages -->
	{#if form?.success}
		<div class="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
			<CheckCircle class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
			<div>
				<p class="text-sm font-medium text-green-800">{form.message || 'Success!'}</p>
				{#if form.warning}
					<p class="text-sm text-green-700 mt-1">{form.warning}</p>
				{/if}
			</div>
		</div>
	{/if}

	{#if form?.error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
			<AlertCircle class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
			<div>
				<p class="text-sm font-medium text-red-800">{form.error}</p>
			</div>
		</div>
	{/if}

	<!-- Progress Steps -->
	<div class="bg-white rounded-lg border border-gray-200 p-6">
		<div class="flex items-center justify-between">
			{#each steps as step, index}
				<div class="flex items-center {index < steps.length - 1 ? 'flex-1' : ''}">
					<div class="flex flex-col items-center">
						<button
							type="button"
							onclick={() => (currentStep = step.number)}
							class="w-10 h-10 rounded-full flex items-center justify-center font-medium text-sm transition-colors {currentStep ===
							step.number
								? 'bg-blue-600 text-white'
								: currentStep > step.number
									? 'bg-green-600 text-white'
									: 'bg-gray-200 text-gray-600'}"
						>
							{#if currentStep > step.number}
								✓
							{:else}
								{step.number}
							{/if}
						</button>
						<span
							class="text-xs mt-2 {currentStep === step.number
								? 'text-blue-600 font-medium'
								: 'text-gray-600'} hidden md:block"
						>
							{step.title}
						</span>
					</div>
					{#if index < steps.length - 1}
						<div
							class="flex-1 h-0.5 mx-2 {currentStep > step.number ? 'bg-green-600' : 'bg-gray-200'}"
						></div>
					{/if}
				</div>
			{/each}
		</div>
	</div>

	<!-- Form -->
	<form
		method="POST"
		action="?/{currentAction}"
		use:enhance={() => {
			isSubmitting = true;
			return async ({ result, update }) => {
				isSubmitting = false;
				await update();
			};
		}}
	>
		<!-- Form Content -->
		<div class="bg-white rounded-lg border border-gray-200 p-6 md:p-8">
			{#if currentStep === 1}
				<!-- Step 1: Job Basics -->
				<div class="space-y-6">
					<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
						<Briefcase class="w-6 h-6" />
						Job Basics
					</h2>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div class="md:col-span-2">
							<label for="job-title" class="block text-sm font-medium text-gray-700 mb-2">
								Job Title <span class="text-red-500">*</span>
							</label>
							<input
								id="job-title"
								type="text"
								name="title"
								bind:value={formData.jobTitle}
								placeholder="e.g., Senior Frontend Developer"
								required
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>

						<div>
							<label for="company-name" class="block text-sm font-medium text-gray-700 mb-2">
								Company Name <span class="text-red-500">*</span>
							</label>
							<input
								id="company-name"
								type="text"
								name="company_name"
								bind:value={formData.companyName}
								placeholder="e.g., Acme Inc."
								required
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>

						<div>
							<label for="job-department" class="block text-sm font-medium text-gray-700 mb-2">
								Department <span class="text-red-500">*</span>
							</label>
							<input
								id="job-department"
								type="text"
								name="job_role"
								bind:value={formData.department}
								placeholder="e.g., Engineering"
								required
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>

						<div>
							<label for="employment-type" class="block text-sm font-medium text-gray-700 mb-2">
								Employment Type <span class="text-red-500">*</span>
							</label>
							<select
								id="employment-type"
								name="job_type"
								bind:value={formData.employmentType}
								required
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							>
								{#each employmentTypes as type}
									<option value={type.value}>{type.label}</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="seniority-level" class="block text-sm font-medium text-gray-700 mb-2">
								Seniority Level
							</label>
							<select
								id="seniority-level"
								name="seniority_level"
								bind:value={formData.seniorityLevel}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							>
								<option value="">Select level</option>
								{#each seniorityLevels as level}
									<option value={level.value}>{level.label}</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="experience-level" class="block text-sm font-medium text-gray-700 mb-2">
								Experience Level <span class="text-red-500">*</span>
							</label>
							<select
								id="experience-level"
								name="experience_level"
								bind:value={formData.experienceLevel}
								required
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							>
								<option value="">Select experience level</option>
								{#each experienceLevels as level}
									<option value={level}>{level}</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="number-of-positions" class="block text-sm font-medium text-gray-700 mb-2">
								Number of Positions <span class="text-red-500">*</span>
							</label>
							<input
								id="number-of-positions"
								type="number"
								name="vacancies"
								bind:value={formData.positions}
								min="1"
								required
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>
					</div>
				</div>

			{:else if currentStep === 2}
				<!-- Step 2: Location & Work Mode -->
				<div class="space-y-6">
					<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
						<MapPin class="w-6 h-6" />
						Location & Work Mode
					</h2>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div class="md:col-span-2">
							<label for="work-mode" class="block text-sm font-medium text-gray-700 mb-2">
								Work Mode <span class="text-red-500">*</span>
							</label>
							<div id="work-mode" class="grid grid-cols-3 gap-3">
								{#each workModes as mode}
									<label class="relative flex cursor-pointer">
										<input
											type="radio"
											name="work_mode"
											value={mode.value}
											bind:group={formData.workMode}
											class="peer sr-only"
										/>
										<div class="w-full py-3 px-4 text-center border-2 border-gray-200 rounded-lg peer-checked:border-blue-600 peer-checked:bg-blue-50 transition-colors">
											<span class="text-sm font-medium text-gray-700 peer-checked:text-blue-600">{mode.label}</span>
										</div>
									</label>
								{/each}
							</div>
						</div>

						<div class="md:col-span-2">
							<label for="job-locations-search" class="block text-sm font-medium text-gray-700 mb-2">
								Job Location(s) <span class="text-red-500">*</span> <span class="text-gray-500 text-xs">(Max 3)</span>
							</label>
							<div class="space-y-3">
								<input
									id="job-locations-search"
									type="text"
									bind:value={formData.searchCity}
									placeholder="Search city... (e.g., Bangalore, Mumbai)"
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									disabled={formData.selectedLocationIds.length >= 3}
								/>

								{#if formData.selectedLocationIds.length > 0}
									<div class="flex flex-wrap gap-2">
										{#each formData.selectedLocationIds as cityId}
											{@const city = data.metadata.cities.find(c => c.id === cityId)}
											{#if city}
												<span class="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-sm">
													{city.name}, {city.state?.name}
													<button
														type="button"
														onclick={() => toggleLocation(cityId)}
														class="hover:text-blue-900"
													>
														<X class="w-4 h-4" />
													</button>
												</span>
											{/if}
										{/each}
									</div>
								{/if}

								{#if formData.selectedLocationIds.length >= 3}
									<p class="text-sm text-orange-600">Maximum 3 locations reached. Remove a location to add another.</p>
								{/if}

								{#if formData.searchCity.length > 0}
									<div class="border border-gray-300 rounded-lg max-h-60 overflow-y-auto">
										{#each filteredCities as city}
											<button
												type="button"
												onclick={() => {
													if (formData.selectedLocationIds.length < 3 || formData.selectedLocationIds.includes(city.id)) {
														toggleLocation(city.id);
														formData.searchCity = '';
													}
												}}
												disabled={formData.selectedLocationIds.length >= 3 && !formData.selectedLocationIds.includes(city.id)}
												class="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center justify-between {formData.selectedLocationIds.includes(city.id) ? 'bg-blue-50 text-blue-700' : ''} disabled:opacity-50 disabled:cursor-not-allowed"
											>
												<span class="text-sm">{city.name}, {city.state?.name || 'N/A'}</span>
												{#if formData.selectedLocationIds.includes(city.id)}
													<CheckCircle class="w-4 h-4 text-blue-600" />
												{/if}
											</button>
										{/each}
									</div>
								{/if}
							</div>
							<p class="text-xs text-gray-500 mt-1">Select up to 3 cities where the job is available</p>
						</div>

						{#if formData.workMode !== 'remote'}
							<div class="md:col-span-2">
								<label for="new-office-address" class="block text-sm font-medium text-gray-700 mb-2">
									Office Address
								</label>
								<textarea
									id="new-office-address"
									name="company_address"
									bind:value={formData.officeAddress}
									rows="2"
									placeholder="Office address"
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								></textarea>
							</div>
						{/if}
					</div>
				</div>

			{:else if currentStep === 3}
				<!-- Step 3: Details & Requirements -->
				<div class="space-y-6">
					<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
						<FileText class="w-6 h-6" />
						Job Details & Requirements
					</h2>

					<div class="space-y-6">
						<div>
							<label for="job-description" class="block text-sm font-medium text-gray-700 mb-2">
								Job Description <span class="text-red-500">*</span>
							</label>
							<textarea
								id="job-description"
								name="description"
								bind:value={formData.description}
								rows="6"
								required
								placeholder="Describe the role, responsibilities, and what you're looking for..."
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							></textarea>
						</div>

						<div>
							<label for="key-skills-search" class="block text-sm font-medium text-gray-700 mb-2">
								Key Skills <span class="text-gray-500 text-xs">(Max 8)</span>
							</label>
							<div class="space-y-3">
								<input
									id="key-skills-search"
									type="text"
									bind:value={formData.searchSkill}
									placeholder="Search skills... (e.g., Python, React, AWS)"
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								/>

								{#if formData.selectedSkillIds.length > 0}
									<div class="flex flex-wrap gap-2">
										{#each formData.selectedSkillIds as skillId}
											{@const skill = data.metadata.skills.find(s => s.id === skillId)}
											{#if skill}
												<span class="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-sm">
													{skill.name}
													<button
														type="button"
														onclick={() => toggleSkill(skillId)}
														class="hover:text-blue-900"
													>
														<X class="w-4 h-4" />
													</button>
												</span>
											{/if}
										{/each}
									</div>
								{/if}

								{#if formData.searchSkill.length > 0}
									<div class="border border-gray-300 rounded-lg max-h-60 overflow-y-auto">
										{#each filteredSkills as skill}
											<button
												type="button"
												onclick={() => {
													if (formData.selectedSkillIds.length < 8 || formData.selectedSkillIds.includes(skill.id)) {
														toggleSkill(skill.id);
														formData.searchSkill = '';
													}
												}}
												disabled={formData.selectedSkillIds.length >= 8 && !formData.selectedSkillIds.includes(skill.id)}
												class="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center justify-between {formData.selectedSkillIds.includes(skill.id) ? 'bg-blue-50 text-blue-700' : ''} disabled:opacity-50 disabled:cursor-not-allowed"
											>
												<span class="text-sm">{skill.name}</span>
												{#if formData.selectedSkillIds.includes(skill.id)}
													<CheckCircle class="w-4 h-4 text-blue-600" />
												{/if}
											</button>
										{/each}
									</div>
								{/if}
							</div>
							<p class="text-xs text-gray-500 mt-1">Select up to 8 key skills required for this role</p>
						</div>

						<!-- Industries -->
						<div>
							<label for="industry-preferences" class="block text-sm font-medium text-gray-700 mb-2">
								Industry/Domain Preference
							</label>
							<div id="industry-preferences" class="border border-gray-300 rounded-lg p-3 max-h-60 overflow-y-auto">
								<div class="grid grid-cols-2 md:grid-cols-3 gap-2">
									{#each data.metadata.industries as industry}
										<label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
											<input
												type="checkbox"
												checked={formData.selectedIndustryIds.includes(industry.id)}
												onchange={() => toggleIndustry(industry.id)}
												class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
											/>
											<span class="text-sm text-gray-700">{industry.name}</span>
										</label>
									{/each}
								</div>
							</div>
							<p class="text-xs text-gray-500 mt-1">Select preferred industries for candidates</p>
						</div>

						<!-- Education/Qualifications -->
						<div>
							<label for="education-qualifications" class="block text-sm font-medium text-gray-700 mb-2">
								Education Qualification
							</label>
							<div id="education-qualifications" class="border border-gray-300 rounded-lg p-3 max-h-60 overflow-y-auto">
								<div class="grid grid-cols-2 md:grid-cols-3 gap-2">
									{#each data.metadata.qualifications as qual}
										<label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
											<input
												type="checkbox"
												checked={formData.selectedQualificationIds.includes(qual.id)}
												onchange={() => toggleQualification(qual.id)}
												class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
											/>
											<span class="text-sm text-gray-700">{qual.name}</span>
										</label>
									{/each}
								</div>
							</div>
							<p class="text-xs text-gray-500 mt-1">Select minimum education qualifications required</p>
						</div>

						<!-- Language Requirements -->
						<div>
							<label for="language-requirements" class="block text-sm font-medium text-gray-700 mb-2">
								Language Requirements
							</label>
							<div id="language-requirements" class="space-y-3">
								{#each formData.languages as lang, index}
									<div class="flex gap-3 items-start">
										<input
											id="language-{index}"
											type="text"
											bind:value={lang.language}
											placeholder="Language (e.g., English)"
											class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
										/>
										<select
											id="proficiency-{index}"
											bind:value={lang.proficiency}
											class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
										>
											{#each languageProficiencies as prof}
												<option value={prof.value}>{prof.label}</option>
											{/each}
										</select>
										<button
											type="button"
											onclick={() => removeLanguage(index)}
											class="p-2 text-red-600 hover:bg-red-50 rounded-lg"
										>
											<X class="w-5 h-5" />
										</button>
									</div>
								{/each}
								<button
									type="button"
									onclick={addLanguage}
									class="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-2"
								>
									<Plus class="w-4 h-4" />
									Add Language
								</button>
							</div>
						</div>

						<!-- Certifications -->
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<div>
								<label for="required-certifications" class="block text-sm font-medium text-gray-700 mb-2">
									Required Certifications
								</label>
								<textarea
									id="required-certifications"
									name="required_certifications"
									bind:value={formData.requiredCertifications}
									placeholder="e.g., AWS Solutions Architect, Azure Administrator"
									rows="3"
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								></textarea>
								<p class="text-xs text-gray-500 mt-1">Comma-separated list</p>
							</div>

							<div>
								<label for="preferred-certifications" class="block text-sm font-medium text-gray-700 mb-2">
									Preferred Certifications
								</label>
								<textarea
									id="preferred-certifications"
									name="preferred_certifications"
									bind:value={formData.preferredCertifications}
									placeholder="e.g., PMP, ISTQB"
									rows="3"
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								></textarea>
								<p class="text-xs text-gray-500 mt-1">Nice-to-have certifications</p>
							</div>
						</div>
					</div>
				</div>

			{:else if currentStep === 4}
				<!-- Step 4: Compensation & Benefits -->
				<div class="space-y-6">
					<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
						<DollarSign class="w-6 h-6" />
						Compensation & Benefits
					</h2>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<label for="minimum-salary" class="block text-sm font-medium text-gray-700 mb-2">
								Minimum Salary (INR)
							</label>
							<input
								id="minimum-salary"
								type="number"
								name="min_salary"
								bind:value={formData.salaryMin}
								placeholder="e.g., 500000"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>

						<div>
							<label for="maximum-salary" class="block text-sm font-medium text-gray-700 mb-2">
								Maximum Salary (INR)
							</label>
							<input
								id="maximum-salary"
								type="number"
								name="max_salary"
								bind:value={formData.salaryMax}
								placeholder="e.g., 800000"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>

						<div class="md:col-span-2">
							<label class="flex items-center gap-3 cursor-pointer">
								<input
									id="show-salary"
									type="checkbox"
									name="show_salary"
									bind:checked={formData.showSalary}
									class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
								/>
								<span class="text-sm font-medium text-gray-700">
									Show salary range to job seekers
								</span>
							</label>
						</div>

						<!-- Benefits & Perks -->
						<div class="md:col-span-2">
							<label for="benefits-perks" class="block text-sm font-medium text-gray-700 mb-3">
								Benefits & Perks
							</label>
							<div id="benefits-perks" class="grid grid-cols-2 md:grid-cols-4 gap-3">
								{#each benefitOptions as benefit}
									<label class="flex items-center gap-2 cursor-pointer">
										<input
											type="checkbox"
											checked={formData.benefits.includes(benefit)}
											onchange={() => toggleBenefit(benefit)}
											class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
										/>
										<span class="text-sm text-gray-700">{benefit}</span>
									</label>
								{/each}
							</div>
						</div>
					</div>
				</div>

			{:else if currentStep === 5}
				<!-- Step 5: Application Settings -->
				<div class="space-y-6">
					<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
						<Send class="w-6 h-6" />
						Application Settings
					</h2>

					<div class="space-y-6">
						<!-- Application Method -->
						<div>
							<label for="application-method" class="block text-sm font-medium text-gray-700 mb-3">
								Application Method <span class="text-red-500">*</span>
							</label>
							<div id="application-method" class="space-y-3">
								<label class="flex items-center gap-3 cursor-pointer p-3 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors {formData.applicationMethod === 'portal' ? 'border-blue-600 bg-blue-50' : ''}">
									<input
										type="radio"
										name="application_method"
										value="portal"
										bind:group={formData.applicationMethod}
										class="w-4 h-4 text-blue-600"
									/>
									<div>
										<div class="text-sm font-medium text-gray-900">Apply on PeelJobs Portal</div>
										<div class="text-xs text-gray-500">Candidates apply through our platform</div>
									</div>
								</label>
								<label class="flex items-center gap-3 cursor-pointer p-3 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors {formData.applicationMethod === 'external' ? 'border-blue-600 bg-blue-50' : ''}">
									<input
										type="radio"
										name="application_method"
										value="external"
										bind:group={formData.applicationMethod}
										class="w-4 h-4 text-blue-600"
									/>
									<div>
										<div class="text-sm font-medium text-gray-900">External URL</div>
										<div class="text-xs text-gray-500">Redirect to your company careers page</div>
									</div>
								</label>
								<label class="flex items-center gap-3 cursor-pointer p-3 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors {formData.applicationMethod === 'email' ? 'border-blue-600 bg-blue-50' : ''}">
									<input
										type="radio"
										name="application_method"
										value="email"
										bind:group={formData.applicationMethod}
										class="w-4 h-4 text-blue-600"
									/>
									<div>
										<div class="text-sm font-medium text-gray-900">Email</div>
										<div class="text-xs text-gray-500">Candidates apply via email</div>
									</div>
								</label>
							</div>

							{#if formData.applicationMethod === 'external'}
								<div class="mt-3">
									<label for="application-url" class="sr-only">Application URL</label>
									<input
										id="application-url"
										type="url"
										name="application_url"
										bind:value={formData.applicationUrl}
										placeholder="https://example.com/apply"
										class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									/>
								</div>
							{/if}
						</div>

						<div>
							<label for="application-deadline" class="block text-sm font-medium text-gray-700 mb-2">
								Application Deadline
							</label>
							<input
								id="application-deadline"
								type="date"
								name="deadline"
								bind:value={formData.deadline}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>
					</div>
				</div>

			{:else if currentStep === 6}
				<!-- Step 6: Additional Settings -->
				<div class="space-y-6">
					<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
						<Settings class="w-6 h-6" />
						Additional Settings
					</h2>

					<div class="space-y-6">
						<!-- Relocation & Travel -->
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<div>
								<label class="flex items-center gap-3 cursor-pointer">
									<input
										id="relocation-required"
										type="checkbox"
										name="relocation_required"
										bind:checked={formData.relocationRequired}
										class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
									/>
									<span class="text-sm font-medium text-gray-700">
										Relocation Required
									</span>
								</label>
							</div>

							<div>
								<label for="travel-requirements" class="block text-sm font-medium text-gray-700 mb-2">
									Travel Requirements
								</label>
								<select
									id="travel-requirements"
									name="travel_percentage"
									bind:value={formData.travelPercentage}
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								>
									<option value="">No travel required</option>
									<option value="0-10%">0-10%</option>
									<option value="10-25%">10-25%</option>
									<option value="25-50%">25-50%</option>
									<option value="50%+">50%+</option>
								</select>
							</div>
						</div>

						<!-- Hiring Urgency -->
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<div>
								<label for="hiring-timeline" class="block text-sm font-medium text-gray-700 mb-2">
									Hiring Timeline
								</label>
								<select
									id="hiring-timeline"
									name="hiring_timeline"
									bind:value={formData.hiringTimeline}
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								>
									<option value="">Select timeline</option>
									{#each hiringTimelines as timeline}
										<option value={timeline.value}>{timeline.label}</option>
									{/each}
								</select>
							</div>

							<div>
								<label for="hiring-priority" class="block text-sm font-medium text-gray-700 mb-2">
									Priority <span class="text-red-500">*</span>
								</label>
								<select
									id="hiring-priority"
									name="hiring_priority"
									bind:value={formData.hiringPriority}
									required
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								>
									{#each hiringPriorities as priority}
										<option value={priority.value}>{priority.label}</option>
									{/each}
								</select>
							</div>
						</div>
					</div>
				</div>

			{:else if currentStep === 7}
				<!-- Step 7: Preview -->
				<div class="space-y-6">
					<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
						<Eye class="w-6 h-6" />
						Preview & Submit
					</h2>

					<div class="space-y-6 border border-gray-200 rounded-lg p-6">
						<!-- Job Basics -->
						<div>
							<h3 class="font-semibold text-gray-900 mb-3">Job Basics</h3>
							<dl class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
								<div>
									<dt class="text-gray-500">Job Title</dt>
									<dd class="text-gray-900 font-medium">{formData.jobTitle || 'Not set'}</dd>
								</div>
								<div>
									<dt class="text-gray-500">Company</dt>
									<dd class="text-gray-900 font-medium">{formData.companyName || 'Not set'}</dd>
								</div>
								<div>
									<dt class="text-gray-500">Employment Type</dt>
									<dd class="text-gray-900 font-medium capitalize">{formData.employmentType}</dd>
								</div>
								<div>
									<dt class="text-gray-500">Seniority Level</dt>
									<dd class="text-gray-900 font-medium capitalize">{formData.seniorityLevel || 'Not set'}</dd>
								</div>
								<div>
									<dt class="text-gray-500">Work Mode</dt>
									<dd class="text-gray-900 font-medium capitalize">{formData.workMode}</dd>
								</div>
								<div>
									<dt class="text-gray-500">Positions</dt>
									<dd class="text-gray-900 font-medium">{formData.positions}</dd>
								</div>
							</dl>
						</div>

						<!-- Compensation -->
						{#if formData.salaryMin || formData.salaryMax}
							<div>
								<h3 class="font-semibold text-gray-900 mb-3">Compensation</h3>
								<p class="text-sm text-gray-700">
									INR {formData.salaryMin || '0'} - {formData.salaryMax || '0'} per year
									{#if !formData.showSalary}<span class="text-gray-500">(Hidden from candidates)</span>{/if}
								</p>
								{#if formData.benefits.length > 0}
									<div class="mt-2">
										<p class="text-sm text-gray-500 mb-1">Benefits:</p>
										<div class="flex flex-wrap gap-2">
											{#each formData.benefits as benefit}
												<span class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">{benefit}</span>
											{/each}
										</div>
									</div>
								{/if}
							</div>
						{/if}

						<!-- Skills & Requirements -->
						{#if formData.selectedSkillIds.length > 0}
							<div>
								<h3 class="font-semibold text-gray-900 mb-3">Skills</h3>
								<div class="flex flex-wrap gap-2">
									{#each formData.selectedSkillIds as skillId}
										{@const skill = data.metadata.skills.find(s => s.id === skillId)}
										{#if skill}
											<span class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded">{skill.name}</span>
										{/if}
									{/each}
								</div>
							</div>
						{/if}

						<!-- Locations -->
						{#if formData.selectedLocationIds.length > 0}
							<div>
								<h3 class="font-semibold text-gray-900 mb-3">Locations</h3>
								<div class="flex flex-wrap gap-2">
									{#each formData.selectedLocationIds as cityId}
										{@const city = data.metadata.cities.find(c => c.id === cityId)}
										{#if city}
											<span class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded">{city.name}, {city.state?.name}</span>
										{/if}
									{/each}
								</div>
							</div>
						{/if}

						<!-- Application Method -->
						<div>
							<h3 class="font-semibold text-gray-900 mb-3">Application Method</h3>
							<p class="text-sm text-gray-700 capitalize">{formData.applicationMethod}</p>
							{#if formData.applicationMethod === 'external' && formData.applicationUrl}
								<p class="text-sm text-blue-600 mt-1">{formData.applicationUrl}</p>
							{/if}
						</div>
					</div>
				</div>
			{/if}
		</div>

		<!-- Hidden fields for form submission - these ensure data is sent even when inputs are not visible -->
		<!-- Step 1: Basics -->
		<input type="hidden" name="title" value={formData.jobTitle} />
		<input type="hidden" name="company_name" value={formData.companyName} />
		<input type="hidden" name="job_role" value={formData.department} />
		<input type="hidden" name="job_type" value={formData.employmentType} />
		<input type="hidden" name="seniority_level" value={formData.seniorityLevel} />
		<input type="hidden" name="vacancies" value={formData.positions} />

		<!-- Step 2: Location -->
		<input type="hidden" name="work_mode" value={formData.workMode} />
		<input type="hidden" name="company_address" value={formData.officeAddress} />
		{#each formData.selectedLocationIds as cityId}
			<input type="hidden" name="location_ids" value={cityId} />
		{/each}

		<!-- Step 3: Details -->
		<input type="hidden" name="description" value={formData.description} />
		{#each formData.selectedSkillIds as skillId}
			<input type="hidden" name="skill_ids" value={skillId} />
		{/each}
		{#each formData.selectedIndustryIds as industryId}
			<input type="hidden" name="industry_ids" value={industryId} />
		{/each}
		{#each formData.selectedQualificationIds as qualId}
			<input type="hidden" name="qualification_ids" value={qualId} />
		{/each}
		<input type="hidden" name="required_certifications" value={formData.requiredCertifications} />
		<input type="hidden" name="preferred_certifications" value={formData.preferredCertifications} />

		<!-- Step 4: Compensation -->
		<input type="hidden" name="min_salary" value={formData.salaryMin} />
		<input type="hidden" name="max_salary" value={formData.salaryMax} />
		<input type="hidden" name="salary_type" value={formData.salaryType} />
		<input type="hidden" name="show_salary" value={formData.showSalary} />

		<!-- Step 5: Application -->
		<input type="hidden" name="application_method" value={formData.applicationMethod} />
		<input type="hidden" name="application_url" value={formData.applicationUrl} />

		<!-- Step 6: Settings -->
		<input type="hidden" name="relocation_required" value={formData.relocationRequired} />
		<input type="hidden" name="travel_percentage" value={formData.travelPercentage} />
		<input type="hidden" name="hiring_timeline" value={formData.hiringTimeline} />
		<input type="hidden" name="hiring_priority" value={formData.hiringPriority} />

		<!-- Experience fields (computed from experience level) -->
		<input type="hidden" name="min_year" value={formData.minYear} />
		<input type="hidden" name="max_year" value={formData.maxYear} />
		<input type="hidden" name="min_month" value={formData.minMonth} />
		<input type="hidden" name="max_month" value={formData.maxMonth} />
		<input type="hidden" name="fresher" value={formData.fresher} />

		<!-- Language requirements as JSON -->
		{#if formData.languages.length > 0}
			<input type="hidden" name="language_requirements" value={JSON.stringify(formData.languages)} />
		{/if}

		<!-- Benefits as comma-separated -->
		{#if formData.benefits.length > 0}
			<input type="hidden" name="benefits" value={formData.benefits.join(',')} />
		{/if}

		<!-- Navigation Buttons -->
		<div class="flex items-center justify-between mt-6">
			<div class="flex gap-3">
				<button
					type="button"
					onclick={prevStep}
					disabled={currentStep === 1}
					class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
				>
					<ChevronLeft class="w-4 h-4" />
					Previous
				</button>

				{#if currentStep < totalSteps}
					<button
						type="submit"
						onclick={() => (currentAction = 'saveDraft')}
						disabled={isSubmitting}
						class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 flex items-center gap-2"
					>
						<Save class="w-4 h-4" />
						{isSubmitting && currentAction === 'saveDraft' ? 'Saving...' : 'Save Draft'}
					</button>
				{/if}
			</div>

			{#if currentStep < totalSteps}
				<button
					type="button"
					onclick={nextStep}
					class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
				>
					Next
					<ChevronRight class="w-4 h-4" />
				</button>
			{:else}
				<div class="flex gap-3">
					<button
						type="submit"
						onclick={() => (currentAction = 'saveDraft')}
						disabled={isSubmitting}
						class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 flex items-center gap-2"
					>
						<Save class="w-4 h-4" />
						{isSubmitting && currentAction === 'saveDraft' ? 'Saving...' : 'Save as Draft'}
					</button>
					<button
						type="submit"
						onclick={() => (currentAction = 'publish')}
						disabled={isSubmitting}
						class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
					>
						<Send class="w-4 h-4" />
						{isSubmitting && currentAction === 'publish' ? 'Publishing...' : 'Publish Job'}
					</button>
				</div>
			{/if}
		</div>
	</form>
</div>

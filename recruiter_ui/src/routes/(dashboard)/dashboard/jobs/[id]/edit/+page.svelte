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
		workMode: data.job.work_mode || 'in-office',
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
		selectedFunctionalAreaIds: data.job.functional_areas?.map(fa => fa.id) || [],

		// Step 4: Compensation
		salaryMin: data.job.min_salary?.toString() || '',
		salaryMax: data.job.max_salary?.toString() || '',
		hideSalary: false,
		benefits: '',
		perks: '',

		// Step 5: Application Settings
		deadline: data.job.last_date || '',
		assignedRecruiters: [] as string[],
		screeningQuestions: [] as { question: string; required: boolean }[],
		requiredDocuments: {
			resume: true,
			coverLetter: false,
			portfolio: false
		},
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
	const workModes = [
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

	function addScreeningQuestion() {
		formData.screeningQuestions = [
			...formData.screeningQuestions,
			{ question: '', required: false }
		];
	}

	function removeScreeningQuestion(index: number) {
		formData.screeningQuestions = formData.screeningQuestions.filter((_, i) => i !== index);
	}

	// Handle form action results
	$effect(() => {
		if (form?.success && form?.jobId) {
			// Redirect to jobs list
			goto(`/dashboard/jobs/`);
		}
	});
</script>

<svelte:head>
	<title>Edit Job - {data.job.title} - PeelJobs Recruiter</title>
</svelte:head>

<div class="max-w-5xl mx-auto space-y-6">
	<!-- Header -->
	<div>
		<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Edit Job</h1>
		<p class="text-gray-600 mt-1">Update details for: {data.job.title}</p>
		<div class="mt-2 inline-flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-200 rounded-lg text-sm">
			<span class="font-medium text-blue-800">Status:</span>
			<span class="text-blue-600">{data.job.status}</span>
		</div>
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
		{#each formData.selectedFunctionalAreaIds as functionalAreaId}
			<input type="hidden" name="functional_area_ids" value={functionalAreaId} />
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
		{#if formData.deadline}
			<input type="hidden" name="last_date" bind:value={formData.deadline} />
		{/if}

		<!-- Additional fields -->
		<input type="hidden" name="company_address" bind:value={formData.officeAddress} />
		<input type="hidden" name="company_description" bind:value={formData.benefits} />

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
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Job Title <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							name="title"
							bind:value={formData.jobTitle}
							placeholder="e.g., Senior Frontend Developer"
							required
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Company Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							name="company_name"
							bind:value={formData.companyName}
							placeholder="e.g., Acme Inc."
							required
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Department <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							name="job_role"
							bind:value={formData.department}
							placeholder="e.g., Engineering"
							required
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Employment Type <span class="text-red-500">*</span>
						</label>
						<select
							name="job_type"
							bind:value={formData.employmentType}
							required
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						>
							{#each employmentTypes as type}
								<option value={type.toLowerCase()}>{type}</option>
							{/each}
						</select>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Experience Level <span class="text-red-500">*</span>
						</label>
						<select
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
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Number of Positions <span class="text-red-500">*</span>
						</label>
						<input
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

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Work Mode <span class="text-red-500">*</span>
					</label>
					<div class="grid grid-cols-3 gap-3">
						{#each workModes as mode}
							<button
								type="button"
								onclick={() => (formData.workMode = mode.value)}
								class="px-4 py-3 rounded-lg border-2 font-medium text-sm transition-colors {formData.workMode ===
								mode.value
									? 'border-blue-600 bg-blue-50 text-blue-600'
									: 'border-gray-300 text-gray-700 hover:border-gray-400'}"
							>
								{mode.label}
							</button>
						{/each}
					</div>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-3">Current Locations</label>
					{#if data.job.locations && data.job.locations.length > 0}
						<div class="flex flex-wrap gap-2 mb-3">
							{#each data.job.locations as location}
								<span class="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
									{location.name}, {location.state}
								</span>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-gray-500 mb-3">No locations set</p>
					{/if}
					<p class="text-xs text-gray-500">Note: Location editing coming soon. Please contact support to change locations.</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Country</label>
						<input
							type="text"
							bind:value={formData.country}
							placeholder="e.g., United States"
							disabled
							class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">State</label>
						<input
							type="text"
							bind:value={formData.state}
							placeholder="e.g., California"
							disabled
							class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">City</label>
						<input
							type="text"
							bind:value={formData.city}
							placeholder="e.g., San Francisco"
							disabled
							class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
						/>
					</div>
				</div>

				{#if formData.workMode !== 'remote'}
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Office Address</label>
						<textarea
							bind:value={formData.officeAddress}
							rows="3"
							placeholder="Enter the full office address"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						></textarea>
					</div>
				{/if}
			</div>
		{:else if currentStep === 3}
			<!-- Step 3: Job Details -->
			<div class="space-y-6">
				<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
					<FileText class="w-6 h-6" />
					Job Details
				</h2>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Job Description <span class="text-red-500">*</span>
					</label>
					<textarea
						name="description"
						bind:value={formData.description}
						rows="6"
						placeholder="Describe the role and what the candidate will be doing..."
						required
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					></textarea>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">Responsibilities</label>
					<textarea
						bind:value={formData.responsibilities}
						rows="5"
						placeholder="List the key responsibilities (one per line)"
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					></textarea>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Requirements <span class="text-red-500">*</span>
					</label>
					<textarea
						bind:value={formData.requirements}
						rows="5"
						placeholder="List the requirements and qualifications (one per line)"
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					></textarea>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-3">Current Skills</label>
					{#if data.job.skills && data.job.skills.length > 0}
						<div class="flex flex-wrap gap-2 mb-3">
							{#each data.job.skills as skill}
								<span class="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
									{skill.name}
								</span>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-gray-500 mb-3">No skills set</p>
					{/if}
					<p class="text-xs text-gray-500">Note: Skill editing coming soon. Please contact support to change skills.</p>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">Education Requirements</label>
					<input
						type="text"
						bind:value={formData.education}
						placeholder="e.g., Bachelor's degree in Computer Science or related field"
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
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
						<label class="block text-sm font-medium text-gray-700 mb-2">Minimum Salary</label>
						<input
							type="number"
							bind:value={formData.salaryMin}
							placeholder="50000"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Maximum Salary</label>
						<input
							type="number"
							bind:value={formData.salaryMax}
							placeholder="80000"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				<div>
					<label class="flex items-center gap-2 cursor-pointer">
						<input type="checkbox" bind:checked={formData.hideSalary} class="w-4 h-4 text-blue-600 rounded" />
						<span class="text-sm text-gray-700">Hide salary range from public job posting</span>
					</label>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">Benefits</label>
					<textarea
						bind:value={formData.benefits}
						rows="4"
						placeholder="List the benefits (e.g., Health insurance, 401k, etc.)"
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					></textarea>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">Perks</label>
					<textarea
						bind:value={formData.perks}
						rows="4"
						placeholder="List additional perks (e.g., Flexible hours, Remote work, etc.)"
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					></textarea>
				</div>
			</div>
		{:else if currentStep === 5}
			<!-- Step 5: Application Settings -->
			<div class="space-y-6">
				<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
					<Settings class="w-6 h-6" />
					Application Settings
				</h2>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Application Deadline <span class="text-red-500">*</span>
					</label>
					<input
						type="date"
						name="last_date"
						bind:value={formData.deadline}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-3">Required Documents</label>
					<div class="space-y-2">
						<label class="flex items-center gap-2 cursor-pointer">
							<input
								type="checkbox"
								bind:checked={formData.requiredDocuments.resume}
								class="w-4 h-4 text-blue-600 rounded"
							/>
							<span class="text-sm text-gray-700">Resume/CV</span>
						</label>
						<label class="flex items-center gap-2 cursor-pointer">
							<input
								type="checkbox"
								bind:checked={formData.requiredDocuments.coverLetter}
								class="w-4 h-4 text-blue-600 rounded"
							/>
							<span class="text-sm text-gray-700">Cover Letter</span>
						</label>
						<label class="flex items-center gap-2 cursor-pointer">
							<input
								type="checkbox"
								bind:checked={formData.requiredDocuments.portfolio}
								class="w-4 h-4 text-blue-600 rounded"
							/>
							<span class="text-sm text-gray-700">Portfolio/Work Samples</span>
						</label>
					</div>
				</div>

				<div>
					<div class="flex items-center justify-between mb-3">
						<label class="block text-sm font-medium text-gray-700">Screening Questions (Optional)</label>
						<button
							type="button"
							onclick={addScreeningQuestion}
							class="text-sm text-blue-600 hover:text-blue-700 font-medium"
						>
							+ Add Question
						</button>
					</div>
					{#if formData.screeningQuestions.length > 0}
						<div class="space-y-3">
							{#each formData.screeningQuestions as question, index}
								<div class="flex gap-3">
									<input
										type="text"
										bind:value={question.question}
										placeholder="Enter your screening question"
										class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									/>
									<label class="flex items-center gap-2 cursor-pointer whitespace-nowrap">
										<input type="checkbox" bind:checked={question.required} class="w-4 h-4 text-blue-600 rounded" />
										<span class="text-sm text-gray-700">Required</span>
									</label>
									<button
										type="button"
										onclick={() => removeScreeningQuestion(index)}
										class="p-2 text-red-600 hover:bg-red-50 rounded-lg"
									>
										<X class="w-5 h-5" />
									</button>
								</div>
							{/each}
						</div>
					{/if}
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">Auto-Reply Email Template</label>
					<textarea
						bind:value={formData.autoReplyTemplate}
						rows="4"
						placeholder="Thank you for applying! We have received your application and will review it shortly..."
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					></textarea>
				</div>
			</div>
		{:else if currentStep === 6}
			<!-- Step 6: Preview -->
			<div class="space-y-6">
				<h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
					<Eye class="w-6 h-6" />
					Preview & Update
				</h2>

				<div class="bg-gray-50 rounded-lg p-6 space-y-4">
					<div>
						<h3 class="text-2xl font-bold text-gray-900">{formData.jobTitle || 'Job Title'}</h3>
						<div class="flex flex-wrap gap-3 mt-2 text-sm text-gray-600">
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
							<h4 class="font-semibold text-gray-900 mb-2">Description</h4>
							<p class="text-gray-700 whitespace-pre-line">{formData.description}</p>
						</div>
					{/if}

					{#if formData.responsibilities}
						<div>
							<h4 class="font-semibold text-gray-900 mb-2">Responsibilities</h4>
							<p class="text-gray-700 whitespace-pre-line">{formData.responsibilities}</p>
						</div>
					{/if}

					{#if formData.requirements}
						<div>
							<h4 class="font-semibold text-gray-900 mb-2">Requirements</h4>
							<p class="text-gray-700 whitespace-pre-line">{formData.requirements}</p>
						</div>
					{/if}

					{#if data.job.skills && data.job.skills.length > 0}
						<div>
							<h4 class="font-semibold text-gray-900 mb-2">Required Skills</h4>
							<div class="flex flex-wrap gap-2">
								{#each data.job.skills as skill}
									<span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">{skill.name}</span>
								{/each}
							</div>
						</div>
					{/if}

					{#if formData.salaryMin || formData.salaryMax}
						{#if !formData.hideSalary}
							<div>
								<h4 class="font-semibold text-gray-900 mb-2">Salary Range</h4>
								<p class="text-gray-700">
									${formData.salaryMin || '0'} - ${formData.salaryMax || '0'}
								</p>
							</div>
						{/if}
					{/if}
				</div>

				<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
					<p class="text-sm text-blue-800">
						<strong>Note:</strong> Changes will be saved to this job posting. If you publish, it will be visible to job seekers.
					</p>
				</div>
			</div>
		{/if}
	</div>

		<!-- Navigation Buttons -->
		<div class="flex items-center justify-between bg-white rounded-lg border border-gray-200 p-4">
			<button
				type="button"
				onclick={prevStep}
				disabled={currentStep === 1}
				class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
			>
				<ChevronLeft class="w-4 h-4" />
				Previous
			</button>

			<div class="flex items-center gap-3">
				<button
					type="submit"
					formaction="?/saveDraft"
					disabled={isSubmitting}
					class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
				>
					<Save class="w-4 h-4" />
					{isSubmitting ? 'Saving...' : 'Save Changes'}
				</button>

				{#if currentStep < totalSteps}
					<button
						type="button"
						onclick={nextStep}
						class="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
					>
						Next
						<ChevronRight class="w-4 h-4" />
					</button>
				{:else}
					<button
						type="submit"
						formaction="?/publish"
						disabled={isSubmitting}
						class="inline-flex items-center gap-2 px-6 py-2 bg-green-600 rounded-lg text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
					>
						<Send class="w-4 h-4" />
						{isSubmitting ? 'Publishing...' : data.job.status === 'Live' ? 'Update & Republish' : 'Update & Publish'}
					</button>
				{/if}
			</div>
		</div>
	</form>
</div>

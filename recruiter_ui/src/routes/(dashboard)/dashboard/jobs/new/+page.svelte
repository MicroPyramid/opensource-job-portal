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
		X
	} from '@lucide/svelte';

	let currentStep = $state(1);
	const totalSteps = 6;

	// Form data
	let formData = $state({
		// Step 1: Basics
		jobTitle: '',
		department: '',
		employmentType: 'Full-time',
		experienceLevel: '',
		positions: 1,

		// Step 2: Location
		country: '',
		state: '',
		city: '',
		workMode: 'On-site',
		officeAddress: '',

		// Step 3: Details
		description: '',
		responsibilities: '',
		requirements: '',
		skills: [] as string[],
		education: '',

		// Step 4: Compensation
		salaryMin: '',
		salaryMax: '',
		hideSalary: false,
		benefits: '',
		perks: '',

		// Step 5: Application Settings
		deadline: '',
		assignedRecruiters: [] as string[],
		screeningQuestions: [] as { question: string; required: boolean }[],
		requiredDocuments: {
			resume: true,
			coverLetter: false,
			portfolio: false
		},
		autoReplyTemplate: ''
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
	const workModes = ['On-site', 'Remote', 'Hybrid'];

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

	function saveAsDraft() {
		console.log('Saving as draft...', formData);
		// API call here
	}

	function publishJob() {
		console.log('Publishing job...', formData);
		// API call here
	}
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

	<!-- Progress Steps -->
	<div class="bg-white rounded-lg border border-gray-200 p-6">
		<div class="flex items-center justify-between">
			{#each steps as step, index}
				<div class="flex items-center {index < steps.length - 1 ? 'flex-1' : ''}">
					<div class="flex flex-col items-center">
						<button
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
							bind:value={formData.jobTitle}
							placeholder="e.g., Senior Frontend Developer"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Department <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.department}
							placeholder="e.g., Engineering"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Employment Type <span class="text-red-500">*</span>
						</label>
						<select
							bind:value={formData.employmentType}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						>
							{#each employmentTypes as type}
								<option value={type}>{type}</option>
							{/each}
						</select>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Experience Level <span class="text-red-500">*</span>
						</label>
						<select
							bind:value={formData.experienceLevel}
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
							bind:value={formData.positions}
							min="1"
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
								onclick={() => (formData.workMode = mode)}
								class="px-4 py-3 rounded-lg border-2 font-medium text-sm transition-colors {formData.workMode ===
								mode
									? 'border-blue-600 bg-blue-50 text-blue-600'
									: 'border-gray-300 text-gray-700 hover:border-gray-400'}"
							>
								{mode}
							</button>
						{/each}
					</div>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Country <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.country}
							placeholder="e.g., United States"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							State <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.state}
							placeholder="e.g., California"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							City <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.city}
							placeholder="e.g., San Francisco"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				{#if formData.workMode !== 'Remote'}
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
						bind:value={formData.description}
						rows="6"
						placeholder="Describe the role and what the candidate will be doing..."
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
					<label class="block text-sm font-medium text-gray-700 mb-2">Skills</label>
					<div class="flex gap-2 mb-3">
						<input
							type="text"
							bind:value={newSkill}
							placeholder="Add a skill (e.g., React, Python)"
							onkeydown={(e) => {
								if (e.key === 'Enter') {
									e.preventDefault();
									addSkill();
								}
							}}
							class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
						<button
							onclick={addSkill}
							class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
						>
							Add
						</button>
					</div>
					{#if formData.skills.length > 0}
						<div class="flex flex-wrap gap-2">
							{#each formData.skills as skill, index}
								<span
									class="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
								>
									{skill}
									<button onclick={() => removeSkill(index)} class="hover:text-blue-900">
										<X class="w-3 h-3" />
									</button>
								</span>
							{/each}
						</div>
					{/if}
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
					Preview & Publish
				</h2>

				<div class="bg-gray-50 rounded-lg p-6 space-y-4">
					<div>
						<h3 class="text-2xl font-bold text-gray-900">{formData.jobTitle || 'Job Title'}</h3>
						<div class="flex flex-wrap gap-3 mt-2 text-sm text-gray-600">
							<span>{formData.department || 'Department'}</span>
							<span>•</span>
							<span>{formData.city}, {formData.state}</span>
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

					{#if formData.skills.length > 0}
						<div>
							<h4 class="font-semibold text-gray-900 mb-2">Required Skills</h4>
							<div class="flex flex-wrap gap-2">
								{#each formData.skills as skill}
									<span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">{skill}</span>
								{/each}
							</div>
						</div>
					{/if}

					{#if formData.salaryMin || formData.salaryMax}
						{#if !formData.hideSalary}
							<div>
								<h4 class="font-semibold text-gray-900 mb-2">Salary Range</h4>
								<p class="text-gray-700">
									${formData.salaryMin?.toLocaleString() || '0'} - ${formData.salaryMax?.toLocaleString() ||
										'0'}
								</p>
							</div>
						{/if}
					{/if}
				</div>

				<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
					<p class="text-sm text-yellow-800">
						<strong>Note:</strong> Once published, this job will be visible to all job seekers on the platform.
						You can edit or close it at any time from the Jobs page.
					</p>
				</div>
			</div>
		{/if}
	</div>

	<!-- Navigation Buttons -->
	<div class="flex items-center justify-between bg-white rounded-lg border border-gray-200 p-4">
		<button
			onclick={prevStep}
			disabled={currentStep === 1}
			class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
		>
			<ChevronLeft class="w-4 h-4" />
			Previous
		</button>

		<div class="flex items-center gap-3">
			<button
				onclick={saveAsDraft}
				class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
			>
				<Save class="w-4 h-4" />
				Save Draft
			</button>

			{#if currentStep < totalSteps}
				<button
					onclick={nextStep}
					class="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
				>
					Next
					<ChevronRight class="w-4 h-4" />
				</button>
			{:else}
				<button
					onclick={publishJob}
					class="inline-flex items-center gap-2 px-6 py-2 bg-green-600 rounded-lg text-sm font-medium text-white hover:bg-green-700 transition-colors"
				>
					<Send class="w-4 h-4" />
					Publish Job
				</button>
			{/if}
		</div>
	</div>
</div>

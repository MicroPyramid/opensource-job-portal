<script lang="ts">
	import {
		Building2,
		Upload,
		MapPin,
		Users,
		CheckCircle2,
		ChevronRight,
		ChevronLeft
	} from '@lucide/svelte';

	let currentStep = $state(1);
	const totalSteps = 3;

	// Form data
	let formData = $state({
		// Step 1: Company Details
		logo: null as string | null,
		about: '',
		headquarters: '',
		website: '',
		foundedYear: '',

		// Step 2: Team Setup
		teamSize: 1,
		inviteEmails: [''] as string[],

		// Step 3: Preferences
		jobCategories: [] as string[],
		hiringGoals: '',
		monthlyHires: ''
	});

	const jobCategoryOptions = [
		'Engineering',
		'Product',
		'Design',
		'Marketing',
		'Sales',
		'Customer Success',
		'Operations',
		'Finance',
		'HR',
		'Other'
	];

	function nextStep() {
		if (currentStep < totalSteps) currentStep++;
	}

	function prevStep() {
		if (currentStep > 1) currentStep--;
	}

	function handleLogoUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (file) {
			const reader = new FileReader();
			reader.onload = (e) => {
				formData.logo = e.target?.result as string;
			};
			reader.readAsDataURL(file);
		}
	}

	function addEmailField() {
		formData.inviteEmails = [...formData.inviteEmails, ''];
	}

	function removeEmailField(index: number) {
		formData.inviteEmails = formData.inviteEmails.filter((_, i) => i !== index);
	}

	function toggleCategory(category: string) {
		if (formData.jobCategories.includes(category)) {
			formData.jobCategories = formData.jobCategories.filter((c) => c !== category);
		} else {
			formData.jobCategories = [...formData.jobCategories, category];
		}
	}

	function completeOnboarding() {
		console.log('Completing onboarding...', formData);
		// API call here
		window.location.href = '/dashboard/';
	}

	function skipOnboarding() {
		window.location.href = '/dashboard/';
	}
</script>

<svelte:head>
	<title>Welcome - Setup Your Account</title>
</svelte:head>

<div class="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
	<!-- Header -->
	<div class="text-center mb-8">
		<h1 class="text-2xl font-bold text-gray-900">Welcome to PeelJobs!</h1>
		<p class="text-gray-600 mt-2">Let's set up your employer account in just a few steps</p>
	</div>

	<!-- Progress Bar -->
	<div class="mb-8">
		<div class="flex items-center justify-between mb-2">
			<span class="text-sm font-medium text-gray-700">Step {currentStep} of {totalSteps}</span>
			<span class="text-sm text-gray-500">{Math.round((currentStep / totalSteps) * 100)}% complete</span>
		</div>
		<div class="w-full bg-gray-200 rounded-full h-2">
			<div
				class="bg-blue-600 h-2 rounded-full transition-all"
				style="width: {(currentStep / totalSteps) * 100}%"
			></div>
		</div>
	</div>

	<!-- Form Content -->
	<form onsubmit={(e) => { e.preventDefault(); if (currentStep === totalSteps) completeOnboarding(); else nextStep(); }}>
		{#if currentStep === 1}
			<!-- Step 1: Company Details -->
			<div class="space-y-6">
				<h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
					<Building2 class="w-5 h-5" />
					Complete Your Company Profile
				</h2>

				<!-- Logo Upload -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-3">Company Logo</label>
					<div class="flex items-center gap-6">
						<div
							class="w-24 h-24 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center bg-gray-50 overflow-hidden"
						>
							{#if formData.logo}
								<img src={formData.logo} alt="Company Logo" class="w-full h-full object-cover" />
							{:else}
								<Building2 class="w-10 h-10 text-gray-400" />
							{/if}
						</div>
						<div class="flex-1">
							<label
								class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors cursor-pointer"
							>
								<Upload class="w-4 h-4" />
								Upload Logo
								<input type="file" accept="image/*" onchange={handleLogoUpload} class="hidden" />
							</label>
							<p class="text-xs text-gray-500 mt-2">PNG, JPG up to 2MB</p>
						</div>
					</div>
				</div>

				<!-- About Company -->
				<div>
					<label for="about" class="block text-sm font-medium text-gray-700 mb-2">
						About Your Company
					</label>
					<textarea
						id="about"
						bind:value={formData.about}
						rows="4"
						placeholder="Tell candidates about your company, culture, and mission..."
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					></textarea>
				</div>

				<!-- Additional Info -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label for="headquarters" class="block text-sm font-medium text-gray-700 mb-2">
							Headquarters
						</label>
						<div class="relative">
							<MapPin class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
							<input
								type="text"
								id="headquarters"
								bind:value={formData.headquarters}
								placeholder="San Francisco, CA"
								class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>
					</div>

					<div>
						<label for="foundedYear" class="block text-sm font-medium text-gray-700 mb-2">
							Founded Year
						</label>
						<input
							type="text"
							id="foundedYear"
							bind:value={formData.foundedYear}
							placeholder="2015"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>
			</div>
		{:else if currentStep === 2}
			<!-- Step 2: Team Setup -->
			<div class="space-y-6">
				<h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
					<Users class="w-5 h-5" />
					Invite Your Team
				</h2>

				<p class="text-sm text-gray-600">
					Collaborate with your team by inviting recruiters and hiring managers. You can skip this and add them later.
				</p>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-3">Team Members</label>
					<div class="space-y-3">
						{#each formData.inviteEmails as email, index}
							<div class="flex gap-2">
								<input
									type="email"
									bind:value={formData.inviteEmails[index]}
									placeholder="teammate@company.com"
									class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								/>
								{#if formData.inviteEmails.length > 1}
									<button
										type="button"
										onclick={() => removeEmailField(index)}
										class="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
									>
										Remove
									</button>
								{/if}
							</div>
						{/each}
					</div>

					<button
						type="button"
						onclick={addEmailField}
						class="mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
					>
						+ Add another team member
					</button>
				</div>

				<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
					<p class="text-sm text-blue-800">
						<strong>Tip:</strong> Invited team members will receive an email to join your company account
						and can help manage jobs and applicants.
					</p>
				</div>
			</div>
		{:else}
			<!-- Step 3: Hiring Preferences -->
			<div class="space-y-6">
				<h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
					<CheckCircle2 class="w-5 h-5" />
					Tell Us About Your Hiring Needs
				</h2>

				<!-- Job Categories -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-3">
						Which roles are you hiring for?
					</label>
					<div class="grid grid-cols-2 gap-3">
						{#each jobCategoryOptions as category}
							<button
								type="button"
								onclick={() => toggleCategory(category)}
								class="px-4 py-3 rounded-lg border-2 text-sm font-medium transition-colors {formData.jobCategories.includes(
									category
								)
									? 'border-blue-600 bg-blue-50 text-blue-600'
									: 'border-gray-300 text-gray-700 hover:border-gray-400'}"
							>
								{category}
							</button>
						{/each}
					</div>
				</div>

				<!-- Hiring Goals -->
				<div>
					<label for="hiringGoals" class="block text-sm font-medium text-gray-700 mb-2">
						What are your hiring goals?
					</label>
					<select
						id="hiringGoals"
						bind:value={formData.hiringGoals}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					>
						<option value="">Select your goal</option>
						<option value="growth">Growing the team</option>
						<option value="replacement">Replacing departed employees</option>
						<option value="expansion">Opening new positions</option>
						<option value="seasonal">Seasonal hiring</option>
						<option value="other">Other</option>
					</select>
				</div>

				<!-- Monthly Hires -->
				<div>
					<label for="monthlyHires" class="block text-sm font-medium text-gray-700 mb-2">
						How many people do you plan to hire per month?
					</label>
					<select
						id="monthlyHires"
						bind:value={formData.monthlyHires}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					>
						<option value="">Select range</option>
						<option value="1-5">1-5 people</option>
						<option value="6-10">6-10 people</option>
						<option value="11-20">11-20 people</option>
						<option value="20+">20+ people</option>
					</select>
				</div>
			</div>
		{/if}

		<!-- Navigation -->
		<div class="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
			<div>
				{#if currentStep > 1}
					<button
						type="button"
						onclick={prevStep}
						class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
					>
						<ChevronLeft class="w-4 h-4" />
						Back
					</button>
				{:else}
					<button
						type="button"
						onclick={skipOnboarding}
						class="text-sm text-gray-600 hover:text-gray-900"
					>
						Skip for now
					</button>
				{/if}
			</div>

			{#if currentStep < totalSteps}
				<button
					type="submit"
					class="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
				>
					Continue
					<ChevronRight class="w-4 h-4" />
				</button>
			{:else}
				<button
					type="submit"
					class="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
				>
					Complete Setup
					<CheckCircle2 class="w-4 h-4" />
				</button>
			{/if}
		</div>
	</form>
</div>

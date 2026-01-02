<script lang="ts">
	import {
		Building2,
		Upload,
		MapPin,
		Users,
		CheckCircle,
		ChevronRight,
		ChevronLeft,
		Target
	} from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';
	import { Button, Card, Input, FormField } from '$lib/components/ui';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	let { form } = $props();

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-3xl';

	let currentStep = $state(1);
	const totalSteps = 3;
	let loading = $state(false);

	let error = $derived(form?.error || '');

	async function handleSkip() {
		const response = await fetch('?/skip', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			}
		});
		if (response.redirected) {
			goto(response.url);
		}
	}

	let formData = $state({
		logo: null as string | null,
		about: '',
		headquarters: '',
		website: '',
		foundedYear: '',
		teamSize: 1,
		inviteEmails: [''] as string[],
		jobCategories: [] as string[],
		hiringGoals: '',
		monthlyHires: ''
	});

	const jobCategoryOptions = [
		'Engineering', 'Product', 'Design', 'Marketing', 'Sales',
		'Customer Success', 'Operations', 'Finance', 'HR', 'Other'
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
</script>

<svelte:head>
	<title>Welcome - Setup Your Account</title>
	<meta name="description" content="Complete your PeelJobs employer profile setup." />
</svelte:head>

<Card padding="lg" class="shadow-lg max-w-2xl mx-auto">
	<!-- Header -->
	<div class="text-center mb-8">
		<h1 class="text-2xl font-semibold text-black">Welcome to PeelJobs!</h1>
		<p class="text-muted mt-2">Let's set up your employer account in just a few steps</p>
	</div>

	<!-- Progress Bar -->
	<div class="mb-8">
		<div class="flex items-center justify-between mb-2">
			<span class="text-sm font-medium text-black">Step {currentStep} of {totalSteps}</span>
			<span class="text-sm text-muted">{Math.round((currentStep / totalSteps) * 100)}% complete</span>
		</div>
		<div class="w-full bg-surface rounded-full h-2">
			<div
				class="bg-primary h-2 rounded-full transition-all"
				style="width: {(currentStep / totalSteps) * 100}%"
			></div>
		</div>
	</div>

	<!-- Form Content -->
	<form method="POST" action="?/complete" use:enhance={({ cancel }) => {
		if (currentStep !== totalSteps) {
			cancel();
			nextStep();
			return;
		}
		loading = true;
		return async ({ update }) => {
			loading = false;
			await update();
		};
	}}>
		<!-- Hidden fields for all form data -->
		<input type="hidden" name="about" value={formData.about} />
		<input type="hidden" name="headquarters" value={formData.headquarters} />
		<input type="hidden" name="founded_year" value={formData.foundedYear} />
		<input type="hidden" name="invite_emails" value={formData.inviteEmails.filter(e => e).join(',')} />
		<input type="hidden" name="job_categories" value={formData.jobCategories.join(',')} />
		<input type="hidden" name="hiring_goals" value={formData.hiringGoals} />
		<input type="hidden" name="monthly_hires" value={formData.monthlyHires} />

		{#if error}
			<div class="bg-error-light border border-error/20 text-error px-4 py-3 rounded-lg text-sm mb-4">
				{error}
			</div>
		{/if}

		{#if currentStep === 1}
			<!-- Step 1: Company Details -->
			<div class="space-y-6">
				<h2 class="text-lg font-semibold text-black flex items-center gap-2">
					<Building2 class="w-5 h-5 text-primary" />
					Complete Your Company Profile
				</h2>

				<!-- Logo Upload -->
				<div>
					<label for="company-logo-upload" class="block text-sm font-medium text-black mb-3">Company Logo</label>
					<div class="flex items-center gap-6">
						<div class="w-24 h-24 rounded-lg border-2 border-dashed border-border flex items-center justify-center bg-surface overflow-hidden">
							{#if formData.logo}
								<img src={formData.logo} alt="Company Logo" class="w-full h-full object-cover" />
							{:else}
								<Building2 class="w-10 h-10 text-muted" />
							{/if}
						</div>
						<div class="flex-1">
							<label
								for="company-logo-upload"
								class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-border rounded-lg text-sm font-medium text-black hover:bg-surface transition-colors cursor-pointer"
							>
								<Upload class="w-4 h-4" />
								Upload Logo
								<input id="company-logo-upload" type="file" accept="image/*" onchange={handleLogoUpload} class="hidden" />
							</label>
							<p class="text-xs text-muted mt-2">PNG, JPG up to 2MB</p>
						</div>
					</div>
				</div>

				<!-- About Company -->
				<FormField label="About Your Company">
					<textarea
						id="about"
						bind:value={formData.about}
						rows={4}
						placeholder="Tell candidates about your company, culture, and mission..."
						class="w-full px-4 py-3 border border-border rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none"
					></textarea>
				</FormField>

				<!-- Additional Info -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<FormField label="Headquarters">
						<Input
							type="text"
							id="headquarters"
							bind:value={formData.headquarters}
							placeholder="San Francisco, CA"
							size="lg"
						>
							{#snippet iconLeft()}
								<MapPin class="w-4 h-4" />
							{/snippet}
						</Input>
					</FormField>

					<FormField label="Founded Year">
						<Input
							type="text"
							id="foundedYear"
							bind:value={formData.foundedYear}
							placeholder="2015"
							size="lg"
						/>
					</FormField>
				</div>
			</div>
		{:else if currentStep === 2}
			<!-- Step 2: Team Setup -->
			<div class="space-y-6">
				<h2 class="text-lg font-semibold text-black flex items-center gap-2">
					<Users class="w-5 h-5 text-primary" />
					Invite Your Team
				</h2>

				<p class="text-sm text-muted">
					Collaborate with your team by inviting recruiters and hiring managers. You can skip this and add them later.
				</p>

				<div>
					<label for="team-member-0" class="block text-sm font-medium text-black mb-3">Team Members</label>
					<div class="space-y-3">
						{#each formData.inviteEmails as email, index}
							<div class="flex gap-2">
								<Input
									id="team-member-{index}"
									type="email"
									bind:value={formData.inviteEmails[index]}
									placeholder="teammate@company.com"
									size="lg"
									class="flex-1"
								/>
								{#if formData.inviteEmails.length > 1}
									<Button type="button" variant="ghost" onclick={() => removeEmailField(index)} class="text-error hover:bg-error-light">
										Remove
									</Button>
								{/if}
							</div>
						{/each}
					</div>

					<button
						type="button"
						onclick={addEmailField}
						class="mt-3 text-sm text-primary hover:text-primary-hover font-medium transition-colors"
					>
						+ Add another team member
					</button>
				</div>

				<div class="bg-primary/5 border border-primary/20 rounded-lg p-4">
					<p class="text-sm text-primary">
						<strong>Tip:</strong> Invited team members will receive an email to join your company account
						and can help manage jobs and applicants.
					</p>
				</div>
			</div>
		{:else}
			<!-- Step 3: Hiring Preferences -->
			<div class="space-y-6">
				<h2 class="text-lg font-semibold text-black flex items-center gap-2">
					<Target class="w-5 h-5 text-primary" />
					Tell Us About Your Hiring Needs
				</h2>

				<!-- Job Categories -->
				<div>
					<label for="job-categories" class="block text-sm font-medium text-black mb-3">
						Which roles are you hiring for?
					</label>
					<div class="grid grid-cols-2 gap-3">
						{#each jobCategoryOptions as category}
							<button
								type="button"
								onclick={() => toggleCategory(category)}
								class="px-4 py-3 rounded-lg border-2 text-sm font-medium transition-colors {formData.jobCategories.includes(category)
									? 'border-primary bg-primary/5 text-primary'
									: 'border-border text-muted hover:border-primary/50'}"
							>
								{category}
							</button>
						{/each}
					</div>
				</div>

				<!-- Hiring Goals -->
				<FormField label="What are your hiring goals?">
					<select
						id="hiringGoals"
						bind:value={formData.hiringGoals}
						class="w-full h-12 px-4 text-base border border-border rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none"
					>
						<option value="">Select your goal</option>
						<option value="growth">Growing the team</option>
						<option value="replacement">Replacing departed employees</option>
						<option value="expansion">Opening new positions</option>
						<option value="seasonal">Seasonal hiring</option>
						<option value="other">Other</option>
					</select>
				</FormField>

				<!-- Monthly Hires -->
				<FormField label="How many people do you plan to hire per month?">
					<select
						id="monthlyHires"
						bind:value={formData.monthlyHires}
						class="w-full h-12 px-4 text-base border border-border rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none"
					>
						<option value="">Select range</option>
						<option value="1-5">1-5 people</option>
						<option value="6-10">6-10 people</option>
						<option value="11-20">11-20 people</option>
						<option value="20+">20+ people</option>
					</select>
				</FormField>
			</div>
		{/if}

		<!-- Navigation -->
		<div class="flex items-center justify-between mt-8 pt-6 border-t border-border">
			<div>
				{#if currentStep > 1}
					<Button type="button" variant="secondary" onclick={prevStep}>
						<ChevronLeft class="w-4 h-4" />
						Back
					</Button>
				{:else}
					<button
						type="button"
						onclick={handleSkip}
						class="text-sm text-muted hover:text-black transition-colors"
					>
						Skip for now
					</button>
				{/if}
			</div>

			{#if currentStep < totalSteps}
				<Button type="submit">
					Continue
					<ChevronRight class="w-4 h-4" />
				</Button>
			{:else}
				<Button type="submit" {loading} disabled={loading}>
					{#if loading}
						Saving...
					{:else}
						Complete Setup
						<CheckCircle class="w-4 h-4" />
					{/if}
				</Button>
			{/if}
		</div>
	</form>
</Card>

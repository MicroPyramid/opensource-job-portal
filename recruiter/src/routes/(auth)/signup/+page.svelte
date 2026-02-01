<script lang="ts">
	import { untrack } from 'svelte';
	import { Building2, Mail, Lock, Phone, Eye, EyeOff, UserCircle, Globe, Users, Zap, Target, UserCheck, Headphones, CheckCircle, Shield, Clock } from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { enhance } from '$app/forms';
	import { Button, Input, Card, FormField, Badge } from '$lib/components/ui';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	let { data, form } = $props();

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-6xl';
	layout.mainClass = 'flex justify-center items-start py-8 px-4 sm:px-6 lg:px-8';

	let invitationToken = $derived(data.invitationToken || '');
	let isInvitationFlow = $derived(!!invitationToken);
	let error = $derived(form?.error || '');

	let step = $state(untrack(() => invitationToken ? 1 : 0));
	let userType = $state<'recruiter' | 'company' | null>(untrack(() => invitationToken ? 'company' : null));
	let showPassword = $state(false);
	let showConfirmPassword = $state(false);
	let loading = $state(false);
	let success = $state(false);

	let formData = $state({
		accountType: '' as 'recruiter' | 'company',
		companyName: '',
		industry: '',
		companySize: '',
		website: '',
		firstName: '',
		lastName: '',
		email: '',
		phone: '',
		jobTitle: '',
		password: '',
		confirmPassword: '',
		agreeToTerms: false,
		subscribeNewsletter: true
	});

	const industries = [
		'Technology', 'Finance', 'Healthcare', 'Education', 'Retail',
		'Manufacturing', 'Consulting', 'Media', 'Real Estate', 'Other'
	];

	const companySizes = [
		'1-10 employees', '11-50 employees', '51-200 employees',
		'201-500 employees', '501-1000 employees', '1001-5000 employees', '5000+ employees'
	];

	function selectAccountType(type: 'recruiter' | 'company') {
		userType = type;
		formData.accountType = type;
		step = 1;
	}

	function nextStep() {
		if (isInvitationFlow) {
			if (step < 2) step++;
		} else if (userType === 'company') {
			if (step < 3) step++;
		} else {
			if (step < 2) step++;
		}
	}

	function prevStep() {
		if (step > 1) {
			step--;
		} else {
			step = 0;
			userType = null;
		}
	}

	const sizeMap: Record<string, string> = {
		'1-10 employees': '1-10',
		'11-50 employees': '11-20',
		'51-200 employees': '50-200',
		'201-500 employees': '200+',
		'501-1000 employees': '200+',
		'1001-5000 employees': '200+',
		'5000+ employees': '200+'
	};

	function getTotalSteps(): number {
		return userType === 'company' ? 3 : 2;
	}
</script>

<svelte:head>
	<title>Sign Up - PeelJobs Recruiter</title>
	<meta name="description" content="Create your PeelJobs employer account and start hiring top talent today." />
</svelte:head>

<div class="w-full">
	<div class="grid lg:grid-cols-2 gap-12 items-start">
		<!-- Left Column: Marketing Content -->
		<div class="space-y-8 lg:sticky lg:top-8 hidden lg:block">
			<div>
				<h1 class="text-3xl xl:text-4xl font-semibold text-black mb-4 leading-tight">
					Join 10,000+ Companies Hiring with PeelJobs
				</h1>
				<p class="text-base xl:text-lg text-muted leading-relaxed">
					Access India's largest talent pool with 100k+ active job seekers. Post unlimited jobs for free and find the perfect candidates faster.
				</p>
			</div>

			<!-- Key Statistics -->
			<div class="grid grid-cols-2 gap-4">
				<div class="bg-primary/5 border border-primary/20 rounded-lg p-5 text-center">
					<div class="text-2xl font-semibold text-primary mb-1">100k+</div>
					<p class="text-sm text-muted font-medium">Active Job Seekers</p>
				</div>
				<div class="bg-success-light border border-success/20 rounded-lg p-5 text-center">
					<div class="text-2xl font-semibold text-success mb-1">1000+</div>
					<p class="text-sm text-muted font-medium">Daily Applications</p>
				</div>
				<div class="bg-primary/5 border border-primary/20 rounded-lg p-5 text-center">
					<div class="text-2xl font-semibold text-primary mb-1">500+</div>
					<p class="text-sm text-muted font-medium">Companies Trust Us</p>
				</div>
				<div class="bg-warning-light border border-warning/20 rounded-lg p-5 text-center">
					<div class="text-2xl font-semibold text-warning mb-1">24/7</div>
					<p class="text-sm text-muted font-medium">Expert Support</p>
				</div>
			</div>

			<!-- Key Benefits -->
			<Card padding="lg" class="shadow-md">
				<h3 class="text-xl font-semibold text-black mb-6 flex items-center gap-2">
					<Target class="w-5 h-5 text-warning" />
					Why Recruiters Choose PeelJobs
				</h3>
				<div class="space-y-5">
					<div class="flex items-start gap-4">
						<div class="bg-primary/10 rounded-full p-2.5 flex-shrink-0">
							<Zap class="w-5 h-5 text-primary" />
						</div>
						<div>
							<h4 class="font-medium text-black text-sm mb-0.5">Instant Job Posting</h4>
							<p class="text-sm text-muted leading-relaxed">Post unlimited jobs for free and get applications within hours</p>
						</div>
					</div>
					<div class="flex items-start gap-4">
						<div class="bg-success-light rounded-full p-2.5 flex-shrink-0">
							<CheckCircle class="w-5 h-5 text-success" />
						</div>
						<div>
							<h4 class="font-medium text-black text-sm mb-0.5">Smart Matching</h4>
							<p class="text-sm text-muted leading-relaxed">AI-powered system matches you with the most qualified candidates</p>
						</div>
					</div>
					<div class="flex items-start gap-4">
						<div class="bg-primary/10 rounded-full p-2.5 flex-shrink-0">
							<UserCheck class="w-5 h-5 text-primary" />
						</div>
						<div>
							<h4 class="font-medium text-black text-sm mb-0.5">Quality Candidates</h4>
							<p class="text-sm text-muted leading-relaxed">Access to verified profiles with detailed skills and experience</p>
						</div>
					</div>
					<div class="flex items-start gap-4">
						<div class="bg-warning-light rounded-full p-2.5 flex-shrink-0">
							<Headphones class="w-5 h-5 text-warning" />
						</div>
						<div>
							<h4 class="font-medium text-black text-sm mb-0.5">Dedicated Support</h4>
							<p class="text-sm text-muted leading-relaxed">24/7 customer support to help optimize your hiring process</p>
						</div>
					</div>
				</div>
			</Card>
		</div>

		<!-- Right Column: Registration Form -->
		<Card padding="lg" class="shadow-lg">
			<!-- Header -->
			<div class="text-center mb-6">
				{#if isInvitationFlow}
					<Badge variant="primary" class="mb-4">
						<Users class="w-4 h-4 mr-1" />
						Team Invitation
					</Badge>
					<h2 class="text-2xl font-semibold text-black">Join Your Team</h2>
					<p class="text-muted mt-2">Complete your profile to join your company's team</p>
				{:else}
					<h2 class="text-2xl font-semibold text-black">Create Employer Account</h2>
					<p class="text-muted mt-2">Start hiring top talent today</p>
				{/if}
			</div>

			{#if step > 0}
				<!-- Progress Indicator -->
				<div class="flex items-center justify-center mb-6">
					<div class="flex items-center">
						{#if userType === 'company' && !isInvitationFlow}
							<div class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step >= 1 ? 'bg-primary text-white' : 'bg-surface text-muted'}">1</div>
							<div class="w-16 h-1 {step >= 2 ? 'bg-primary' : 'bg-surface'}"></div>
							<div class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step >= 2 ? 'bg-primary text-white' : 'bg-surface text-muted'}">2</div>
							<div class="w-16 h-1 {step >= 3 ? 'bg-primary' : 'bg-surface'}"></div>
							<div class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step === 3 ? 'bg-primary text-white' : 'bg-surface text-muted'}">3</div>
						{:else}
							<div class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step >= 1 ? 'bg-primary text-white' : 'bg-surface text-muted'}">1</div>
							<div class="w-16 h-1 {step >= 2 ? 'bg-primary' : 'bg-surface'}"></div>
							<div class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step === 2 ? 'bg-primary text-white' : 'bg-surface text-muted'}">2</div>
						{/if}
					</div>
				</div>
			{/if}

			{#if success}
				<div class="bg-success-light border border-success/20 rounded-lg p-6 text-center">
					<div class="mx-auto w-12 h-12 rounded-full bg-success/20 flex items-center justify-center mb-4">
						<CheckCircle class="w-6 h-6 text-success" />
					</div>
					{#if isInvitationFlow}
						<h3 class="text-xl font-semibold text-black mb-2">Welcome to the Team!</h3>
						<p class="text-muted mb-4">Your account has been created successfully.</p>
						<p class="text-sm text-muted">Redirecting to dashboard...</p>
					{:else}
						<h3 class="text-xl font-semibold text-black mb-2">Registration Successful!</h3>
						<p class="text-muted mb-4">Please check your email ({formData.email}) for a verification link.</p>
						<p class="text-sm text-muted">Redirecting to verification page...</p>
					{/if}
				</div>
			{:else}
				<form method="POST" action={isInvitationFlow ? '?/acceptInvitation' : '?/register'} use:enhance={({ cancel, formData: submitData }) => {
					const isFinalStep = (userType === 'company' && step === 3) || (userType === 'recruiter' && step === 2) || (isInvitationFlow && step === 2);
					if (!isFinalStep) {
						cancel();
						nextStep();
						return;
					}

					submitData.set('account_type', formData.accountType);
					submitData.set('token', invitationToken);
					submitData.set('first_name', formData.firstName);
					submitData.set('last_name', formData.lastName);
					submitData.set('email', formData.email);
					submitData.set('phone', formData.phone);
					submitData.set('job_title', formData.jobTitle);
					submitData.set('password', formData.password);
					submitData.set('confirm_password', formData.confirmPassword);
					submitData.set('agree_to_terms', formData.agreeToTerms ? 'true' : '');

					if (formData.accountType === 'company') {
						submitData.set('company_name', formData.companyName);
						submitData.set('company_website', formData.website);
						submitData.set('company_industry', formData.industry);
						submitData.set('company_size', sizeMap[formData.companySize] || '');
					}

					loading = true;
					return async ({ result, update }) => {
						loading = false;
						if (result.type === 'redirect') {
							success = true;
						}
						await update();
					};
				}} class="space-y-5">
					{#if error}
						<div class="bg-error-light border border-error/20 text-error px-4 py-3 rounded-lg text-sm whitespace-pre-line">
							{error}
						</div>
					{/if}

					{#if step === 0 && !isInvitationFlow}
						<!-- Step 0: Account Type Selection -->
						<div class="space-y-4">
							<h3 class="text-lg font-semibold text-black text-center mb-4">Choose Account Type</h3>

							<div class="grid grid-cols-1 gap-3">
								<button
									type="button"
									onclick={() => selectAccountType('company')}
									class="p-5 border-2 border-border rounded-lg hover:border-primary hover:bg-primary/5 transition-all text-left group"
								>
									<div class="flex items-start gap-4">
										<div class="w-12 h-12 rounded-lg bg-primary/10 group-hover:bg-primary flex items-center justify-center transition-colors">
											<Building2 class="w-6 h-6 text-primary group-hover:text-white transition-colors" />
										</div>
										<div class="flex-1">
											<h4 class="text-lg font-semibold text-black mb-1">Company Account</h4>
											<p class="text-sm text-muted">
												I'm registering on behalf of a company to post jobs and hire talent.
											</p>
											<ul class="mt-2 space-y-1 text-sm text-muted">
												<li class="flex items-center gap-2">
													<CheckCircle class="w-4 h-4 text-success" />
													Post unlimited jobs
												</li>
												<li class="flex items-center gap-2">
													<CheckCircle class="w-4 h-4 text-success" />
													Manage team members
												</li>
												<li class="flex items-center gap-2">
													<CheckCircle class="w-4 h-4 text-success" />
													Company branding & profile
												</li>
											</ul>
										</div>
									</div>
								</button>

								<button
									type="button"
									onclick={() => selectAccountType('recruiter')}
									class="p-5 border-2 border-border rounded-lg hover:border-primary hover:bg-primary/5 transition-all text-left group"
								>
									<div class="flex items-start gap-4">
										<div class="w-12 h-12 rounded-lg bg-primary/10 group-hover:bg-primary flex items-center justify-center transition-colors">
											<UserCircle class="w-6 h-6 text-primary group-hover:text-white transition-colors" />
										</div>
										<div class="flex-1">
											<h4 class="text-lg font-semibold text-black mb-1">Independent Recruiter</h4>
											<p class="text-sm text-muted">
												I'm an independent recruiter or consultant working with multiple companies.
											</p>
											<ul class="mt-2 space-y-1 text-sm text-muted">
												<li class="flex items-center gap-2">
													<CheckCircle class="w-4 h-4 text-success" />
													Post jobs for clients
												</li>
												<li class="flex items-center gap-2">
													<CheckCircle class="w-4 h-4 text-success" />
													Manage candidates
												</li>
												<li class="flex items-center gap-2">
													<CheckCircle class="w-4 h-4 text-success" />
													Personal recruiter profile
												</li>
											</ul>
										</div>
									</div>
								</button>
							</div>
						</div>
					{:else if userType === 'company' && step === 1}
						<!-- Company Step 1: Company Information -->
						<div class="space-y-4">
							<h3 class="text-lg font-semibold text-black mb-3">Company Information</h3>

							<FormField label="Company Name" required>
								<Input
									type="text"
									id="companyName"
									bind:value={formData.companyName}
									required
									placeholder="Your Company Name"
									size="lg"
								>
									{#snippet iconLeft()}
										<Building2 class="w-5 h-5" />
									{/snippet}
								</Input>
							</FormField>

							<FormField label="Company Website" required hint="We'll verify your company website">
								<Input
									type="url"
									id="website"
									bind:value={formData.website}
									required
									placeholder="https://yourcompany.com"
									size="lg"
								>
									{#snippet iconLeft()}
										<Globe class="w-5 h-5" />
									{/snippet}
								</Input>
							</FormField>

							<FormField label="Industry" required>
								<select
									id="industry"
									bind:value={formData.industry}
									required
									class="w-full h-12 px-4 text-base border border-border rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none"
								>
									<option value="">Select industry</option>
									{#each industries as industry}
										<option value={industry}>{industry}</option>
									{/each}
								</select>
							</FormField>

							<FormField label="Company Size" required>
								<select
									id="companySize"
									bind:value={formData.companySize}
									required
									class="w-full h-12 px-4 text-base border border-border rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none"
								>
									<option value="">Select company size</option>
									{#each companySizes as size}
										<option value={size}>{size}</option>
									{/each}
								</select>
							</FormField>
						</div>
					{:else if (userType === 'company' && step === 2) || (userType === 'recruiter' && step === 1) || (isInvitationFlow && step === 1)}
						<!-- Personal Information Step -->
						<div class="space-y-4">
							<h3 class="text-lg font-semibold text-black mb-3">Your Information</h3>

							<div class="grid grid-cols-2 gap-3">
								<FormField label="First Name" required>
									<Input
										type="text"
										id="firstName"
										bind:value={formData.firstName}
										required
										placeholder="John"
										size="lg"
									/>
								</FormField>

								<FormField label="Last Name" required>
									<Input
										type="text"
										id="lastName"
										bind:value={formData.lastName}
										required
										placeholder="Doe"
										size="lg"
									/>
								</FormField>
							</div>

							{#if !isInvitationFlow}
								<FormField label={userType === 'company' ? 'Work Email' : 'Email Address'} required hint={userType === 'company' ? 'Use your company email to verify your association' : undefined}>
									<Input
										type="email"
										id="email"
										bind:value={formData.email}
										required
										placeholder={userType === 'company' ? 'john@company.com' : 'john@example.com'}
										size="lg"
									>
										{#snippet iconLeft()}
											<Mail class="w-5 h-5" />
										{/snippet}
									</Input>
								</FormField>

								<FormField label="Phone Number" required>
									<Input
										type="tel"
										id="phone"
										bind:value={formData.phone}
										required
										placeholder="+1 (555) 123-4567"
										size="lg"
									>
										{#snippet iconLeft()}
											<Phone class="w-5 h-5" />
										{/snippet}
									</Input>
								</FormField>

								<FormField label={userType === 'company' ? 'Your Job Title' : 'Professional Title'} required>
									<Input
										type="text"
										id="jobTitle"
										bind:value={formData.jobTitle}
										required
										placeholder={userType === 'company' ? 'HR Manager, Recruiter, etc.' : 'Senior Recruiter, Talent Acquisition Specialist, etc.'}
										size="lg"
									/>
								</FormField>
							{/if}
						</div>
					{:else if (userType === 'company' && step === 3) || (userType === 'recruiter' && step === 2) || (isInvitationFlow && step === 2)}
						<!-- Final Step: Account Setup -->
						<div class="space-y-4">
							<h3 class="text-lg font-semibold text-black mb-3">{isInvitationFlow ? 'Set Your Password' : 'Create Your Account'}</h3>

							<FormField label="Password" required hint="Must be at least 8 characters">
								<div class="relative">
									<Input
										type={showPassword ? 'text' : 'password'}
										id="password"
										name="password"
										bind:value={formData.password}
										required
										placeholder="Create a strong password"
										size="lg"
										class="pr-12"
									>
										{#snippet iconLeft()}
											<Lock class="w-5 h-5" />
										{/snippet}
									</Input>
									<button
										type="button"
										onclick={() => (showPassword = !showPassword)}
										class="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-black transition-colors"
										aria-label={showPassword ? 'Hide password' : 'Show password'}
									>
										{#if showPassword}
											<EyeOff class="w-5 h-5" />
										{:else}
											<Eye class="w-5 h-5" />
										{/if}
									</button>
								</div>
							</FormField>

							<FormField label="Confirm Password" required>
								<div class="relative">
									<Input
										type={showConfirmPassword ? 'text' : 'password'}
										id="confirmPassword"
										name="confirm_password"
										bind:value={formData.confirmPassword}
										required
										placeholder="Re-enter your password"
										size="lg"
										class="pr-12"
									>
										{#snippet iconLeft()}
											<Lock class="w-5 h-5" />
										{/snippet}
									</Input>
									<button
										type="button"
										onclick={() => (showConfirmPassword = !showConfirmPassword)}
										class="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-black transition-colors"
										aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
									>
										{#if showConfirmPassword}
											<EyeOff class="w-5 h-5" />
										{:else}
											<Eye class="w-5 h-5" />
										{/if}
									</button>
								</div>
							</FormField>

							{#if !isInvitationFlow}
								<div class="space-y-3 pt-3">
									<label class="flex items-start gap-3 cursor-pointer group">
										<input
											type="checkbox"
											bind:checked={formData.agreeToTerms}
											required
											class="w-4 h-4 text-primary border-border rounded mt-0.5 focus:ring-primary/20"
										/>
										<span class="text-sm text-muted group-hover:text-black transition-colors">
											I agree to the <a href="/terms/" class="text-primary hover:text-primary-hover">Terms of Service</a>
											and <a href="/privacy/" class="text-primary hover:text-primary-hover">Privacy Policy</a>
										</span>
									</label>

									<label class="flex items-start gap-3 cursor-pointer group">
										<input
											type="checkbox"
											bind:checked={formData.subscribeNewsletter}
											class="w-4 h-4 text-primary border-border rounded mt-0.5 focus:ring-primary/20"
										/>
										<span class="text-sm text-muted group-hover:text-black transition-colors">
											Send me updates about hiring trends and platform features
										</span>
									</label>
								</div>
							{/if}
						</div>
					{/if}

					{#if step > 0}
						<!-- Navigation Buttons -->
						<div class="flex items-center justify-between mt-6 pt-6 border-t border-border">
							<Button type="button" variant="secondary" onclick={prevStep}>
								Back
							</Button>

							{#if (userType === 'company' && step < 3) || (userType === 'recruiter' && step < 2) || (isInvitationFlow && step < 2)}
								<Button type="submit">
									Continue
								</Button>
							{:else}
								<Button type="submit" disabled={(!isInvitationFlow && !formData.agreeToTerms) || loading} {loading}>
									{#if loading}
										{isInvitationFlow ? 'Joining Team...' : 'Creating Account...'}
									{:else}
										{isInvitationFlow ? 'Join Team' : 'Create Account'}
									{/if}
								</Button>
							{/if}
						</div>
					{/if}
				</form>
			{/if}

			<!-- Sign In Link -->
			<p class="mt-6 text-center text-sm text-muted">
				Already have an account?
				<a href="/login/" class="font-medium text-primary hover:text-primary-hover transition-colors">Sign in</a>
			</p>

			<!-- Trust Indicators -->
			<div class="mt-5 pt-5 border-t border-border">
				<div class="flex justify-center flex-wrap gap-4 text-xs text-muted">
					<div class="flex items-center gap-1.5">
						<Shield class="w-3.5 h-3.5" />
						<span>SSL Encrypted</span>
					</div>
					<div class="flex items-center gap-1.5">
						<CheckCircle class="w-3.5 h-3.5" />
						<span>GDPR Compliant</span>
					</div>
					<div class="flex items-center gap-1.5">
						<Clock class="w-3.5 h-3.5" />
						<span>24/7 Support</span>
					</div>
				</div>
			</div>
		</Card>
	</div>
</div>

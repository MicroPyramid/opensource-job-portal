<script lang="ts">
	import { Building2, Mail, Lock, User, Phone, Eye, EyeOff, UserCircle, Globe } from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { register } from '$lib/api/auth';
	import type { RegisterData } from '$lib/types';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-6xl';
	layout.mainClass = 'flex justify-center items-start py-2 px-4 sm:px-5 lg:px-6';

	let step = $state(0); // Start at 0 for account type selection
	let userType = $state<'recruiter' | 'company' | null>(null);
	let showPassword = $state(false);
	let showConfirmPassword = $state(false);
	let loading = $state(false);
	let error = $state('');
	let success = $state(false);

	// Form data
	let formData = $state({
		// Account type
		accountType: '' as 'recruiter' | 'company',

		// Company Info (for company accounts)
		companyName: '',
		industry: '',
		companySize: '',
		website: '',

		// Personal Info
		firstName: '',
		lastName: '',
		email: '',
		phone: '',
		jobTitle: '',

		// Account
		password: '',
		confirmPassword: '',
		agreeToTerms: false,
		subscribeNewsletter: true
	});

	const industries = [
		'Technology',
		'Finance',
		'Healthcare',
		'Education',
		'Retail',
		'Manufacturing',
		'Consulting',
		'Media',
		'Real Estate',
		'Other'
	];

	const companySizes = [
		'1-10 employees',
		'11-50 employees',
		'51-200 employees',
		'201-500 employees',
		'501-1000 employees',
		'1001-5000 employees',
		'5000+ employees'
	];

	function selectAccountType(type: 'recruiter' | 'company') {
		userType = type;
		formData.accountType = type;
		step = 1;
	}

	function nextStep() {
		// For company: steps are 1 (company info) -> 2 (personal info) -> 3 (account)
		// For recruiter: steps are 1 (personal info) -> 2 (account)
		if (userType === 'company') {
			if (step < 3) step++;
		} else {
			if (step < 2) step++;
		}
	}

	function prevStep() {
		if (step > 1) {
			step--;
		} else {
			// Go back to account type selection
			step = 0;
			userType = null;
		}
	}

	async function handleSubmit() {
		loading = true;
		error = '';

		try {
			// Map company size to API format
			const sizeMap: Record<string, string> = {
				'1-10 employees': '1-10',
				'11-50 employees': '11-20',
				'51-200 employees': '50-200',
				'201-500 employees': '200+',
				'501-1000 employees': '200+',
				'1001-5000 employees': '200+',
				'5000+ employees': '200+'
			};

			const data: RegisterData = {
				account_type: formData.accountType,
				first_name: formData.firstName,
				last_name: formData.lastName,
				email: formData.email,
				phone: formData.phone || undefined,
				job_title: formData.jobTitle || undefined,
				password: formData.password,
				confirm_password: formData.confirmPassword,
				agree_to_terms: formData.agreeToTerms
			};

			// Add company fields if company type
			if (formData.accountType === 'company') {
				data.company_name = formData.companyName;
				data.company_website = formData.website;
				data.company_industry = formData.industry || undefined;
				data.company_size = sizeMap[formData.companySize] as any;
			}

			console.log('Registering...', data);
			const response = await register(data);

			console.log('Registration successful:', response);
			success = true;

			// Show success message and redirect to verify email page
			setTimeout(() => {
				goto('/verify-email?email=' + encodeURIComponent(formData.email));
			}, 2000);
		} catch (err: any) {
			console.error('Registration error:', err);
			error = err.message || 'Registration failed. Please try again.';
		} finally {
			loading = false;
		}
	}


	// Calculate current step number for display
	function getCurrentStepNumber(): number {
		if (step === 0) return 0;
		if (userType === 'recruiter') {
			return step;
		} else {
			return step;
		}
	}

	function getTotalSteps(): number {
		return userType === 'company' ? 3 : 2;
	}
</script>

<svelte:head>
	<title>Sign Up - PeelJobs Recruiter</title>
</svelte:head>

<div class="w-full">
	<div class="grid lg:grid-cols-2 gap-10 items-start">
			<!-- Left Column: Marketing Content -->
			<div class="space-y-6 lg:sticky lg:top-6">
				<!-- Hero Section -->
				<div>
					<h1 class="text-3xl xl:text-4xl font-bold text-gray-900 mb-4 leading-tight">
						Join 10,000+ Companies Hiring with PeelJobs
					</h1>
					<p class="text-base xl:text-lg text-gray-600 leading-relaxed">
						Access India's largest talent pool with 100k+ active job seekers. Post unlimited jobs for free and find the perfect candidates faster.
					</p>
				</div>

				<!-- Key Statistics -->
				<div class="grid grid-cols-2 gap-4">
					<div class="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
						<div class="text-3xl font-bold text-blue-600 mb-1">100k+</div>
						<p class="text-sm text-gray-700 font-medium">Active Job Seekers</p>
					</div>
					<div class="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
						<div class="text-3xl font-bold text-green-600 mb-1">1000+</div>
						<p class="text-sm text-gray-700 font-medium">Daily Applications</p>
					</div>
					<div class="bg-purple-50 border border-purple-200 rounded-xl p-6 text-center">
						<div class="text-3xl font-bold text-purple-600 mb-1">500+</div>
						<p class="text-sm text-gray-700 font-medium">Companies Trust Us</p>
					</div>
					<div class="bg-orange-50 border border-orange-200 rounded-xl p-6 text-center">
						<div class="text-3xl font-bold text-orange-600 mb-1">24/7</div>
						<p class="text-sm text-gray-700 font-medium">Expert Support</p>
					</div>
				</div>

				<!-- Key Benefits -->
				<div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-7">
					<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
						<svg class="w-6 h-6 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
							<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
						</svg>
						Why Recruiters Choose PeelJobs
					</h3>
					<div class="space-y-6">
						<div class="flex items-start gap-4">
							<div class="bg-blue-100 rounded-full p-3 flex-shrink-0">
								<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
								</svg>
							</div>
							<div>
								<h4 class="font-semibold text-gray-900 text-sm mb-1">Instant Job Posting</h4>
								<p class="text-sm text-gray-600 leading-relaxed">Post unlimited jobs for free and get applications within hours</p>
							</div>
						</div>
						<div class="flex items-start gap-4">
							<div class="bg-green-100 rounded-full p-3 flex-shrink-0">
								<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
							</div>
							<div>
								<h4 class="font-semibold text-gray-900 text-sm mb-1">Smart Matching</h4>
								<p class="text-sm text-gray-600 leading-relaxed">AI-powered system matches you with the most qualified candidates</p>
							</div>
						</div>
						<div class="flex items-start gap-4">
							<div class="bg-purple-100 rounded-full p-3 flex-shrink-0">
								<svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
							</div>
							<div>
								<h4 class="font-semibold text-gray-900 text-sm mb-1">Quality Candidates</h4>
								<p class="text-sm text-gray-600 leading-relaxed">Access to verified profiles with detailed skills and experience</p>
							</div>
						</div>
						<div class="flex items-start gap-4">
							<div class="bg-orange-100 rounded-full p-3 flex-shrink-0">
								<svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
								</svg>
							</div>
							<div>
								<h4 class="font-semibold text-gray-900 text-sm mb-1">Dedicated Support</h4>
								<p class="text-sm text-gray-600 leading-relaxed">24/7 customer support to help optimize your hiring process</p>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Right Column: Registration Form -->
			<div class="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
	<!-- Header -->
	<div class="text-center mb-6">
		<h1 class="text-2xl font-bold text-gray-900">Create Employer Account</h1>
		<p class="text-gray-600 mt-2">Start hiring top talent today</p>
	</div>

	{#if step > 0}
		<!-- Progress Indicator -->
		<div class="flex items-center justify-center mb-5">
			<div class="flex items-center">
				{#if userType === 'company'}
					<!-- Company: 3 steps -->
					<div
						class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step >=
						1
							? 'bg-blue-600 text-white'
							: 'bg-gray-200 text-gray-600'}"
					>
						1
					</div>
					<div class="w-16 h-1 {step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}"></div>
					<div
						class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step >=
						2
							? 'bg-blue-600 text-white'
							: 'bg-gray-200 text-gray-600'}"
					>
						2
					</div>
					<div class="w-16 h-1 {step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}"></div>
					<div
						class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step ===
						3
							? 'bg-blue-600 text-white'
							: 'bg-gray-200 text-gray-600'}"
					>
						3
					</div>
				{:else}
					<!-- Recruiter: 2 steps -->
					<div
						class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step >=
						1
							? 'bg-blue-600 text-white'
							: 'bg-gray-200 text-gray-600'}"
					>
						1
					</div>
					<div class="w-16 h-1 {step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}"></div>
					<div
						class="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm {step ===
						2
							? 'bg-blue-600 text-white'
							: 'bg-gray-200 text-gray-600'}"
					>
						2
					</div>
				{/if}
			</div>
		</div>
	{/if}

	{#if success}
		<div class="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
			<div class="mx-auto w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-4">
				<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
				</svg>
			</div>
			<h2 class="text-xl font-bold text-gray-900 mb-2">Registration Successful!</h2>
			<p class="text-gray-600 mb-4">Please check your email ({formData.email}) for a verification link.</p>
			<p class="text-sm text-gray-500">Redirecting to verification page...</p>
		</div>
	{:else}
		<form onsubmit={(e) => { e.preventDefault(); if ((userType === 'company' && step === 3) || (userType === 'recruiter' && step === 2)) handleSubmit(); else nextStep(); }} class="space-y-5">
			{#if error}
				<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm whitespace-pre-line">
					{error}
				</div>
			{/if}

			{#if step === 0}
			<!-- Step 0: Account Type Selection -->
			<div class="space-y-4">
				<h2 class="text-lg font-semibold text-gray-900 text-center mb-4">Choose Account Type</h2>

				<div class="grid grid-cols-1 gap-3">
					<!-- Company Account -->
					<button
						type="button"
						onclick={() => selectAccountType('company')}
						class="p-5 border-2 border-gray-300 rounded-lg hover:border-blue-600 hover:bg-blue-50 transition-all text-left group"
					>
						<div class="flex items-start gap-4">
							<div class="w-12 h-12 rounded-lg bg-blue-100 group-hover:bg-blue-600 flex items-center justify-center transition-colors">
								<Building2 class="w-6 h-6 text-blue-600 group-hover:text-white transition-colors" />
							</div>
							<div class="flex-1">
								<h3 class="text-lg font-semibold text-gray-900 mb-1">Company Account</h3>
								<p class="text-sm text-gray-600">
									I'm registering on behalf of a company to post jobs and hire talent. Perfect for HR managers, company admins, and business owners.
								</p>
								<ul class="mt-2 space-y-1 text-sm text-gray-600">
									<li class="flex items-center gap-2">
										<svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
										</svg>
										Post unlimited jobs
									</li>
									<li class="flex items-center gap-2">
										<svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
										</svg>
										Manage team members
									</li>
									<li class="flex items-center gap-2">
										<svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
										</svg>
										Company branding & profile
									</li>
								</ul>
							</div>
						</div>
					</button>

					<!-- Recruiter Account -->
					<button
						type="button"
						onclick={() => selectAccountType('recruiter')}
						class="p-5 border-2 border-gray-300 rounded-lg hover:border-blue-600 hover:bg-blue-50 transition-all text-left group"
					>
						<div class="flex items-start gap-4">
							<div class="w-12 h-12 rounded-lg bg-purple-100 group-hover:bg-purple-600 flex items-center justify-center transition-colors">
								<UserCircle class="w-6 h-6 text-purple-600 group-hover:text-white transition-colors" />
							</div>
							<div class="flex-1">
								<h3 class="text-lg font-semibold text-gray-900 mb-1">Independent Recruiter</h3>
								<p class="text-sm text-gray-600">
									I'm an independent recruiter or consultant working with multiple companies. Perfect for staffing agencies and freelance recruiters.
								</p>
								<ul class="mt-2 space-y-1 text-sm text-gray-600">
									<li class="flex items-center gap-2">
										<svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
										</svg>
										Post jobs for clients
									</li>
									<li class="flex items-center gap-2">
										<svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
										</svg>
										Manage candidates
									</li>
									<li class="flex items-center gap-2">
										<svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
										</svg>
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
				<h2 class="text-lg font-semibold text-gray-900 mb-3">Company Information</h2>

				<div>
					<label for="companyName" class="block text-sm font-medium text-gray-700 mb-1">
						Company Name <span class="text-red-500">*</span>
					</label>
					<div class="relative">
						<Building2 class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type="text"
							id="companyName"
							bind:value={formData.companyName}
							required
							placeholder="Your Company Name"
							class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				<div>
					<label for="website" class="block text-sm font-medium text-gray-700 mb-1">
						Company Website <span class="text-red-500">*</span>
					</label>
					<div class="relative">
						<Globe class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type="url"
							id="website"
							bind:value={formData.website}
							required
							placeholder="https://yourcompany.com"
							class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
					<p class="text-xs text-gray-500 mt-1">We'll verify your company website</p>
				</div>

				<div>
					<label for="industry" class="block text-sm font-medium text-gray-700 mb-1">
						Industry <span class="text-red-500">*</span>
					</label>
					<select
						id="industry"
						bind:value={formData.industry}
						required
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					>
						<option value="">Select industry</option>
						{#each industries as industry}
							<option value={industry}>{industry}</option>
						{/each}
					</select>
				</div>

				<div>
					<label for="companySize" class="block text-sm font-medium text-gray-700 mb-1">
						Company Size <span class="text-red-500">*</span>
					</label>
					<select
						id="companySize"
						bind:value={formData.companySize}
						required
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					>
						<option value="">Select company size</option>
						{#each companySizes as size}
							<option value={size}>{size}</option>
						{/each}
					</select>
				</div>
			</div>
		{:else if (userType === 'company' && step === 2) || (userType === 'recruiter' && step === 1)}
			<!-- Step: Personal Information (Company Step 2 or Recruiter Step 1) -->
			<div class="space-y-4">
				<h2 class="text-lg font-semibold text-gray-900 mb-3">Your Information</h2>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="firstName" class="block text-sm font-medium text-gray-700 mb-1">
							First Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="firstName"
							bind:value={formData.firstName}
							required
							placeholder="John"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label for="lastName" class="block text-sm font-medium text-gray-700 mb-1">
							Last Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="lastName"
							bind:value={formData.lastName}
							required
							placeholder="Doe"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				<div>
					<label for="email" class="block text-sm font-medium text-gray-700 mb-1">
						{userType === 'company' ? 'Work Email' : 'Email Address'} <span class="text-red-500">*</span>
					</label>
					<div class="relative">
						<Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type="email"
							id="email"
							bind:value={formData.email}
							required
							placeholder={userType === 'company' ? 'john@company.com' : 'john@example.com'}
							class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
					{#if userType === 'company'}
						<p class="text-xs text-gray-500 mt-1">Use your company email to verify your association</p>
					{/if}
				</div>

				<div>
					<label for="phone" class="block text-sm font-medium text-gray-700 mb-1">
						Phone Number <span class="text-red-500">*</span>
					</label>
					<div class="relative">
						<Phone class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type="tel"
							id="phone"
							bind:value={formData.phone}
							required
							placeholder="+1 (555) 123-4567"
							class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				<div>
					<label for="jobTitle" class="block text-sm font-medium text-gray-700 mb-1">
						{userType === 'company' ? 'Your Job Title' : 'Professional Title'} <span class="text-red-500">*</span>
					</label>
					<input
						type="text"
						id="jobTitle"
						bind:value={formData.jobTitle}
						required
						placeholder={userType === 'company' ? 'HR Manager, Recruiter, etc.' : 'Senior Recruiter, Talent Acquisition Specialist, etc.'}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>
			</div>
		{:else}
			<!-- Final Step: Account Setup (Company Step 3 or Recruiter Step 2) -->
			<div class="space-y-4">
				<h2 class="text-lg font-semibold text-gray-900 mb-3">Create Your Account</h2>

				<div>
					<label for="password" class="block text-sm font-medium text-gray-700 mb-1">
						Password <span class="text-red-500">*</span>
					</label>
					<div class="relative">
						<Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type={showPassword ? 'text' : 'password'}
							id="password"
							bind:value={formData.password}
							required
							placeholder="Create a strong password"
							class="w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
						<button
							type="button"
							onclick={() => (showPassword = !showPassword)}
							class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
						>
							{#if showPassword}
								<EyeOff class="w-5 h-5" />
							{:else}
								<Eye class="w-5 h-5" />
							{/if}
						</button>
					</div>
					<p class="text-xs text-gray-500 mt-1">Must be at least 8 characters</p>
				</div>

				<div>
					<label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">
						Confirm Password <span class="text-red-500">*</span>
					</label>
					<div class="relative">
						<Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type={showConfirmPassword ? 'text' : 'password'}
							id="confirmPassword"
							bind:value={formData.confirmPassword}
							required
							placeholder="Re-enter your password"
							class="w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
						<button
							type="button"
							onclick={() => (showConfirmPassword = !showConfirmPassword)}
							class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
						>
							{#if showConfirmPassword}
								<EyeOff class="w-5 h-5" />
							{:else}
								<Eye class="w-5 h-5" />
							{/if}
						</button>
					</div>
				</div>

				<div class="space-y-2 pt-3">
					<label class="flex items-start gap-3 cursor-pointer">
						<input
							type="checkbox"
							bind:checked={formData.agreeToTerms}
							required
							class="w-4 h-4 text-blue-600 rounded mt-0.5"
						/>
						<span class="text-sm text-gray-700">
							I agree to the <a href="/terms/" class="text-blue-600 hover:text-blue-700">Terms of Service</a>
							and
							<a href="/privacy/" class="text-blue-600 hover:text-blue-700">Privacy Policy</a>
						</span>
					</label>

					<label class="flex items-start gap-3 cursor-pointer">
						<input
							type="checkbox"
							bind:checked={formData.subscribeNewsletter}
							class="w-4 h-4 text-blue-600 rounded mt-0.5"
						/>
						<span class="text-sm text-gray-700">
							Send me updates about hiring trends and platform features
						</span>
					</label>
				</div>
			</div>
		{/if}

		{#if step > 0}
			<!-- Navigation Buttons -->
			<div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
				<button
					type="button"
					onclick={prevStep}
					class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
				>
					Back
				</button>

				{#if (userType === 'company' && step < 3) || (userType === 'recruiter' && step < 2)}
					<button
						type="submit"
						class="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
					>
						Continue
					</button>
				{:else}
					<button
						type="submit"
						disabled={!formData.agreeToTerms || loading}
						class="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
					>
						{#if loading}
							<span class="flex items-center justify-center gap-2">
								<svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Creating Account...
							</span>
						{:else}
							Create Account
						{/if}
					</button>
				{/if}
			</div>
		{/if}
	</form>
	{/if}

	<!-- Sign In Link -->
	<p class="mt-4 text-center text-sm text-gray-600">
		Already have an account?
		<a href="/login/" class="font-medium text-blue-600 hover:text-blue-700">Sign in</a>
	</p>

	<!-- Trust Indicators -->
	<div class="mt-4 pt-3 border-t border-gray-200">
		<div class="flex justify-center flex-wrap gap-3 text-xs text-gray-500">
			<div class="flex items-center gap-1">
				<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
				</svg>
				SSL Encrypted
			</div>
			<div class="flex items-center gap-1">
				<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
				</svg>
				GDPR Compliant
			</div>
			<div class="flex items-center gap-1">
				<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
					<path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
				</svg>
				24/7 Support
			</div>
		</div>
	</div>
		</div>
	</div>
</div>

<script lang="ts">
	import {
		Building2,
		Upload,
		Globe,
		MapPin,
		Users,
		Calendar,
		Linkedin,
		Twitter,
		Facebook,
		Instagram,
		Save,
		Eye
	} from '@lucide/svelte';

	// Form data
	let formData = $state({
		companyName: 'TechCorp Inc.',
		logo: null as string | null,
		industry: 'Technology',
		companySize: '50-200',
		foundedYear: '2015',
		website: 'https://techcorp.com',
		headquarters: 'San Francisco, CA',
		about:
			'We are a leading technology company focused on building innovative solutions for modern businesses.',
		culture: 'We value collaboration, innovation, and continuous learning.',
		mission: 'To empower businesses through cutting-edge technology solutions.',
		primaryEmail: 'hr@techcorp.com',
		phone: '+1 (555) 123-4567',
		address: '123 Tech Street, San Francisco, CA 94105',
		linkedinUrl: 'https://linkedin.com/company/techcorp',
		twitterUrl: 'https://twitter.com/techcorp',
		facebookUrl: '',
		instagramUrl: ''
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
		'1-10',
		'11-50',
		'51-200',
		'201-500',
		'501-1000',
		'1001-5000',
		'5000+'
	];

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

	function saveProfile() {
		console.log('Saving profile...', formData);
		// API call here
	}

	function calculateCompleteness(): number {
		const fields = [
			formData.companyName,
			formData.logo,
			formData.industry,
			formData.companySize,
			formData.website,
			formData.headquarters,
			formData.about,
			formData.primaryEmail
		];
		const completed = fields.filter((f) => f && f.toString().trim() !== '').length;
		return Math.round((completed / fields.length) * 100);
	}

	let completeness = $derived(calculateCompleteness());
</script>

<svelte:head>
	<title>Company Profile - PeelJobs Recruiter</title>
</svelte:head>

<div class="max-w-4xl space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Company Profile</h1>
			<p class="text-gray-600 mt-1">Manage your company's public information</p>
		</div>
		<div class="flex items-center gap-3">
			<button
				class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
			>
				<Eye class="w-4 h-4" />
				Preview
			</button>
			<button
				onclick={saveProfile}
				class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
			>
				<Save class="w-4 h-4" />
				Save Changes
			</button>
		</div>
	</div>

	<!-- Profile Completeness -->
	<div class="bg-white rounded-lg border border-gray-200 p-6">
		<div class="flex items-center justify-between mb-3">
			<h3 class="text-sm font-medium text-gray-900">Profile Completeness</h3>
			<span class="text-sm font-semibold text-blue-600">{completeness}%</span>
		</div>
		<div class="w-full bg-gray-200 rounded-full h-2">
			<div class="bg-blue-600 h-2 rounded-full transition-all" style="width: {completeness}%"></div>
		</div>
		<p class="text-xs text-gray-600 mt-2">
			Complete your profile to attract more qualified candidates
		</p>
	</div>

	<!-- Company Logo -->
	<div class="bg-white rounded-lg border border-gray-200 p-6">
		<h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
			<Building2 class="w-5 h-5" />
			Company Logo
		</h2>
		<div class="flex items-start gap-6">
			<div
				class="w-32 h-32 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center bg-gray-50 overflow-hidden"
			>
				{#if formData.logo}
					<img src={formData.logo} alt="Company Logo" class="w-full h-full object-cover" />
				{:else}
					<Building2 class="w-12 h-12 text-gray-400" />
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
				<p class="text-sm text-gray-600 mt-2">
					Recommended: Square image, at least 200x200px. Max file size: 2MB.
				</p>
			</div>
		</div>
	</div>

	<!-- Basic Information -->
	<div class="bg-white rounded-lg border border-gray-200 p-6">
		<h2 class="text-lg font-semibold text-gray-900 mb-6">Basic Information</h2>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<div class="md:col-span-2">
				<label class="block text-sm font-medium text-gray-700 mb-2">
					Company Name <span class="text-red-500">*</span>
				</label>
				<input
					type="text"
					bind:value={formData.companyName}
					placeholder="Your Company Name"
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">
					Industry <span class="text-red-500">*</span>
				</label>
				<select
					bind:value={formData.industry}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				>
					{#each industries as industry}
						<option value={industry}>{industry}</option>
					{/each}
				</select>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">
					Company Size <span class="text-red-500">*</span>
				</label>
				<select
					bind:value={formData.companySize}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				>
					{#each companySizes as size}
						<option value={size}>{size} employees</option>
					{/each}
				</select>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Founded Year</label>
				<input
					type="text"
					bind:value={formData.foundedYear}
					placeholder="2015"
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Website URL</label>
				<div class="relative">
					<Globe class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
					<input
						type="url"
						bind:value={formData.website}
						placeholder="https://yourcompany.com"
						class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>
			</div>

			<div class="md:col-span-2">
				<label class="block text-sm font-medium text-gray-700 mb-2">Headquarters Location</label>
				<div class="relative">
					<MapPin class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
					<input
						type="text"
						bind:value={formData.headquarters}
						placeholder="City, State, Country"
						class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>
			</div>
		</div>
	</div>

	<!-- About Company -->
	<div class="bg-white rounded-lg border border-gray-200 p-6">
		<h2 class="text-lg font-semibold text-gray-900 mb-6">About Company</h2>
		<div class="space-y-6">
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">
					Company Description <span class="text-red-500">*</span>
				</label>
				<textarea
					bind:value={formData.about}
					rows="5"
					placeholder="Tell candidates about your company..."
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				></textarea>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Company Culture</label>
				<textarea
					bind:value={formData.culture}
					rows="4"
					placeholder="Describe your company culture and values..."
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				></textarea>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Mission Statement</label>
				<textarea
					bind:value={formData.mission}
					rows="3"
					placeholder="What is your company's mission?"
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				></textarea>
			</div>
		</div>
	</div>

	<!-- Contact Information -->
	<div class="bg-white rounded-lg border border-gray-200 p-6">
		<h2 class="text-lg font-semibold text-gray-900 mb-6">Contact Information</h2>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">
					Primary Email <span class="text-red-500">*</span>
				</label>
				<input
					type="email"
					bind:value={formData.primaryEmail}
					placeholder="hr@yourcompany.com"
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
				<input
					type="tel"
					bind:value={formData.phone}
					placeholder="+1 (555) 123-4567"
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<div class="md:col-span-2">
				<label class="block text-sm font-medium text-gray-700 mb-2">Office Address</label>
				<textarea
					bind:value={formData.address}
					rows="2"
					placeholder="Full office address"
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				></textarea>
			</div>
		</div>
	</div>

	<!-- Social Media Links -->
	<div class="bg-white rounded-lg border border-gray-200 p-6">
		<h2 class="text-lg font-semibold text-gray-900 mb-6">Social Media</h2>
		<div class="space-y-4">
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">LinkedIn</label>
				<div class="relative">
					<Linkedin class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
					<input
						type="url"
						bind:value={formData.linkedinUrl}
						placeholder="https://linkedin.com/company/yourcompany"
						class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Twitter</label>
				<div class="relative">
					<Twitter class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
					<input
						type="url"
						bind:value={formData.twitterUrl}
						placeholder="https://twitter.com/yourcompany"
						class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Facebook</label>
				<div class="relative">
					<Facebook class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
					<input
						type="url"
						bind:value={formData.facebookUrl}
						placeholder="https://facebook.com/yourcompany"
						class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Instagram</label>
				<div class="relative">
					<Instagram class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
					<input
						type="url"
						bind:value={formData.instagramUrl}
						placeholder="https://instagram.com/yourcompany"
						class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					/>
				</div>
			</div>
		</div>
	</div>

	<!-- Save Button -->
	<div class="flex justify-end">
		<button
			onclick={saveProfile}
			class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors"
		>
			<Save class="w-4 h-4" />
			Save Changes
		</button>
	</div>
</div>

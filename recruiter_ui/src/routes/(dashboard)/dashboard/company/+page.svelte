<script lang="ts">
	import {
		Building2,
		Upload,
		Globe,
		MapPin,
		Save,
		CheckCircle,
		XCircle
	} from '@lucide/svelte';
	import { enhance } from '$app/forms';
	import type { PageData, ActionData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	// Form data initialized from loaded company data
	let formData = $state({
		companyName: data.company?.name || '',
		logo: data.company?.logo_url || null as string | null,
		companySize: data.company?.size || '1-10',
		website: data.company?.website || '',
		about: data.company?.profile || '',
		primaryEmail: data.company?.email || '',
		phone: data.company?.phone_number || '',
		address: data.company?.address || ''
	});

	const companySizes = [
		'1-10',
		'11-20',
		'21-50',
		'50-200',
		'200+'
	];

	let saving = $state(false);
	let showSuccessMessage = $state(false);
	let showErrorMessage = $state(false);

	// Watch for form submission result
	$effect(() => {
		if (form?.success) {
			showSuccessMessage = true;
			saving = false;
			// Update form data with returned company data
			if (form.company) {
				formData.companyName = form.company.name;
				formData.companySize = form.company.size;
				formData.website = form.company.website || '';
				formData.about = form.company.profile || '';
				formData.primaryEmail = form.company.email || '';
				formData.phone = form.company.phone_number || '';
				formData.address = form.company.address || '';
				formData.logo = form.company.logo_url || null;
			}
			setTimeout(() => {
				showSuccessMessage = false;
			}, 5000);
		} else if (form?.success === false) {
			showErrorMessage = true;
			saving = false;
			setTimeout(() => {
				showErrorMessage = false;
			}, 5000);
		}
	});

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

	function calculateCompleteness(): number {
		const fields = [
			formData.companyName,
			formData.logo,
			formData.companySize,
			formData.website,
			formData.about,
			formData.primaryEmail
		];
		const completed = fields.filter((f) => f && f.toString().trim() !== '').length;
		return Math.round((completed / fields.length) * 100);
	}

	let completeness = $derived(calculateCompleteness());
	let isAdmin = $derived(data.user?.is_admin === true);
</script>

<svelte:head>
	<title>Company Profile - PeelJobs Recruiter</title>
</svelte:head>

<div class="max-w-4xl space-y-6">
	<!-- Success/Error Messages -->
	{#if showSuccessMessage}
		<div class="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
			<CheckCircle class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
			<div class="flex-1">
				<h3 class="text-sm font-medium text-green-900">Success!</h3>
				<p class="text-sm text-green-700 mt-1">{form?.message || 'Company profile updated successfully'}</p>
			</div>
		</div>
	{/if}

	{#if showErrorMessage}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
			<XCircle class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
			<div class="flex-1">
				<h3 class="text-sm font-medium text-red-900">Error</h3>
				<p class="text-sm text-red-700 mt-1">{form?.error || 'Failed to update company profile'}</p>
			</div>
		</div>
	{/if}

	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Company Profile</h1>
			<p class="text-gray-600 mt-1">Manage your company's public information</p>
			{#if !isAdmin}
				<p class="text-sm text-amber-600 mt-1">⚠️ Only company admins can edit the profile</p>
			{/if}
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

	<!-- Company Form -->
	<form
		method="POST"
		action="?/updateCompany"
		use:enhance={() => {
			saving = true;
			return async ({ update }) => {
				await update();
			};
		}}
	>
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
						name="name"
						bind:value={formData.companyName}
						placeholder="Your Company Name"
						required
						disabled={!isAdmin}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
					/>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Company Size <span class="text-red-500">*</span>
					</label>
					<select
						name="size"
						bind:value={formData.companySize}
						disabled={!isAdmin}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
					>
						{#each companySizes as size}
							<option value={size}>{size} employees</option>
						{/each}
					</select>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">Website URL</label>
					<div class="relative">
						<Globe class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type="url"
							name="website"
							bind:value={formData.website}
							placeholder="https://yourcompany.com"
							disabled={!isAdmin}
							class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
						/>
					</div>
				</div>
			</div>
		</div>

		<!-- About Company -->
		<div class="bg-white rounded-lg border border-gray-200 p-6 mt-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-6">About Company</h2>
			<div class="space-y-6">
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Company Description <span class="text-red-500">*</span>
					</label>
					<textarea
						name="profile"
						bind:value={formData.about}
						rows="5"
						placeholder="Tell candidates about your company..."
						disabled={!isAdmin}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
					></textarea>
				</div>
			</div>
		</div>

		<!-- Contact Information -->
		<div class="bg-white rounded-lg border border-gray-200 p-6 mt-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-6">Contact Information</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">
						Primary Email <span class="text-red-500">*</span>
					</label>
					<input
						type="email"
						name="email"
						bind:value={formData.primaryEmail}
						placeholder="hr@yourcompany.com"
						disabled={!isAdmin}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
					/>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
					<input
						type="tel"
						name="phone_number"
						bind:value={formData.phone}
						placeholder="+91-9876543210"
						disabled={!isAdmin}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
					/>
				</div>

				<div class="md:col-span-2">
					<label class="block text-sm font-medium text-gray-700 mb-2">Office Address</label>
					<textarea
						name="address"
						bind:value={formData.address}
						rows="2"
						placeholder="Full office address"
						disabled={!isAdmin}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
					></textarea>
				</div>
			</div>
		</div>

		<!-- Save Button -->
		{#if isAdmin}
			<div class="flex justify-end mt-6">
				<button
					type="submit"
					disabled={saving}
					class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 rounded-lg text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
				>
					<Save class="w-4 h-4" />
					{saving ? 'Saving...' : 'Save Changes'}
				</button>
			</div>
		{/if}
	</form>
</div>

<script lang="ts">
	import { User, Mail, Phone, Briefcase, Camera, Loader2 } from '@lucide/svelte';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import type { PageData, ActionData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	// Form state
	let isEditing = $state(false);
	let isUploadingPicture = $state(false);

	// User data from server load (SSR-safe)
	let user = $derived(data.user);

	function startEditing() {
		isEditing = true;
	}

	function cancelEditing() {
		isEditing = false;
	}
</script>

<div class="max-w-7xl mx-auto px-4 py-6">
	<!-- Page Header -->
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Account Settings</h1>
			<p class="mt-1 text-sm text-gray-600">Manage your profile information</p>
		</div>

		{#if !isEditing}
			<button
				onclick={startEditing}
				class="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
			>
				Edit Profile
			</button>
		{/if}
	</div>

	<!-- Success/Error Messages -->
	{#if form?.success}
		<div class="mb-4 p-3 bg-green-50 border border-green-200 text-green-800 rounded-md text-sm">
			{form.message}
		</div>
	{/if}

	{#if form?.error}
		<div class="mb-4 p-3 bg-red-50 border border-red-200 text-red-800 rounded-md text-sm">
			{form.error}
		</div>
	{/if}

	<!-- Main Content Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Left Column: Profile Picture + Account Info -->
		<div class="lg:col-span-1 space-y-6">
			<!-- Profile Picture Card -->
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
				<h2 class="text-sm font-semibold text-gray-900 mb-4">Profile Picture</h2>

				<form
					method="POST"
					action="?/uploadPicture"
					enctype="multipart/form-data"
					use:enhance={() => {
						isUploadingPicture = true;
						return async ({ result, update }) => {
							isUploadingPicture = false;
							if (result.type === 'success') {
								await invalidateAll(); // Reload user data
							}
							await update();
						};
					}}
				>
					<div class="flex flex-col items-center">
						<div class="relative mb-4">
							{#if user?.profile_pic}
								<img
									src={user.profile_pic}
									alt="Profile"
									class="w-32 h-32 rounded-full object-cover border-2 border-gray-200"
								/>
							{:else}
								<div
									class="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center border-2 border-gray-300"
								>
									<User class="w-16 h-16 text-gray-500" />
								</div>
							{/if}

							{#if isUploadingPicture}
								<div
									class="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center"
								>
									<Loader2 class="w-6 h-6 text-white animate-spin" />
								</div>
							{/if}
						</div>

						<label
							for="profile-picture"
							class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
						>
							<Camera class="w-4 h-4" />
							{isUploadingPicture ? 'Uploading...' : 'Change'}
						</label>
						<input
							id="profile-picture"
							name="profile_pic"
							type="file"
							accept="image/jpeg,image/jpg,image/png"
							onchange={(e) => {
								const form = e.currentTarget.form;
								if (form && e.currentTarget.files?.length) {
									form.requestSubmit();
								}
							}}
							disabled={isUploadingPicture}
							class="hidden"
						/>
						<p class="mt-2 text-xs text-gray-500 text-center">JPG, PNG. Max 2MB.</p>
					</div>
				</form>
			</div>

			<!-- Account Information Card -->
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
				<h2 class="text-sm font-semibold text-gray-900 mb-4">Account Details</h2>

				<div class="space-y-3">
					<div class="flex flex-col gap-1">
						<span class="text-xs font-medium text-gray-500">Account Type</span>
						<span class="text-sm text-gray-900">
							{#if user?.company}
								Company Account
							{:else}
								Independent Recruiter
							{/if}
						</span>
					</div>

					{#if user?.company}
						<div class="flex flex-col gap-1 pt-3 border-t border-gray-100">
							<span class="text-xs font-medium text-gray-500">Company</span>
							<span class="text-sm text-gray-900">{user.company.name}</span>
						</div>

						<div class="flex flex-col gap-1 pt-3 border-t border-gray-100">
							<span class="text-xs font-medium text-gray-500">Role</span>
							<span class="text-sm text-gray-900">
								{user.is_admin ? 'Company Admin' : 'Team Member'}
							</span>
						</div>
					{/if}

					<div class="flex flex-col gap-1 pt-3 border-t border-gray-100">
						<span class="text-xs font-medium text-gray-500">Member Since</span>
						<span class="text-sm text-gray-900">
							{new Date(user?.date_joined || '').toLocaleDateString('en-US', {
								year: 'numeric',
								month: 'short',
								day: 'numeric'
							})}
						</span>
					</div>

					<div class="flex flex-col gap-1 pt-3 border-t border-gray-100">
						<span class="text-xs font-medium text-gray-500">Email Status</span>
						<span class="text-sm">
							{#if user?.email_verified}
								<span class="text-green-600 font-medium">✓ Verified</span>
							{:else}
								<span class="text-amber-600 font-medium">⚠ Not Verified</span>
							{/if}
						</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Right Column: Profile Information Form -->
		<div class="lg:col-span-2">
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
				<h2 class="text-sm font-semibold text-gray-900 mb-6">Profile Information</h2>

				<form
					method="POST"
					action="?/updateProfile"
					use:enhance={() => {
						return async ({ result, update }) => {
							if (result.type === 'success') {
								isEditing = false;
								await invalidateAll(); // Reload user data
							}
							await update();
						};
					}}
				>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<!-- First Name -->
						<div>
							<label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
								First Name *
							</label>
							{#if isEditing}
								<input
									type="text"
									id="first_name"
									name="first_name"
									value={user?.first_name || ''}
									required
									class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
							{:else}
								<div class="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-md">
									<User class="w-4 h-4 text-gray-400" />
									<span class="text-sm text-gray-900">{user?.first_name || 'Not set'}</span>
								</div>
							{/if}
						</div>

						<!-- Last Name -->
						<div>
							<label for="last_name" class="block text-sm font-medium text-gray-700 mb-2">
								Last Name
							</label>
							{#if isEditing}
								<input
									type="text"
									id="last_name"
									name="last_name"
									value={user?.last_name || ''}
									class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
							{:else}
								<div class="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-md">
									<User class="w-4 h-4 text-gray-400" />
									<span class="text-sm text-gray-900">{user?.last_name || 'Not set'}</span>
								</div>
							{/if}
						</div>

						<!-- Email (Read-only) -->
						<div>
							<label for="email" class="block text-sm font-medium text-gray-700 mb-2">
								Email Address
							</label>
							<div
								class="flex items-center justify-between gap-2 px-3 py-2 bg-gray-50 rounded-md"
							>
								<div class="flex items-center gap-2 min-w-0">
									<Mail class="w-4 h-4 text-gray-400 flex-shrink-0" />
									<span class="text-sm text-gray-900 truncate">{user?.email}</span>
								</div>
								<span class="text-xs text-gray-500 flex-shrink-0">Read-only</span>
							</div>
						</div>

						<!-- Job Title -->
						<div>
							<label for="job_title" class="block text-sm font-medium text-gray-700 mb-2">
								Job Title
							</label>
							{#if isEditing}
								<input
									type="text"
									id="job_title"
									name="job_title"
									value={user?.job_title || ''}
									placeholder="e.g., Senior Recruiter"
									class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
							{:else}
								<div class="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-md">
									<Briefcase class="w-4 h-4 text-gray-400" />
									<span class="text-sm text-gray-900">{user?.job_title || 'Not set'}</span>
								</div>
							{/if}
						</div>

						<!-- Mobile -->
						<div class="md:col-span-2">
							<label for="mobile" class="block text-sm font-medium text-gray-700 mb-2">
								Phone Number
							</label>
							{#if isEditing}
								<input
									type="tel"
									id="mobile"
									name="mobile"
									value={user?.mobile || ''}
									placeholder="+1234567890"
									class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
							{:else}
								<div class="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-md">
									<Phone class="w-4 h-4 text-gray-400" />
									<span class="text-sm text-gray-900">{user?.mobile || 'Not set'}</span>
								</div>
							{/if}
						</div>

						<!-- Action Buttons (only shown when editing) -->
						{#if isEditing}
							<div class="md:col-span-2 flex items-center gap-3 pt-4 border-t border-gray-200">
								<button
									type="submit"
									class="px-6 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
								>
									Save Changes
								</button>
								<button
									type="button"
									onclick={cancelEditing}
									class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
								>
									Cancel
								</button>
							</div>
						{/if}
					</div>
				</form>
			</div>
		</div>
	</div>
</div>

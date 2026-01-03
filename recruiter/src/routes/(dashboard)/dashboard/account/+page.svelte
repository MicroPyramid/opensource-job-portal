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
			<h1 class="text-2xl font-bold text-black">Account Settings</h1>
			<p class="mt-1 text-sm text-muted">Manage your profile information</p>
		</div>

		{#if !isEditing}
			<button
				onclick={startEditing}
				class="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors"
			>
				Edit Profile
			</button>
		{/if}
	</div>

	<!-- Success/Error Messages -->
	{#if form?.success}
		<div class="mb-4 p-3 bg-success-light border border-success/30 text-success rounded-lg text-sm">
			{form.message}
		</div>
	{/if}

	{#if form?.error}
		<div class="mb-4 p-3 bg-error-light border border-error/30 text-error rounded-lg text-sm">
			{form.error}
		</div>
	{/if}

	<!-- Main Content Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Left Column: Profile Picture + Account Info -->
		<div class="lg:col-span-1 space-y-6">
			<!-- Profile Picture Card -->
			<div class="bg-white rounded-lg shadow-sm border border-border p-6">
				<h2 class="text-sm font-semibold text-black mb-4">Profile Picture</h2>

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
									class="w-32 h-32 rounded-full object-cover border-2 border-border"
								/>
							{:else}
								<div
									class="w-32 h-32 rounded-full bg-surface flex items-center justify-center border-2 border-border"
								>
									<User class="w-16 h-16 text-muted" />
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
							class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-border rounded-lg text-sm font-medium text-muted hover:bg-surface cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
						<p class="mt-2 text-xs text-muted text-center">JPG, PNG. Max 2MB.</p>
					</div>
				</form>
			</div>

			<!-- Account Information Card -->
			<div class="bg-white rounded-lg shadow-sm border border-border p-6">
				<h2 class="text-sm font-semibold text-black mb-4">Account Details</h2>

				<div class="space-y-3">
					<div class="flex flex-col gap-1">
						<span class="text-xs font-medium text-muted">Account Type</span>
						<span class="text-sm text-black">
							{#if user?.company}
								Company Account
							{:else}
								Independent Recruiter
							{/if}
						</span>
					</div>

					{#if user?.company}
						<div class="flex flex-col gap-1 pt-3 border-t border-border">
							<span class="text-xs font-medium text-muted">Company</span>
							<span class="text-sm text-black">{user.company.name}</span>
						</div>

						<div class="flex flex-col gap-1 pt-3 border-t border-border">
							<span class="text-xs font-medium text-muted">Role</span>
							<span class="text-sm text-black">
								{user.is_admin ? 'Company Admin' : 'Team Member'}
							</span>
						</div>
					{/if}

					<div class="flex flex-col gap-1 pt-3 border-t border-border">
						<span class="text-xs font-medium text-muted">Member Since</span>
						<span class="text-sm text-black">
							{new Date(user?.date_joined || '').toLocaleDateString('en-US', {
								year: 'numeric',
								month: 'short',
								day: 'numeric'
							})}
						</span>
					</div>

					<div class="flex flex-col gap-1 pt-3 border-t border-border">
						<span class="text-xs font-medium text-muted">Email Status</span>
						<span class="text-sm">
							{#if user?.email_verified}
								<span class="text-success font-medium">✓ Verified</span>
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
			<div class="bg-white rounded-lg shadow-sm border border-border p-6">
				<h2 class="text-sm font-semibold text-black mb-6">Profile Information</h2>

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
							<label for="first_name" class="block text-sm font-medium text-muted mb-2">
								First Name *
							</label>
							{#if isEditing}
								<input
									type="text"
									id="first_name"
									name="first_name"
									value={user?.first_name || ''}
									required
									class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
								/>
							{:else}
								<div class="flex items-center gap-2 px-3 py-2 bg-surface rounded-lg">
									<User class="w-4 h-4 text-muted" />
									<span class="text-sm text-black">{user?.first_name || 'Not set'}</span>
								</div>
							{/if}
						</div>

						<!-- Last Name -->
						<div>
							<label for="last_name" class="block text-sm font-medium text-muted mb-2">
								Last Name
							</label>
							{#if isEditing}
								<input
									type="text"
									id="last_name"
									name="last_name"
									value={user?.last_name || ''}
									class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
								/>
							{:else}
								<div class="flex items-center gap-2 px-3 py-2 bg-surface rounded-lg">
									<User class="w-4 h-4 text-muted" />
									<span class="text-sm text-black">{user?.last_name || 'Not set'}</span>
								</div>
							{/if}
						</div>

						<!-- Email (Read-only) -->
						<div>
							<label for="email" class="block text-sm font-medium text-muted mb-2">
								Email Address
							</label>
							<div
								class="flex items-center justify-between gap-2 px-3 py-2 bg-surface rounded-lg"
							>
								<div class="flex items-center gap-2 min-w-0">
									<Mail class="w-4 h-4 text-muted flex-shrink-0" />
									<span class="text-sm text-black truncate">{user?.email}</span>
								</div>
								<span class="text-xs text-muted flex-shrink-0">Read-only</span>
							</div>
						</div>

						<!-- Job Title -->
						<div>
							<label for="job_title" class="block text-sm font-medium text-muted mb-2">
								Job Title
							</label>
							{#if isEditing}
								<input
									type="text"
									id="job_title"
									name="job_title"
									value={user?.job_title || ''}
									placeholder="e.g., Senior Recruiter"
									class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
								/>
							{:else}
								<div class="flex items-center gap-2 px-3 py-2 bg-surface rounded-lg">
									<Briefcase class="w-4 h-4 text-muted" />
									<span class="text-sm text-black">{user?.job_title || 'Not set'}</span>
								</div>
							{/if}
						</div>

						<!-- Mobile -->
						<div class="md:col-span-2">
							<label for="mobile" class="block text-sm font-medium text-muted mb-2">
								Phone Number
							</label>
							{#if isEditing}
								<input
									type="tel"
									id="mobile"
									name="mobile"
									value={user?.mobile || ''}
									placeholder="+1234567890"
									class="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
								/>
							{:else}
								<div class="flex items-center gap-2 px-3 py-2 bg-surface rounded-lg">
									<Phone class="w-4 h-4 text-muted" />
									<span class="text-sm text-black">{user?.mobile || 'Not set'}</span>
								</div>
							{/if}
						</div>

						<!-- Action Buttons (only shown when editing) -->
						{#if isEditing}
							<div class="md:col-span-2 flex items-center gap-3 pt-4 border-t border-border">
								<button
									type="submit"
									class="px-6 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
								>
									Save Changes
								</button>
								<button
									type="button"
									onclick={cancelEditing}
									class="px-6 py-2 bg-white border border-border text-muted rounded-lg text-sm font-medium hover:bg-surface transition-colors"
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

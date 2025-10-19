<script lang="ts">
	import { onMount } from 'svelte';
	import { Settings, Lock, Bell, Shield } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import { authStore } from '$lib/stores/auth';
	import { getProfile } from '$lib/api/profile';
	import {
		changePassword,
		updateNotificationSettings,
		updatePrivacySettings,
		type PasswordChangeData,
		type NotificationSettings,
		type PrivacySettings
	} from '$lib/api/settings';

	// Tab state
	let activeTab = $state<'privacy' | 'notifications' | 'password'>('privacy');

	// Loading states
	let loading = $state(false);
	let profileLoading = $state(true);

	// Privacy settings
	let privacyData = $state<PrivacySettings>({
		show_email: false,
		is_looking_for_job: false,
		is_open_to_offers: false
	});

	// Notification settings
	let notificationData = $state<NotificationSettings>({
		email_notifications: true,
		is_unsubscribe: false
	});

	// Password change data
	let passwordData = $state<PasswordChangeData>({
		old_password: '',
		new_password: '',
		confirm_password: ''
	});

	onMount(async () => {
		await loadProfile();
	});

	async function loadProfile() {
		try {
			profileLoading = true;
			const profile = await getProfile();

			// Populate privacy settings
			privacyData = {
				show_email: profile.show_email ?? false,
				is_looking_for_job: profile.is_looking_for_job ?? false,
				is_open_to_offers: profile.is_open_to_offers ?? false
			};

			// Populate notification settings
			notificationData = {
				email_notifications: profile.email_notifications ?? true,
				is_unsubscribe: profile.is_unsubscribe ?? false
			};
		} catch (error: any) {
			toast.error(error.message || 'Failed to load profile');
		} finally {
			profileLoading = false;
		}
	}

	async function handleSavePrivacy() {
		try {
			loading = true;
			await updatePrivacySettings(privacyData);
			toast.success('Privacy settings updated successfully');
		} catch (error: any) {
			toast.error(error.message || 'Failed to update privacy settings');
		} finally {
			loading = false;
		}
	}

	async function handleSaveNotifications() {
		try {
			loading = true;
			await updateNotificationSettings(notificationData);
			toast.success('Notification settings updated successfully');
		} catch (error: any) {
			toast.error(error.message || 'Failed to update notification settings');
		} finally {
			loading = false;
		}
	}

	async function handleChangePassword(e: Event) {
		e.preventDefault();

		if (!passwordData.old_password || !passwordData.new_password || !passwordData.confirm_password) {
			toast.error('All password fields are required');
			return;
		}

		if (passwordData.new_password !== passwordData.confirm_password) {
			toast.error('New passwords do not match');
			return;
		}

		if (passwordData.new_password.length < 8) {
			toast.error('Password must be at least 8 characters');
			return;
		}

		try {
			loading = true;
			await changePassword(passwordData);
			toast.success('Password changed successfully');

			// Reset form
			passwordData = {
				old_password: '',
				new_password: '',
				confirm_password: ''
			};
		} catch (error: any) {
			const errorMsg = error.error?.old_password?.[0] || error.message || 'Failed to change password';
			toast.error(errorMsg);
		} finally {
			loading = false;
		}
	}
</script>

<!-- Header -->
<div class="mb-8">
	<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Settings</h1>
	<p class="text-gray-600 mt-2">Manage your account settings and preferences</p>
</div>

{#if profileLoading}
	<div class="flex items-center justify-center py-12">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
	</div>
		{:else}
	<!-- Tabs -->
	<div class="bg-white rounded-lg shadow-sm mb-6">
		<div class="border-b border-gray-200">
			<nav class="flex -mb-px overflow-x-auto" aria-label="Settings tabs">
				<button
					onclick={() => (activeTab = 'privacy')}
					class="flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 whitespace-nowrap {activeTab ===
					'privacy'
						? 'border-blue-600 text-blue-600'
						: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
				>
					<Shield class="w-4 h-4" />
					Privacy
				</button>

				<button
					onclick={() => (activeTab = 'notifications')}
					class="flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 whitespace-nowrap {activeTab ===
					'notifications'
						? 'border-blue-600 text-blue-600'
						: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
				>
					<Bell class="w-4 h-4" />
					Notifications
				</button>

				<button
					onclick={() => (activeTab = 'password')}
					class="flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 whitespace-nowrap {activeTab ===
					'password'
						? 'border-blue-600 text-blue-600'
						: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
				>
					<Lock class="w-4 h-4" />
					Password
				</button>
			</nav>
		</div>

		<!-- Tab Content -->
		<div class="p-6">
			{#if activeTab === 'privacy'}
				<!-- Privacy Settings -->
				<div class="space-y-6">
					<div>
						<h2 class="text-xl font-semibold text-gray-900 mb-4">Privacy Settings</h2>
						<p class="text-gray-600 text-sm mb-6">
							Control how your information is displayed to recruiters and other users.
						</p>

						<div class="space-y-4">
							<div class="flex items-start">
								<div class="flex items-center h-5">
									<input
										id="show_email"
										type="checkbox"
										bind:checked={privacyData.show_email}
										class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
									/>
								</div>
								<div class="ml-3">
									<label for="show_email" class="font-medium text-gray-900"
										>Show email to recruiters</label
									>
									<p class="text-sm text-gray-600">
										Allow recruiters to see your email address in your profile
									</p>
								</div>
							</div>

							<div class="flex items-start">
								<div class="flex items-center h-5">
									<input
										id="is_looking_for_job"
										type="checkbox"
										bind:checked={privacyData.is_looking_for_job}
										class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
									/>
								</div>
								<div class="ml-3">
									<label for="is_looking_for_job" class="font-medium text-gray-900"
										>Currently looking for a job</label
									>
									<p class="text-sm text-gray-600">
										Indicate that you are actively seeking new opportunities
									</p>
								</div>
							</div>

							<div class="flex items-start">
								<div class="flex items-center h-5">
									<input
										id="is_open_to_offers"
										type="checkbox"
										bind:checked={privacyData.is_open_to_offers}
										class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
									/>
								</div>
								<div class="ml-3">
									<label for="is_open_to_offers" class="font-medium text-gray-900"
										>Open to job offers</label
									>
									<p class="text-sm text-gray-600">
										Let recruiters know you're open to hearing about new opportunities
									</p>
								</div>
							</div>
						</div>
					</div>

					<div class="flex justify-end pt-4">
						<button
							onclick={handleSavePrivacy}
							disabled={loading}
							class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							{loading ? 'Saving...' : 'Save Privacy Settings'}
						</button>
					</div>
				</div>
			{:else if activeTab === 'notifications'}
				<!-- Notification Settings -->
				<div class="space-y-6">
					<div>
						<h2 class="text-xl font-semibold text-gray-900 mb-4">Notification Preferences</h2>
						<p class="text-gray-600 text-sm mb-6">
							Manage how you receive updates and communications from PeelJobs.
						</p>

						<div class="space-y-4">
							<div class="flex items-start">
								<div class="flex items-center h-5">
									<input
										id="email_notifications"
										type="checkbox"
										bind:checked={notificationData.email_notifications}
										class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
									/>
								</div>
								<div class="ml-3">
									<label for="email_notifications" class="font-medium text-gray-900"
										>Email notifications</label
									>
									<p class="text-sm text-gray-600">
										Receive email notifications about job matches, applications, and updates
									</p>
								</div>
							</div>

							<div class="flex items-start">
								<div class="flex items-center h-5">
									<input
										id="is_unsubscribe"
										type="checkbox"
										bind:checked={notificationData.is_unsubscribe}
										class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
									/>
								</div>
								<div class="ml-3">
									<label for="is_unsubscribe" class="font-medium text-gray-900"
										>Unsubscribe from all emails</label
									>
									<p class="text-sm text-gray-600">
										Stop receiving all promotional and marketing emails (important account
										emails will still be sent)
									</p>
								</div>
							</div>
						</div>
					</div>

					<div class="flex justify-end pt-4">
						<button
							onclick={handleSaveNotifications}
							disabled={loading}
							class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							{loading ? 'Saving...' : 'Save Notification Settings'}
						</button>
					</div>
				</div>
			{:else if activeTab === 'password'}
				<!-- Password Change -->
				<div class="space-y-6">
					<div>
						<h2 class="text-xl font-semibold text-gray-900 mb-4">Change Password</h2>
						<p class="text-gray-600 text-sm mb-6">
							Update your password to keep your account secure.
						</p>

						<form onsubmit={handleChangePassword} class="space-y-4 max-w-md">
							<div>
								<label for="old_password" class="block text-sm font-medium text-gray-700 mb-1"
									>Current Password</label
								>
								<input
									id="old_password"
									type="password"
									bind:value={passwordData.old_password}
									required
									class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
							</div>

							<div>
								<label for="new_password" class="block text-sm font-medium text-gray-700 mb-1"
									>New Password</label
								>
								<input
									id="new_password"
									type="password"
									bind:value={passwordData.new_password}
									required
									minlength="8"
									class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
								<p class="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
							</div>

							<div>
								<label
									for="confirm_password"
									class="block text-sm font-medium text-gray-700 mb-1"
									>Confirm New Password</label
								>
								<input
									id="confirm_password"
									type="password"
									bind:value={passwordData.confirm_password}
									required
									minlength="8"
									class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
							</div>

							<div class="pt-4">
								<button
									type="submit"
									disabled={loading}
									class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
								>
									{loading ? 'Changing Password...' : 'Change Password'}
								</button>
							</div>
						</form>
					</div>
				</div>
			{/if}
		</div>
	</div>
{/if}

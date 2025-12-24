<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { toast } from '$lib/stores/toast';
	import { getProfile, patchProfile, type UserProfile } from '$lib/api/profile';
	import { Save, Loader, User, Sparkles } from '@lucide/svelte';

	import ProfilePictureSection from '$lib/components/profile/ProfilePictureSection.svelte';
	import PersonalInfoSection from '$lib/components/profile/PersonalInfoSection.svelte';
	import AddressInfoSection from '$lib/components/profile/AddressInfoSection.svelte';
	import LocationSection from '$lib/components/profile/LocationSection.svelte';
	import ProfessionalInfoSection from '$lib/components/profile/ProfessionalInfoSection.svelte';

	let profile: UserProfile | null = null;
	let loading = true;
	let saving = false;
	let validationErrors: Record<string, string> = {};

	let formData = {
		first_name: '',
		last_name: '',
		mobile: '',
		alternate_mobile: '',
		gender: '',
		dob: '',
		marital_status: '',
		nationality: '',
		address: '',
		permanent_address: '',
		pincode: '',
		city_id: undefined as number | undefined,
		state_id: undefined as number | undefined,
		country_id: undefined as number | undefined,
		current_city_id: undefined as number | undefined,
		preferred_city_ids: [] as number[],
		job_role: '',
		profile_description: '',
		year: '',
		month: '',
		current_salary: '',
		expected_salary: '',
		notice_period: '',
		relocation: false
	};

	onMount(async () => {
		await loadProfile();
	});

	async function loadProfile() {
		try {
			loading = true;
			profile = await getProfile();

			formData = {
				first_name: profile.first_name || '',
				last_name: profile.last_name || '',
				mobile: profile.mobile || '',
				alternate_mobile: profile.alternate_mobile?.toString() || '',
				gender: profile.gender || '',
				dob: profile.dob || '',
				marital_status: profile.marital_status || '',
				nationality: profile.nationality || '',
				address: profile.address || '',
				permanent_address: profile.permanent_address || '',
				pincode: profile.pincode?.toString() || '',
				city_id: profile.city?.id,
				state_id: profile.state?.id,
				country_id: profile.country?.id,
				current_city_id: profile.current_city?.id,
				preferred_city_ids: profile.preferred_city?.map((c) => c.id) || [],
				job_role: profile.job_role || '',
				profile_description: profile.profile_description || '',
				year: profile.year || '',
				month: profile.month || '',
				current_salary: profile.current_salary || '',
				expected_salary: profile.expected_salary || '',
				notice_period: profile.notice_period || '',
				relocation: profile.relocation || false
			};
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to load profile';
			toast.error(errorMessage);
			console.error('Profile load error:', err);
		} finally {
			loading = false;
		}
	}

	async function handleSaveProfile() {
		try {
			saving = true;
			validationErrors = {};

			if (!formData.first_name.trim()) {
				validationErrors.first_name = 'First name is required';
			}
			if (!formData.last_name.trim()) {
				validationErrors.last_name = 'Last name is required';
			}
			if (formData.mobile && !/^\+?[\d\s\-()]+$/.test(formData.mobile)) {
				validationErrors.mobile = 'Invalid phone number format';
			}
			if (formData.alternate_mobile && !/^\+?[\d\s\-()]+$/.test(formData.alternate_mobile)) {
				validationErrors.alternate_mobile = 'Invalid phone number format';
			}
			if (formData.pincode && !/^\d{6}$/.test(formData.pincode)) {
				validationErrors.pincode = 'PIN code must be 6 digits';
			}

			if (Object.keys(validationErrors).length > 0) {
				saving = false;
				return;
			}

			const updatePayload: Record<string, unknown> = {};

			updatePayload.first_name = formData.first_name.trim();
			updatePayload.last_name = formData.last_name.trim();

			if (formData.mobile?.trim()) updatePayload.mobile = formData.mobile.trim();
			if (formData.alternate_mobile?.trim())
				updatePayload.alternate_mobile = parseInt(formData.alternate_mobile.replace(/\D/g, ''));
			if (formData.gender) updatePayload.gender = formData.gender;
			if (formData.dob) updatePayload.dob = formData.dob;
			if (formData.marital_status) updatePayload.marital_status = formData.marital_status;
			if (formData.nationality?.trim()) updatePayload.nationality = formData.nationality.trim();
			if (formData.address?.trim()) updatePayload.address = formData.address.trim();
			if (formData.permanent_address?.trim())
				updatePayload.permanent_address = formData.permanent_address.trim();
			if (formData.pincode?.trim()) updatePayload.pincode = parseInt(formData.pincode);

			if (formData.city_id) updatePayload.city_id = formData.city_id;
			if (formData.state_id) updatePayload.state_id = formData.state_id;
			if (formData.country_id) updatePayload.country_id = formData.country_id;
			if (formData.current_city_id) updatePayload.current_city_id = formData.current_city_id;
			if (formData.preferred_city_ids && formData.preferred_city_ids.length > 0) {
				updatePayload.preferred_city_ids = formData.preferred_city_ids;
			}

			if (formData.job_role?.trim()) updatePayload.job_role = formData.job_role.trim();
			if (formData.profile_description?.trim())
				updatePayload.profile_description = formData.profile_description.trim();
			if (formData.year) updatePayload.year = formData.year;
			if (formData.month) updatePayload.month = formData.month;
			if (formData.current_salary?.trim())
				updatePayload.current_salary = formData.current_salary.trim();
			if (formData.expected_salary?.trim())
				updatePayload.expected_salary = formData.expected_salary.trim();
			if (formData.notice_period?.trim())
				updatePayload.notice_period = formData.notice_period.trim();

			updatePayload.relocation = formData.relocation;

			profile = await patchProfile(updatePayload);

			authStore.updateUser({
				...$authStore.user!,
				first_name: profile.first_name,
				last_name: profile.last_name,
				profile_completion_percentage: profile.profile_completion_percentage
			});

			toast.success('Profile updated successfully!');
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to update profile';
			toast.error(errorMessage);
			console.error('Profile update error:', err);
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Personal Information - Profile - PeelJobs</title>
	<meta name="description" content="Manage your personal information and preferences" />
</svelte:head>

<!-- Header -->
<div class="mb-6 animate-fade-in-up" style="opacity: 0;">
	<div class="flex items-center gap-3 mb-2">
		<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
			<User size={20} class="text-primary-600" />
		</div>
		<div>
			<h2 class="text-xl lg:text-2xl font-bold text-gray-900">Personal Information</h2>
			<p class="text-sm text-gray-600">Manage your personal information and preferences</p>
		</div>
	</div>
</div>

<!-- Loading State -->
{#if loading}
	<div
		class="bg-white rounded-2xl p-12 elevation-1 border border-gray-100 text-center animate-fade-in-up"
		style="opacity: 0; animation-delay: 100ms;"
	>
		<div
			class="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
		></div>
		<p class="text-gray-600">Loading your profile...</p>
	</div>
{:else if profile}
	<!-- Profile Completion Card -->
	{#if profile.profile_completion_percentage < 100}
		<div
			class="bg-white rounded-2xl p-5 lg:p-6 elevation-1 border border-gray-100 mb-6 animate-fade-in-up"
			style="opacity: 0; animation-delay: 100ms;"
		>
			<div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
				<div class="flex items-start gap-4">
					<div
						class="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center flex-shrink-0"
					>
						<Sparkles size={24} class="text-primary-600" />
					</div>
					<div>
						<h3 class="text-lg font-semibold text-gray-900 mb-1">Complete Your Profile</h3>
						<p class="text-sm text-gray-600">
							A complete profile gets 3x more views from recruiters
						</p>
					</div>
				</div>

				<div class="flex items-center gap-4 lg:gap-6">
					<div class="flex-1 lg:w-48">
						<div class="flex justify-between text-sm mb-2">
							<span class="text-gray-600">Progress</span>
							<span class="font-semibold text-primary-600"
								>{profile.profile_completion_percentage}%</span
							>
						</div>
						<div class="w-full bg-gray-100 rounded-full h-2.5">
							<div
								class="bg-primary-600 rounded-full h-2.5 transition-all duration-500"
								style="width: {profile.profile_completion_percentage}%"
							></div>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Profile Form -->
	<form
		onsubmit={(e) => {
			e.preventDefault();
			handleSaveProfile();
		}}
		class="space-y-6"
	>
		<!-- Profile Picture Section -->
		<div
			class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
			style="opacity: 0; animation-delay: 150ms;"
		>
			<ProfilePictureSection
				profilePicUrl={profile.profile_pic_url}
				photo={profile.photo}
				onUploadComplete={loadProfile}
			/>
		</div>

		<!-- Personal Information Section -->
		<div
			class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
			style="opacity: 0; animation-delay: 200ms;"
		>
			<PersonalInfoSection bind:formData email={profile.email} {validationErrors} />
		</div>

		<!-- Address Information Section -->
		<div
			class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
			style="opacity: 0; animation-delay: 250ms;"
		>
			<AddressInfoSection bind:formData {validationErrors} />
		</div>

		<!-- Location Preferences Section -->
		<div
			class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
			style="opacity: 0; animation-delay: 300ms;"
		>
			<LocationSection bind:formData {profile} />
		</div>

		<!-- Professional Information Section -->
		<div
			class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
			style="opacity: 0; animation-delay: 350ms;"
		>
			<ProfessionalInfoSection bind:formData />
		</div>

		<!-- Save Button -->
		<div
			class="flex justify-end gap-4 animate-fade-in-up"
			style="opacity: 0; animation-delay: 400ms;"
		>
			<button
				type="submit"
				disabled={saving}
				class="px-6 py-3 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 elevation-1"
			>
				{#if saving}
					<Loader size={20} class="animate-spin" />
					Saving...
				{:else}
					<Save size={20} />
					Save Profile
				{/if}
			</button>
		</div>
	</form>
{/if}

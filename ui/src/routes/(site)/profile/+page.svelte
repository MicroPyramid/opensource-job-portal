<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { toast } from '$lib/stores/toast';
	import { getProfile, patchProfile, type UserProfile } from '$lib/api/profile';
	import { Save, Loader } from '@lucide/svelte';

	// Import components
	import ProfilePictureSection from '$lib/components/profile/ProfilePictureSection.svelte';
	import PersonalInfoSection from '$lib/components/profile/PersonalInfoSection.svelte';
	import AddressInfoSection from '$lib/components/profile/AddressInfoSection.svelte';
	import LocationSection from '$lib/components/profile/LocationSection.svelte';
	import ProfessionalInfoSection from '$lib/components/profile/ProfessionalInfoSection.svelte';

	// State
	let profile: UserProfile | null = null;
	let loading = true;
	let saving = false;
	let validationErrors: Record<string, string> = {};

	// Form data
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

	// Load profile on mount
	onMount(async () => {
		await loadProfile();
	});

	async function loadProfile() {
		try {
			loading = true;
			profile = await getProfile();

			// Populate form with profile data
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

			// Validate required fields
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

			// Build update payload - only include non-empty values
			const updatePayload: any = {};

			// Always include required fields
			updatePayload.first_name = formData.first_name.trim();
			updatePayload.last_name = formData.last_name.trim();

			// Include optional fields only if they have values
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

			// Location fields
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

			// Boolean fields - always include
			updatePayload.relocation = formData.relocation;

			// Update profile
			profile = await patchProfile(updatePayload);

			// Update auth store with new user data
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

<!-- Header -->
<div class="mb-8">
	<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Personal Information</h1>
	<p class="text-gray-600 mt-2">Manage your personal information and preferences</p>
</div>

<!-- Loading State -->
{#if loading}
	<div class="bg-white rounded-lg shadow-sm p-8 text-center">
		<Loader class="w-8 h-8 animate-spin mx-auto text-blue-600" />
		<p class="mt-4 text-gray-600">Loading your profile...</p>
	</div>
{:else if profile}
	<!-- Profile Completion -->
	<div class="bg-white rounded-lg shadow-sm p-6 mb-6">
		<div class="flex items-center justify-between mb-3">
			<h2 class="text-lg font-semibold text-gray-900">Profile Completion</h2>
			<span class="text-2xl font-bold text-blue-600">
				{profile.profile_completion_percentage}%
			</span>
		</div>
		<div class="w-full bg-gray-200 rounded-full h-3">
			<div
				class="bg-blue-600 h-3 rounded-full transition-all duration-500"
				style="width: {profile.profile_completion_percentage}%"
			></div>
		</div>
		{#if profile.profile_completion_percentage < 100}
			<p class="mt-2 text-sm text-gray-600">
				Complete your profile to increase your chances of getting hired
			</p>
		{/if}
	</div>

	<!-- Profile Form -->
	<form
		onsubmit={(e) => {
			e.preventDefault();
			handleSaveProfile();
		}}
		class="space-y-6"
	>
		<!-- Profile Picture Section -->
		<ProfilePictureSection
			profilePicUrl={profile.profile_pic_url}
			photo={profile.photo}
			onUploadComplete={loadProfile}
		/>

		<!-- Personal Information Section -->
		<PersonalInfoSection bind:formData email={profile.email} {validationErrors} />

		<!-- Address Information Section -->
		<AddressInfoSection bind:formData {validationErrors} />

		<!-- Location Preferences Section -->
		<LocationSection bind:formData {profile} />

		<!-- Professional Information Section -->
		<ProfessionalInfoSection bind:formData />

		<!-- Save Button -->
		<div class="flex justify-end gap-4">
			<button
				type="submit"
				disabled={saving}
				class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
			>
				{#if saving}
					<Loader class="w-5 h-5 animate-spin" />
					Saving...
				{:else}
					<Save class="w-5 h-5" />
					Save Profile
				{/if}
			</button>
		</div>
	</form>
{/if}

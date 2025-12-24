<script lang="ts">
	import { User, Camera, Loader } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import { uploadProfilePicture } from '$lib/api/profile';

	export let profilePicUrl: string | null = null;
	export let photo: string = '';
	export let onUploadComplete: () => Promise<void>;

	let uploadingPic = false;

	async function handleProfilePicUpload(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;

		// Validate file type
		if (!file.type.startsWith('image/')) {
			toast.error('Please select an image file');
			return;
		}

		// Validate file size (5MB max)
		if (file.size > 5 * 1024 * 1024) {
			toast.error('Image size must not exceed 5MB');
			return;
		}

		try {
			uploadingPic = true;
			const response = await uploadProfilePicture(file);
			toast.success(response.message);

			// Reload profile to get updated picture URL
			await onUploadComplete();
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to upload profile picture';
			toast.error(errorMessage);
			console.error('Profile pic upload error:', err);
		} finally {
			uploadingPic = false;
		}
	}
</script>

<div class="p-5 lg:p-6">
	<div class="flex items-center gap-3 mb-6">
		<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
			<Camera size={20} class="text-primary-600" />
		</div>
		<div>
			<h2 class="text-lg font-semibold text-gray-900">Profile Picture</h2>
			<p class="text-sm text-gray-600">Your profile photo</p>
		</div>
	</div>

	<div class="flex items-center gap-5">
		<div class="relative">
			{#if profilePicUrl || photo}
				<img
					src={profilePicUrl || photo}
					alt="Profile"
					class="w-24 h-24 rounded-2xl object-cover border-2 border-gray-100 elevation-1"
				/>
			{:else}
				<div
					class="w-24 h-24 rounded-2xl bg-primary-50 flex items-center justify-center border-2 border-primary-100"
				>
					<User size={40} class="text-primary-600" />
				</div>
			{/if}
			<label
				for="profile-pic-upload"
				class="absolute -bottom-1 -right-1 bg-primary-600 text-white rounded-xl p-2 cursor-pointer hover:bg-primary-700 transition-colors elevation-1"
			>
				<Camera size={16} />
			</label>
		</div>
		<div>
			<input
				id="profile-pic-upload"
				type="file"
				accept="image/jpeg,image/jpg,image/png"
				onchange={handleProfilePicUpload}
				class="hidden"
				disabled={uploadingPic}
			/>
			<p class="text-sm text-gray-600">
				{#if uploadingPic}
					<span class="flex items-center gap-2">
						<Loader size={16} class="animate-spin text-primary-600" />
						Uploading...
					</span>
				{:else}
					JPG, JPEG or PNG (max 5MB)
				{/if}
			</p>
			<p class="mt-1 text-xs text-gray-500">Click the camera icon to upload</p>
		</div>
	</div>
</div>

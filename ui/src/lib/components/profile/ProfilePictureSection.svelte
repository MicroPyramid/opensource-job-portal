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

<div class="bg-white rounded-lg shadow-sm p-6">
	<h2 class="text-lg font-semibold text-gray-900 mb-4">Profile Picture</h2>

	<div class="flex items-center gap-4">
		<div class="relative">
			{#if profilePicUrl || photo}
				<img
					src={profilePicUrl || photo}
					alt="Profile"
					class="w-24 h-24 rounded-full object-cover border-2 border-gray-200"
				/>
			{:else}
				<div
					class="w-24 h-24 rounded-full bg-blue-100 flex items-center justify-center border-2 border-gray-200"
				>
					<User class="w-12 h-12 text-blue-600" />
				</div>
			{/if}
			<label
				for="profile-pic-upload"
				class="absolute bottom-0 right-0 bg-blue-600 text-white rounded-full p-2 cursor-pointer hover:bg-blue-700 transition-colors"
			>
				<Camera class="w-4 h-4" />
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
						<Loader class="w-4 h-4 animate-spin" />
						Uploading...
					</span>
				{:else}
					JPG, JPEG or PNG (max 5MB)
				{/if}
			</p>
		</div>
	</div>
</div>

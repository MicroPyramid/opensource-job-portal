<script lang="ts">
	import { onMount } from 'svelte';
	import { GraduationCap, Plus, BookOpen } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import { getMyEducation, deleteEducation } from '$lib/api/education';
	import type { EducationDetails } from '$lib/api/education';
	import EducationCard from '$lib/components/profile/EducationCard.svelte';
	import AddEducationModal from '$lib/components/profile/AddEducationModal.svelte';

	// State
	let educationList: EducationDetails[] = $state([]);
	let loading = $state(true);
	let isModalOpen = $state(false);
	let selectedEducation: EducationDetails | null = $state(null);

	/**
	 * Load education data on mount
	 */
	onMount(async () => {
		await loadEducation();
	});

	/**
	 * Fetch user's education details
	 */
	async function loadEducation() {
		loading = true;
		try {
			educationList = await getMyEducation();
		} catch (error) {
			console.error('Failed to load education:', error);
			toast.error('Failed to load education details');
		} finally {
			loading = false;
		}
	}

	/**
	 * Open modal to add new education
	 */
	function handleAddEducation() {
		selectedEducation = null;
		isModalOpen = true;
	}

	/**
	 * Open modal to edit education
	 */
	function handleEditEducation(education: EducationDetails) {
		selectedEducation = education;
		isModalOpen = true;
	}

	/**
	 * Delete education with confirmation
	 */
	async function handleDeleteEducation(id: number) {
		if (!confirm('Are you sure you want to delete this education entry?')) {
			return;
		}

		try {
			await deleteEducation(id);
			toast.success('Education deleted successfully!');
			await loadEducation();
		} catch (error) {
			console.error('Failed to delete education:', error);
			toast.error('Failed to delete education. Please try again.');
		}
	}

	/**
	 * Handle successful add/edit
	 */
	async function handleSuccess() {
		await loadEducation();
	}

	/**
	 * Close modal
	 */
	function handleCloseModal() {
		isModalOpen = false;
		selectedEducation = null;
	}
</script>

<svelte:head>
	<title>Education - PeelJobs</title>
</svelte:head>

<!-- Header -->
<div class="mb-6 md:mb-8">
	<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Education</h1>
	<p class="text-gray-600 mt-2">Manage your educational qualifications</p>
</div>

<!-- Add Education Button -->
<div class="mb-6">
	<button
		type="button"
		onclick={handleAddEducation}
		class="w-full md:w-auto inline-flex items-center justify-center gap-2 px-4 md:px-6 py-2.5 md:py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm md:text-base"
	>
		<Plus class="w-4 h-4 md:w-5 md:h-5" />
		<span>Add Education</span>
	</button>
</div>

		<!-- Education List -->
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="text-center">
					<div
						class="inline-block w-8 h-8 md:w-12 md:h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"
					></div>
					<p class="mt-4 text-sm md:text-base text-gray-600">Loading education details...</p>
				</div>
			</div>
		{:else if educationList.length === 0}
			<!-- Empty State -->
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 md:p-12 text-center">
				<div class="mx-auto w-16 h-16 md:w-20 md:h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
					<BookOpen class="w-8 h-8 md:w-10 md:h-10 text-gray-400" />
				</div>
				<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-2">No education added yet</h3>
				<p class="text-sm md:text-base text-gray-600 mb-6 max-w-md mx-auto">
					Add your educational qualifications to showcase your academic background to potential
					employers.
				</p>
				<button
					type="button"
					onclick={handleAddEducation}
					class="inline-flex items-center gap-2 px-4 md:px-6 py-2.5 md:py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm md:text-base"
				>
					<Plus class="w-4 h-4 md:w-5 md:h-5" />
					<span>Add Your First Education</span>
				</button>
			</div>
		{:else}
			<!-- Education Cards -->
			<div class="space-y-4 md:space-y-6">
				{#each educationList as education (education.id)}
					<EducationCard
						{education}
						onEdit={handleEditEducation}
						onDelete={handleDeleteEducation}
					/>
				{/each}
			</div>

			<!-- Summary -->
			<div class="mt-6 md:mt-8 p-4 md:p-6 bg-blue-50 border border-blue-200 rounded-lg">
				<div class="flex items-start gap-3">
					<GraduationCap class="w-5 h-5 md:w-6 md:h-6 text-blue-600 shrink-0 mt-0.5" />
					<div>
						<h3 class="text-sm md:text-base font-semibold text-gray-900 mb-1">
							{educationList.length} {educationList.length === 1
								? 'Qualification'
								: 'Qualifications'} Added
						</h3>
						<p class="text-xs md:text-sm text-gray-600">
							Keep your education details updated to improve your profile visibility and attract
							better job opportunities.
						</p>
					</div>
				</div>
			</div>
		{/if}

<!-- Add/Edit Education Modal -->
<AddEducationModal
	bind:isOpen={isModalOpen}
	onClose={handleCloseModal}
	onSuccess={handleSuccess}
	education={selectedEducation}
/>

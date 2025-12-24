<script lang="ts">
	import { onMount } from 'svelte';
	import { GraduationCap, Plus, BookOpen } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import { getMyEducation, deleteEducation } from '$lib/api/education';
	import type { EducationDetails } from '$lib/api/education';
	import EducationCard from '$lib/components/profile/EducationCard.svelte';
	import AddEducationModal from '$lib/components/profile/AddEducationModal.svelte';

	let educationList: EducationDetails[] = $state([]);
	let loading = $state(true);
	let isModalOpen = $state(false);
	let selectedEducation: EducationDetails | null = $state(null);

	onMount(async () => {
		await loadEducation();
	});

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

	function handleAddEducation() {
		selectedEducation = null;
		isModalOpen = true;
	}

	function handleEditEducation(education: EducationDetails) {
		selectedEducation = education;
		isModalOpen = true;
	}

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

	async function handleSuccess() {
		await loadEducation();
	}

	function handleCloseModal() {
		isModalOpen = false;
		selectedEducation = null;
	}
</script>

<svelte:head>
	<title>Education - Profile - PeelJobs</title>
	<meta name="description" content="Manage your educational qualifications" />
</svelte:head>

<!-- Header -->
<div class="mb-6 animate-fade-in-up" style="opacity: 0;">
	<div class="flex items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
				<GraduationCap size={20} class="text-primary-600" />
			</div>
			<div>
				<h2 class="text-xl lg:text-2xl font-bold text-gray-900">Education</h2>
				<p class="text-sm text-gray-600">Manage your educational qualifications</p>
			</div>
		</div>
		<button
			type="button"
			onclick={handleAddEducation}
			class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors elevation-1 text-sm"
		>
			<Plus size={18} />
			<span class="hidden sm:inline">Add Education</span>
		</button>
	</div>
</div>

<!-- Education List -->
{#if loading}
	<div
		class="bg-white rounded-2xl p-12 elevation-1 border border-gray-100 text-center animate-fade-in-up"
		style="opacity: 0; animation-delay: 100ms;"
	>
		<div
			class="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
		></div>
		<p class="text-gray-600">Loading education details...</p>
	</div>
{:else if educationList.length === 0}
	<!-- Empty State -->
	<div
		class="bg-white rounded-2xl p-12 elevation-1 border border-gray-100 text-center animate-fade-in-up"
		style="opacity: 0; animation-delay: 100ms;"
	>
		<div
			class="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-6"
		>
			<BookOpen size={36} class="text-gray-400" />
		</div>
		<h3 class="text-xl font-semibold text-gray-900 mb-2">No education added yet</h3>
		<p class="text-gray-600 mb-6 max-w-md mx-auto">
			Add your educational qualifications to showcase your academic background to potential
			employers.
		</p>
		<button
			type="button"
			onclick={handleAddEducation}
			class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors elevation-1"
		>
			<Plus size={18} />
			<span>Add Your First Education</span>
		</button>
	</div>
{:else}
	<!-- Education Cards -->
	<div class="space-y-4">
		{#each educationList as education, i (education.id)}
			<div
				class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
				style="opacity: 0; animation-delay: {(i + 1) * 50 + 100}ms;"
			>
				<EducationCard {education} onEdit={handleEditEducation} onDelete={handleDeleteEducation} />
			</div>
		{/each}
	</div>

	<!-- Summary -->
	<div
		class="mt-6 p-5 lg:p-6 bg-primary-50 border border-primary-100 rounded-2xl animate-fade-in-up"
		style="opacity: 0; animation-delay: 400ms;"
	>
		<div class="flex items-start gap-4">
			<div
				class="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center flex-shrink-0"
			>
				<GraduationCap size={22} class="text-primary-600" />
			</div>
			<div>
				<h3 class="font-semibold text-gray-900 mb-1">
					{educationList.length}
					{educationList.length === 1 ? 'Qualification' : 'Qualifications'} Added
				</h3>
				<p class="text-sm text-gray-600">
					Keep your education details updated to improve your profile visibility and attract better
					job opportunities.
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

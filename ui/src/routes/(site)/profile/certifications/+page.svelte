<script lang="ts">
	import { onMount } from 'svelte';
	import { Award, Plus, FileText } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import { getMyCertifications, deleteCertification } from '$lib/api/certifications';
	import type { Certification } from '$lib/api/certifications';
	import CertificationCard from '$lib/components/profile/CertificationCard.svelte';
	import AddCertificationModal from '$lib/components/profile/AddCertificationModal.svelte';

	let certificationList: Certification[] = $state([]);
	let loading = $state(true);
	let isModalOpen = $state(false);
	let selectedCertification: Certification | null = $state(null);

	onMount(async () => {
		await loadCertifications();
	});

	async function loadCertifications() {
		loading = true;
		try {
			certificationList = await getMyCertifications();
		} catch (error) {
			console.error('Failed to load certifications:', error);
			toast.error('Failed to load certifications');
		} finally {
			loading = false;
		}
	}

	function handleAddCertification() {
		selectedCertification = null;
		isModalOpen = true;
	}

	function handleEditCertification(certification: Certification) {
		selectedCertification = certification;
		isModalOpen = true;
	}

	async function handleDeleteCertification(id: number) {
		if (!confirm('Are you sure you want to delete this certification?')) {
			return;
		}

		try {
			await deleteCertification(id);
			toast.success('Certification deleted successfully!');
			await loadCertifications();
		} catch (error) {
			console.error('Failed to delete certification:', error);
			toast.error('Failed to delete certification');
		}
	}

	async function handleSuccess() {
		await loadCertifications();
	}

	function handleCloseModal() {
		isModalOpen = false;
		selectedCertification = null;
	}
</script>

<svelte:head>
	<title>Certifications - PeelJobs</title>
</svelte:head>


	
		<div class="mb-6 md:mb-8">
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 md:p-3 bg-blue-600 rounded-lg">
					<Award class="w-6 h-6 md:w-8 md:h-8 text-white" />
				</div>
				<div>
					<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Certifications</h1>
					<p class="text-sm md:text-base text-gray-600 mt-1">Manage your professional certifications</p>
				</div>
			</div>
		</div>

		<div class="mb-6">
			<button
				type="button"
				onclick={handleAddCertification}
				class="w-full md:w-auto inline-flex items-center justify-center gap-2 px-4 md:px-6 py-2.5 md:py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm md:text-base"
			>
				<Plus class="w-4 h-4 md:w-5 md:h-5" />
				<span>Add Certification</span>
			</button>
		</div>

		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="text-center">
					<div class="inline-block w-8 h-8 md:w-12 md:h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
					<p class="mt-4 text-sm md:text-base text-gray-600">Loading certifications...</p>
				</div>
			</div>
		{:else if certificationList.length === 0}
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 md:p-12 text-center">
				<div class="mx-auto w-16 h-16 md:w-20 md:h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
					<FileText class="w-8 h-8 md:w-10 md:h-10 text-gray-400" />
				</div>
				<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-2">No certifications added yet</h3>
				<p class="text-sm md:text-base text-gray-600 mb-6 max-w-md mx-auto">
					Add your professional certifications to stand out to recruiters and demonstrate your expertise.
				</p>
				<button
					type="button"
					onclick={handleAddCertification}
					class="inline-flex items-center gap-2 px-4 md:px-6 py-2.5 md:py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm md:text-base"
				>
					<Plus class="w-4 h-4 md:w-5 md:h-5" />
					<span>Add Your First Certification</span>
				</button>
			</div>
		{:else}
			<div class="space-y-4 md:space-y-6">
				{#each certificationList as certification (certification.id)}
					<CertificationCard {certification} onEdit={handleEditCertification} onDelete={handleDeleteCertification} />
				{/each}
			</div>

			<div class="mt-6 md:mt-8 p-4 md:p-6 bg-blue-50 border border-blue-200 rounded-lg">
				<div class="flex items-start gap-3">
					<Award class="w-5 h-5 md:w-6 md:h-6 text-blue-600 shrink-0 mt-0.5" />
					<div>
						<h3 class="text-sm md:text-base font-semibold text-gray-900 mb-1">
							{certificationList.length} {certificationList.length === 1 ? 'Certification' : 'Certifications'} Added
						</h3>
						<p class="text-xs md:text-sm text-gray-600">
							Professional certifications validate your skills and make your profile more attractive to employers.
						</p>
					</div>
				</div>
			</div>
		{/if}

<AddCertificationModal
	bind:isOpen={isModalOpen}
	onClose={handleCloseModal}
	onSuccess={handleSuccess}
	certification={selectedCertification}
/>

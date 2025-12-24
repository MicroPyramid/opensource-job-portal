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
	<title>Certifications - Profile - PeelJobs</title>
	<meta name="description" content="Manage your professional certifications" />
</svelte:head>

<!-- Header -->
<div class="mb-6 animate-fade-in-up" style="opacity: 0;">
	<div class="flex items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
				<Award size={20} class="text-primary-600" />
			</div>
			<div>
				<h2 class="text-xl lg:text-2xl font-bold text-gray-900">Certifications</h2>
				<p class="text-sm text-gray-600">Manage your professional certifications</p>
			</div>
		</div>
		<button
			type="button"
			onclick={handleAddCertification}
			class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors elevation-1 text-sm"
		>
			<Plus size={18} />
			<span class="hidden sm:inline">Add Certification</span>
		</button>
	</div>
</div>

<!-- Certification List -->
{#if loading}
	<div
		class="bg-white rounded-2xl p-12 elevation-1 border border-gray-100 text-center animate-fade-in-up"
		style="opacity: 0; animation-delay: 100ms;"
	>
		<div
			class="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"
		></div>
		<p class="text-gray-600">Loading certifications...</p>
	</div>
{:else if certificationList.length === 0}
	<!-- Empty State -->
	<div
		class="bg-white rounded-2xl p-12 elevation-1 border border-gray-100 text-center animate-fade-in-up"
		style="opacity: 0; animation-delay: 100ms;"
	>
		<div
			class="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-6"
		>
			<FileText size={36} class="text-gray-400" />
		</div>
		<h3 class="text-xl font-semibold text-gray-900 mb-2">No certifications added yet</h3>
		<p class="text-gray-600 mb-6 max-w-md mx-auto">
			Add your professional certifications to stand out to recruiters and demonstrate your
			expertise.
		</p>
		<button
			type="button"
			onclick={handleAddCertification}
			class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors elevation-1"
		>
			<Plus size={18} />
			<span>Add Your First Certification</span>
		</button>
	</div>
{:else}
	<!-- Certification Cards -->
	<div class="space-y-4">
		{#each certificationList as certification, i (certification.id)}
			<div
				class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
				style="opacity: 0; animation-delay: {(i + 1) * 50 + 100}ms;"
			>
				<CertificationCard
					{certification}
					onEdit={handleEditCertification}
					onDelete={handleDeleteCertification}
				/>
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
				<Award size={22} class="text-primary-600" />
			</div>
			<div>
				<h3 class="font-semibold text-gray-900 mb-1">
					{certificationList.length}
					{certificationList.length === 1 ? 'Certification' : 'Certifications'} Added
				</h3>
				<p class="text-sm text-gray-600">
					Professional certifications validate your skills and make your profile more attractive to
					employers.
				</p>
			</div>
		</div>
	</div>
{/if}

<!-- Add/Edit Certification Modal -->
<AddCertificationModal
	bind:isOpen={isModalOpen}
	onClose={handleCloseModal}
	onSuccess={handleSuccess}
	certification={selectedCertification}
/>

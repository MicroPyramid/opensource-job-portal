<script lang="ts">
	import { X, Award } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import type { Certification, CertificationCreateUpdate } from '$lib/api/certifications';
	import { addCertification, updateCertification } from '$lib/api/certifications';

	interface Props {
		isOpen: boolean;
		onClose: () => void;
		onSuccess: () => void;
		certification?: Certification | null;
	}

	let { isOpen = $bindable(), onClose, onSuccess, certification = null }: Props = $props();

	let formData = $state<CertificationCreateUpdate>({
		name: '',
		organization: '',
		credential_id: '',
		credential_url: '',
		issued_date: '',
		expiry_date: '',
		does_not_expire: false,
		description: ''
	});

	let loading = $state(false);

	$effect(() => {
		if (isOpen && certification) {
			formData = {
				name: certification.name,
				organization: certification.organization,
				credential_id: certification.credential_id || '',
				credential_url: certification.credential_url || '',
				issued_date: certification.issued_date || '',
				expiry_date: certification.expiry_date || '',
				does_not_expire: certification.does_not_expire,
				description: certification.description || ''
			};
		} else if (isOpen) {
			formData = {
				name: '',
				organization: '',
				credential_id: '',
				credential_url: '',
				issued_date: '',
				expiry_date: '',
				does_not_expire: false,
				description: ''
			};
		}
	});

	$effect(() => {
		if (formData.does_not_expire) {
			formData.expiry_date = '';
		}
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();

		if (!formData.name.trim()) {
			toast.error('Please enter certification name');
			return;
		}

		if (!formData.organization.trim()) {
			toast.error('Please enter issuing organization');
			return;
		}

		loading = true;

		try {
			const submitData: CertificationCreateUpdate = {
				name: formData.name,
				organization: formData.organization,
				does_not_expire: formData.does_not_expire,
				credential_id: formData.credential_id || undefined,
				credential_url: formData.credential_url || undefined,
				issued_date: formData.issued_date || undefined,
				expiry_date: formData.expiry_date || undefined,
				description: formData.description || undefined
			};

			if (certification) {
				await updateCertification(certification.id, submitData);
				toast.success('Certification updated successfully!');
			} else {
				await addCertification(submitData);
				toast.success('Certification added successfully!');
			}

			onSuccess();
			handleClose();
		} catch (error: any) {
			console.error('Failed to save certification:', error);
			toast.error(error?.response?.data?.detail || 'Failed to save certification');
		} finally {
			loading = false;
		}
	}

	function handleClose() {
		onClose();
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			handleClose();
		}
	}
</script>

{#if isOpen}
	<div class="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true">
		<button
			type="button"
			class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity cursor-default"
			onclick={handleBackdropClick}
			aria-label="Close modal"
			tabindex="-1"
		></button>

		<div class="flex min-h-screen items-center justify-center p-4">
			<div class="relative w-full max-w-2xl transform overflow-hidden rounded-lg bg-white shadow-xl">
				<div class="flex items-center justify-between border-b border-gray-200 px-4 md:px-6 py-4">
					<div class="flex items-center gap-3">
						<div class="p-2 bg-blue-50 rounded-lg">
							<Award class="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
						</div>
						<h3 class="text-lg md:text-xl font-semibold text-gray-900">
							{certification ? 'Edit Certification' : 'Add Certification'}
						</h3>
					</div>
					<button type="button" onclick={handleClose} class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100">
						<X class="w-5 h-5 md:w-6 md:h-6" />
					</button>
				</div>

				<form onsubmit={handleSubmit} class="px-4 md:px-6 py-4 md:py-6 space-y-4">
					<div>
						<label for="name" class="block text-sm font-medium text-gray-700 mb-1">
							Certification Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="name"
							bind:value={formData.name}
							placeholder="e.g., AWS Certified Solutions Architect"
							class="w-full px-3 md:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm md:text-base"
							required
						/>
					</div>

					<div>
						<label for="organization" class="block text-sm font-medium text-gray-700 mb-1">
							Issuing Organization <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="organization"
							bind:value={formData.organization}
							placeholder="e.g., Amazon Web Services"
							class="w-full px-3 md:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm md:text-base"
							required
						/>
					</div>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="credential_id" class="block text-sm font-medium text-gray-700 mb-1">Credential ID</label>
							<input
								type="text"
								id="credential_id"
								bind:value={formData.credential_id}
								placeholder="e.g., AWS-CSA-12345"
								class="w-full px-3 md:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm md:text-base"
							/>
						</div>

						<div>
							<label for="credential_url" class="block text-sm font-medium text-gray-700 mb-1">Credential URL</label>
							<input
								type="url"
								id="credential_url"
								bind:value={formData.credential_url}
								placeholder="https://..."
								class="w-full px-3 md:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm md:text-base"
							/>
						</div>
					</div>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="issued_date" class="block text-sm font-medium text-gray-700 mb-1">Issued Date</label>
							<input
								type="date"
								id="issued_date"
								bind:value={formData.issued_date}
								class="w-full px-3 md:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm md:text-base"
							/>
						</div>

						<div>
							<label for="expiry_date" class="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
							<input
								type="date"
								id="expiry_date"
								bind:value={formData.expiry_date}
								disabled={formData.does_not_expire}
								class="w-full px-3 md:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 text-sm md:text-base"
							/>
						</div>
					</div>

					<div class="flex items-center gap-2">
						<input
							type="checkbox"
							id="does_not_expire"
							bind:checked={formData.does_not_expire}
							class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
						/>
						<label for="does_not_expire" class="text-sm font-medium text-gray-700">
							This certification does not expire
						</label>
					</div>

					<div>
						<label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
						<textarea
							id="description"
							bind:value={formData.description}
							placeholder="Additional details about this certification..."
							rows="3"
							class="w-full px-3 md:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm md:text-base resize-none"
						></textarea>
					</div>

					<div class="flex flex-col-reverse md:flex-row gap-3 pt-4">
						<button
							type="button"
							onclick={handleClose}
							class="w-full md:w-auto px-4 md:px-6 py-2 border border-gray-300 rounded-lg text-sm md:text-base font-medium text-gray-700 hover:bg-gray-50"
							disabled={loading}
						>
							Cancel
						</button>
						<button
							type="submit"
							class="w-full md:flex-1 px-4 md:px-6 py-2 bg-blue-600 text-white rounded-lg text-sm md:text-base font-medium hover:bg-blue-700 disabled:bg-blue-400"
							disabled={loading}
						>
							{loading ? 'Saving...' : certification ? 'Update Certification' : 'Add Certification'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

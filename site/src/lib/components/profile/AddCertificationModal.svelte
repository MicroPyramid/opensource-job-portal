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
	<div class="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true" aria-labelledby="modal-title">
		<button
			type="button"
			class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity cursor-default animate-fade-in"
			onclick={handleBackdropClick}
			aria-label="Close modal"
			tabindex="-1"
		></button>

		<div class="flex min-h-screen items-center justify-center p-4">
			<div class="relative w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white elevation-4 transition-all animate-scale-in">
				<div class="flex items-center justify-between border-b border-gray-100 p-5 lg:p-6">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
							<Award size={20} class="text-primary-600" />
						</div>
						<h3 class="text-lg font-semibold text-gray-900" id="modal-title">
							{certification ? 'Edit Certification' : 'Add Certification'}
						</h3>
					</div>
					<button type="button" onclick={handleClose} class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">
						<X size={20} />
					</button>
				</div>

				<form onsubmit={handleSubmit} class="p-5 lg:p-6 space-y-5">
					<div>
						<label for="name" class="block text-sm font-medium text-gray-700 mb-2">
							Certification Name <span class="text-error-500">*</span>
						</label>
						<input
							type="text"
							id="name"
							bind:value={formData.name}
							placeholder="e.g., AWS Certified Solutions Architect"
							class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
							required
						/>
					</div>

					<div>
						<label for="organization" class="block text-sm font-medium text-gray-700 mb-2">
							Issuing Organization <span class="text-error-500">*</span>
						</label>
						<input
							type="text"
							id="organization"
							bind:value={formData.organization}
							placeholder="e.g., Amazon Web Services"
							class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
							required
						/>
					</div>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="credential_id" class="block text-sm font-medium text-gray-700 mb-2">Credential ID</label>
							<input
								type="text"
								id="credential_id"
								bind:value={formData.credential_id}
								placeholder="e.g., AWS-CSA-12345"
								class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
							/>
						</div>

						<div>
							<label for="credential_url" class="block text-sm font-medium text-gray-700 mb-2">Credential URL</label>
							<input
								type="url"
								id="credential_url"
								bind:value={formData.credential_url}
								placeholder="https://..."
								class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
							/>
						</div>
					</div>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="issued_date" class="block text-sm font-medium text-gray-700 mb-2">Issued Date</label>
							<input
								type="date"
								id="issued_date"
								bind:value={formData.issued_date}
								class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
							/>
						</div>

						<div>
							<label for="expiry_date" class="block text-sm font-medium text-gray-700 mb-2">Expiry Date</label>
							<input
								type="date"
								id="expiry_date"
								bind:value={formData.expiry_date}
								disabled={formData.does_not_expire}
								class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
							/>
						</div>
					</div>

					<div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
						<label class="flex items-start gap-3 cursor-pointer">
							<input
								type="checkbox"
								id="does_not_expire"
								bind:checked={formData.does_not_expire}
								class="w-5 h-5 mt-0.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
							/>
							<div>
								<p class="font-medium text-gray-900">Does not expire</p>
								<p class="text-sm text-gray-600">Check this if the certification has no expiry date</p>
							</div>
						</label>
					</div>

					<div>
						<label for="description" class="block text-sm font-medium text-gray-700 mb-2">Description</label>
						<textarea
							id="description"
							bind:value={formData.description}
							placeholder="Additional details about this certification..."
							rows="3"
							class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none resize-none"
						></textarea>
					</div>

					<div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
						<button
							type="button"
							onclick={handleClose}
							class="px-5 py-2.5 text-gray-700 bg-white border border-gray-200 rounded-full font-medium hover:bg-gray-50 transition-colors"
							disabled={loading}
						>
							Cancel
						</button>
						<button
							type="submit"
							class="px-5 py-2.5 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed elevation-1"
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

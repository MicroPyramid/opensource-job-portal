<script lang="ts">
	import { Pencil, Trash2, Award, Calendar, ExternalLink, CheckCircle, AlertCircle } from '@lucide/svelte';
	import type { Certification } from '$lib/api/certifications';

	interface Props {
		certification: Certification;
		onEdit: (certification: Certification) => void;
		onDelete: (id: number) => void;
	}

	let { certification, onEdit, onDelete }: Props = $props();

	function formatDate(dateString?: string): string {
		if (!dateString) return '';
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
	}

	function isExpired(): boolean {
		if (certification.does_not_expire || !certification.expiry_date) return false;
		return new Date(certification.expiry_date) < new Date();
	}
</script>

<div class="p-5">
	<div class="flex items-start justify-between gap-4">
		<div class="flex-1 min-w-0">
			<div class="flex items-start gap-3 mb-3">
				<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
					<Award size={20} class="text-primary-600" />
				</div>
				<div class="flex-1 min-w-0">
					<h3 class="text-base md:text-lg font-semibold text-gray-900 break-words">
						{certification.name}
					</h3>
					<p class="text-sm text-gray-600 mt-0.5">{certification.organization}</p>
				</div>
			</div>

			{#if certification.description}
				<p class="text-sm text-gray-700 mb-3 pl-0 md:pl-13 break-words">{certification.description}</p>
			{/if}

			<div class="space-y-3 pl-0 md:pl-13">
				{#if certification.credential_id}
					<div class="text-xs md:text-sm text-gray-600">
						<span class="font-medium">ID:</span> {certification.credential_id}
					</div>
				{/if}

				{#if certification.issued_date || certification.expiry_date}
					<div class="flex flex-wrap items-center gap-2 md:gap-4 text-xs md:text-sm text-gray-600">
						<div class="flex items-center gap-1.5">
							<Calendar size={14} class="text-gray-400" />
							<span>
								{#if certification.issued_date}Issued {formatDate(certification.issued_date)}{/if}
								{#if certification.expiry_date && !certification.does_not_expire}
									- Expires {formatDate(certification.expiry_date)}
								{/if}
							</span>
						</div>
					</div>
				{/if}

				<div class="flex flex-wrap items-center gap-2">
					{#if certification.does_not_expire}
						<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-success-50 text-success-700 border border-success-200">
							<CheckCircle size={14} />
							No Expiration
						</span>
					{:else if isExpired()}
						<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-error-50 text-error-700 border border-error-200">
							<AlertCircle size={14} />
							Expired
						</span>
					{:else if certification.expiry_date}
						<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-primary-50 text-primary-700 border border-primary-200">
							<CheckCircle size={14} />
							Valid
						</span>
					{/if}

					{#if certification.credential_url}
						<a
							href={certification.credential_url}
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100 transition-colors"
						>
							<ExternalLink size={14} />
							Verify
						</a>
					{/if}
				</div>
			</div>
		</div>

		<div class="flex flex-col md:flex-row gap-1 shrink-0">
			<button
				type="button"
				onclick={() => onEdit(certification)}
				class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-colors"
				aria-label="Edit certification"
			>
				<Pencil size={16} />
			</button>
			<button
				type="button"
				onclick={() => onDelete(certification.id)}
				class="p-2 text-gray-400 hover:text-error-600 hover:bg-error-50 rounded-xl transition-colors"
				aria-label="Delete certification"
			>
				<Trash2 size={16} />
			</button>
		</div>
	</div>
</div>

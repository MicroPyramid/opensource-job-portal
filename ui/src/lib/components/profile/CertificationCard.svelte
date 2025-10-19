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

<div class="bg-white border border-gray-200 rounded-lg p-4 md:p-6 hover:shadow-md transition-shadow">
	<div class="flex items-start justify-between gap-4">
		<div class="flex-1 min-w-0">
			<div class="flex items-start gap-3 mb-3">
				<div class="p-2 bg-blue-50 rounded-lg shrink-0">
					<Award class="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
				</div>
				<div class="flex-1 min-w-0">
					<h3 class="text-base md:text-lg font-semibold text-gray-900 break-words">
						{certification.name}
					</h3>
					<p class="text-sm md:text-base text-gray-600 mt-1">{certification.organization}</p>
				</div>
			</div>

			{#if certification.description}
				<p class="text-sm md:text-base text-gray-700 mb-3 pl-0 md:pl-11 break-words">{certification.description}</p>
			{/if}

			<div class="space-y-2 pl-0 md:pl-11">
				{#if certification.credential_id}
					<div class="text-xs md:text-sm text-gray-600">
						<span class="font-medium">ID:</span> {certification.credential_id}
					</div>
				{/if}

				{#if certification.issued_date || certification.expiry_date}
					<div class="flex flex-wrap items-center gap-2 md:gap-4 text-xs md:text-sm text-gray-600">
						<div class="flex items-center gap-1.5">
							<Calendar class="w-3.5 h-3.5 md:w-4 md:h-4" />
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
						<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
							<CheckCircle class="w-3.5 h-3.5" />
							No Expiration
						</span>
					{:else if isExpired()}
						<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">
							<AlertCircle class="w-3.5 h-3.5" />
							Expired
						</span>
					{:else if certification.expiry_date}
						<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
							<CheckCircle class="w-3.5 h-3.5" />
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
							<ExternalLink class="w-3.5 h-3.5" />
							Verify
						</a>
					{/if}
				</div>
			</div>
		</div>

		<div class="flex flex-col md:flex-row gap-2 shrink-0">
			<button
				type="button"
				onclick={() => onEdit(certification)}
				class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
				aria-label="Edit certification"
			>
				<Pencil class="w-4 h-4 md:w-5 md:h-5" />
			</button>
			<button
				type="button"
				onclick={() => onDelete(certification.id)}
				class="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
				aria-label="Delete certification"
			>
				<Trash2 class="w-4 h-4 md:w-5 md:h-5" />
			</button>
		</div>
	</div>
</div>

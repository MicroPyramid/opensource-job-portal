<script lang="ts">
	import { Pencil, Trash2, GraduationCap, Calendar, Award } from '@lucide/svelte';
	import type { EducationDetails } from '$lib/api/education';

	interface Props {
		education: EducationDetails;
		onEdit: (education: EducationDetails) => void;
		onDelete: (id: number) => void;
	}

	let { education, onEdit, onDelete }: Props = $props();

	/**
	 * Format date to readable format
	 */
	function formatDate(dateString?: string): string {
		if (!dateString) return '';
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
	}

	/**
	 * Calculate duration between from and to dates
	 */
	function calculateDuration(): string {
		const fromDate = new Date(education.from_date);
		const toDate = education.to_date ? new Date(education.to_date) : new Date();

		const months =
			(toDate.getFullYear() - fromDate.getFullYear()) * 12 +
			(toDate.getMonth() - fromDate.getMonth());

		const years = Math.floor(months / 12);
		const remainingMonths = months % 12;

		if (years > 0 && remainingMonths > 0) {
			return `${years} year${years > 1 ? 's' : ''} ${remainingMonths} month${remainingMonths > 1 ? 's' : ''}`;
		} else if (years > 0) {
			return `${years} year${years > 1 ? 's' : ''}`;
		} else {
			return `${remainingMonths} month${remainingMonths > 1 ? 's' : ''}`;
		}
	}
</script>

<div class="p-5">
	<div class="flex items-start justify-between gap-4">
		<div class="flex-1 min-w-0">
			<!-- Degree and Specialization -->
			<div class="flex items-start gap-3 mb-3">
				<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
					<GraduationCap size={20} class="text-primary-600" />
				</div>
				<div class="flex-1 min-w-0">
					<h3 class="text-base md:text-lg font-semibold text-gray-900 break-words">
						{education.degree_name}
					</h3>
					{#if education.specialization}
						<p class="text-sm text-gray-600 break-words mt-0.5">
							{education.specialization}
						</p>
					{/if}
					{#if education.degree_type}
						<span
							class="inline-block mt-2 px-2.5 py-1 text-xs font-medium rounded-full border {education.degree_type === 'Permanent'
								? 'bg-success-50 text-success-700 border-success-200'
								: 'bg-warning-50 text-warning-700 border-warning-200'}"
						>
							{education.degree_type}
						</span>
					{/if}
				</div>
			</div>

			<!-- Institute -->
			<div class="mt-4 mb-3 pl-0 md:pl-13">
				<p class="text-sm md:text-base font-medium text-gray-700 break-words">
					{education.institute_name}
				</p>
				{#if education.institute_address}
					<p class="text-xs md:text-sm text-gray-500 mt-1 break-words">
						{education.institute_address}
					</p>
				{/if}
			</div>

			<!-- Date Range and Duration -->
			<div class="flex flex-wrap items-center gap-2 md:gap-4 text-xs md:text-sm text-gray-600 pl-0 md:pl-13">
				<div class="flex items-center gap-1.5">
					<Calendar size={14} class="text-gray-400" />
					<span>
						{formatDate(education.from_date)} - {education.current_education
							? 'Present'
							: formatDate(education.to_date)}
					</span>
				</div>
				<span class="hidden md:inline text-gray-300">•</span>
				<div class="w-full md:w-auto text-gray-500">
					{calculateDuration()}
				</div>
			</div>

			<!-- Score -->
			{#if education.score}
				<div class="mt-3 flex items-center gap-1.5 text-xs md:text-sm text-gray-600 pl-0 md:pl-13">
					<Award size={14} class="text-gray-400" />
					<span>Score: <span class="font-medium text-gray-900">{education.score}</span></span>
				</div>
			{/if}

			<!-- Current Education Badge -->
			{#if education.current_education}
				<div class="mt-3 pl-0 md:pl-13">
					<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-primary-50 text-primary-700 border border-primary-200">
						Currently Pursuing
					</span>
				</div>
			{/if}
		</div>

		<!-- Action Buttons -->
		<div class="flex flex-col md:flex-row gap-1 shrink-0">
			<button
				type="button"
				onclick={() => onEdit(education)}
				class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-colors"
				aria-label="Edit education"
			>
				<Pencil size={16} />
			</button>
			<button
				type="button"
				onclick={() => onDelete(education.id)}
				class="p-2 text-gray-400 hover:text-error-600 hover:bg-error-50 rounded-xl transition-colors"
				aria-label="Delete education"
			>
				<Trash2 size={16} />
			</button>
		</div>
	</div>
</div>

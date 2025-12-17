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

<div
	class="bg-white border border-gray-200 rounded-lg p-4 md:p-6 hover:shadow-md transition-shadow"
>
	<div class="flex items-start justify-between gap-4">
		<div class="flex-1 min-w-0">
			<!-- Degree and Specialization -->
			<div class="flex items-start gap-3 mb-2">
				<div class="p-2 bg-blue-50 rounded-lg shrink-0">
					<GraduationCap class="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
				</div>
				<div class="flex-1 min-w-0">
					<h3 class="text-base md:text-lg font-semibold text-gray-900 break-words">
						{education.degree_name}
					</h3>
					{#if education.specialization}
						<p class="text-sm md:text-base text-gray-600 break-words">
							{education.specialization}
						</p>
					{/if}
					{#if education.degree_type}
						<span
							class="inline-block mt-1 px-2 py-0.5 text-xs font-medium rounded-full {education.degree_type ===
							'Permanent'
								? 'bg-green-100 text-green-800'
								: 'bg-orange-100 text-orange-800'}"
						>
							{education.degree_type}
						</span>
					{/if}
				</div>
			</div>

			<!-- Institute -->
			<div class="mt-3 mb-3 pl-0 md:pl-11">
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
			<div class="flex flex-wrap items-center gap-2 md:gap-4 text-xs md:text-sm text-gray-600 pl-0 md:pl-11">
				<div class="flex items-center gap-1.5">
					<Calendar class="w-3.5 h-3.5 md:w-4 md:h-4" />
					<span>
						{formatDate(education.from_date)} - {education.current_education
							? 'Present'
							: formatDate(education.to_date)}
					</span>
				</div>
				<span class="hidden md:inline text-gray-400">•</span>
				<div class="w-full md:w-auto text-gray-500">
					{calculateDuration()}
				</div>
			</div>

			<!-- Score -->
			{#if education.score}
				<div class="mt-3 flex items-center gap-1.5 text-xs md:text-sm text-gray-600 pl-0 md:pl-11">
					<Award class="w-3.5 h-3.5 md:w-4 md:h-4" />
					<span>Score: <span class="font-medium text-gray-900">{education.score}</span></span>
				</div>
			{/if}

			<!-- Current Education Badge -->
			{#if education.current_education}
				<div class="mt-3 pl-0 md:pl-11">
					<span
						class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
					>
						Currently Pursuing
					</span>
				</div>
			{/if}
		</div>

		<!-- Action Buttons -->
		<div class="flex flex-col md:flex-row gap-2 shrink-0">
			<button
				type="button"
				onclick={() => onEdit(education)}
				class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
				aria-label="Edit education"
			>
				<Pencil class="w-4 h-4 md:w-5 md:h-5" />
			</button>
			<button
				type="button"
				onclick={() => onDelete(education.id)}
				class="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
				aria-label="Delete education"
			>
				<Trash2 class="w-4 h-4 md:w-5 md:h-5" />
			</button>
		</div>
	</div>
</div>

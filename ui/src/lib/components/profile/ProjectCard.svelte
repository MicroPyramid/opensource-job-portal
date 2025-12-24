<script lang="ts">
	import { Pencil, Trash2, Rocket, Calendar, MapPin, Users, Briefcase } from '@lucide/svelte';
	import type { Project } from '$lib/api/projects';

	interface Props {
		project: Project;
		onEdit: (project: Project) => void;
		onDelete: (id: number) => void;
	}

	let { project, onEdit, onDelete }: Props = $props();

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
	function calculateDuration(): string | null {
		if (!project.from_date) return null;

		const fromDate = new Date(project.from_date);
		const toDate = project.to_date ? new Date(project.to_date) : new Date();

		const months =
			(toDate.getFullYear() - fromDate.getFullYear()) * 12 +
			(toDate.getMonth() - fromDate.getMonth());

		const years = Math.floor(months / 12);
		const remainingMonths = months % 12;

		if (years > 0 && remainingMonths > 0) {
			return `${years} year${years > 1 ? 's' : ''} ${remainingMonths} month${remainingMonths > 1 ? 's' : ''}`;
		} else if (years > 0) {
			return `${years} year${years > 1 ? 's' : ''}`;
		} else if (months > 0) {
			return `${remainingMonths} month${remainingMonths > 1 ? 's' : ''}`;
		}
		return null;
	}
</script>

<div class="p-5">
	<div class="flex items-start justify-between gap-4">
		<div class="flex-1 min-w-0">
			<!-- Project Name -->
			<div class="flex items-start gap-3 mb-3">
				<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
					<Rocket size={20} class="text-primary-600" />
				</div>
				<div class="flex-1 min-w-0">
					<h3 class="text-base md:text-lg font-semibold text-gray-900 break-words">
						{project.name}
					</h3>
				</div>
			</div>

			<!-- Description -->
			<div class="mb-4 pl-0 md:pl-13">
				<p class="text-sm text-gray-700 leading-relaxed break-words">
					{project.description}
				</p>
			</div>

			<!-- Project Details Grid -->
			<div class="space-y-3 pl-0 md:pl-13">
				<!-- Role and Team Size -->
				<div class="flex flex-wrap items-center gap-3 md:gap-4 text-xs md:text-sm">
					{#if project.role}
						<div class="flex items-center gap-1.5 text-gray-600">
							<Briefcase size={14} class="text-gray-400" />
							<span class="font-medium">{project.role}</span>
						</div>
					{/if}

					{#if project.size}
						<div class="flex items-center gap-1.5 text-gray-600">
							<Users size={14} class="text-gray-400" />
							<span>Team of {project.size}</span>
						</div>
					{/if}
				</div>

				<!-- Date Range and Duration -->
				{#if project.from_date}
					<div class="flex flex-wrap items-center gap-2 md:gap-4 text-xs md:text-sm text-gray-600">
						<div class="flex items-center gap-1.5">
							<Calendar size={14} class="text-gray-400" />
							<span>
								{formatDate(project.from_date)} - {project.to_date
									? formatDate(project.to_date)
									: 'Present'}
							</span>
						</div>
						{#if calculateDuration()}
							<span class="hidden md:inline text-gray-300">•</span>
							<div class="w-full md:w-auto text-gray-500">
								{calculateDuration()}
							</div>
						{/if}
					</div>
				{/if}

				<!-- Location -->
				{#if project.location}
					<div class="flex items-center gap-1.5 text-xs md:text-sm text-gray-600">
						<MapPin size={14} class="text-gray-400" />
						<span>{project.location.name}</span>
					</div>
				{/if}

				<!-- Skills -->
				{#if project.skills && project.skills.length > 0}
					<div class="flex flex-wrap gap-2 mt-3">
						{#each project.skills as skill}
							<span class="px-2.5 py-1 bg-primary-50 text-primary-700 text-xs font-medium rounded-lg border border-primary-100">
								{skill.name}
							</span>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<!-- Action Buttons -->
		<div class="flex flex-col md:flex-row gap-1 shrink-0">
			<button
				type="button"
				onclick={() => onEdit(project)}
				class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-colors"
				aria-label="Edit project"
			>
				<Pencil size={16} />
			</button>
			<button
				type="button"
				onclick={() => onDelete(project.id)}
				class="p-2 text-gray-400 hover:text-error-600 hover:bg-error-50 rounded-xl transition-colors"
				aria-label="Delete project"
			>
				<Trash2 size={16} />
			</button>
		</div>
	</div>
</div>

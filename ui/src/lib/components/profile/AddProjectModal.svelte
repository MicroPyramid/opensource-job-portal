<script lang="ts">
	import { X, Rocket, Search, Plus, Trash2 } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import type { Project, ProjectCreateUpdate, Skill } from '$lib/api/projects';
	import { addProject, updateProject } from '$lib/api/projects';
	import { searchSkills } from '$lib/api/skills';
	import { getCities, type City } from '$lib/api/locations';

	interface Props {
		isOpen: boolean;
		onClose: () => void;
		onSuccess: () => void;
		project?: Project | null;
	}

	let { isOpen = $bindable(), onClose, onSuccess, project = null }: Props = $props();

	// Form state
	let formData = $state<ProjectCreateUpdate>({
		name: '',
		from_date: '',
		to_date: '',
		skill_ids: [],
		description: '',
		location_id: undefined,
		role: '',
		size: undefined
	});

	// Skills state
	let selectedSkills: Skill[] = $state([]);
	let availableSkills: Skill[] = $state([]);
	let skillSearchQuery = $state('');
	let searchingSkills = $state(false);

	// Location state
	let cities: City[] = $state([]);
	let citySearchQuery = $state('');
	let searchingCities = $state(false);

	// UI state
	let loading = $state(false);

	/**
	 * Initialize form with project data (for editing)
	 */
	$effect(() => {
		if (isOpen && project) {
			// Editing mode
			formData = {
				name: project.name,
				from_date: project.from_date || '',
				to_date: project.to_date || '',
				skill_ids: project.skills.map((s) => s.id),
				description: project.description,
				location_id: project.location?.id,
				role: project.role || '',
				size: project.size
			};
			selectedSkills = [...project.skills];
		} else if (isOpen) {
			// Adding mode - reset form
			formData = {
				name: '',
				from_date: '',
				to_date: '',
				skill_ids: [],
				description: '',
				location_id: undefined,
				role: '',
				size: undefined
			};
			selectedSkills = [];
			availableSkills = [];
			cities = [];
		}
	});

	/**
	 * Search skills
	 */
	async function handleSkillSearch() {
		if (!skillSearchQuery.trim()) {
			availableSkills = [];
			return;
		}

		searchingSkills = true;
		try {
			const results = await searchSkills({ search: skillSearchQuery });
			// Filter out already selected skills
			availableSkills = results.filter(
				(skill) => !selectedSkills.some((s) => s.id === skill.id)
			);
		} catch (error) {
			console.error('Failed to search skills:', error);
		} finally {
			searchingSkills = false;
		}
	}

	/**
	 * Add skill to selection
	 */
	function addSkill(skill: Skill) {
		if (!selectedSkills.some((s) => s.id === skill.id)) {
			selectedSkills = [...selectedSkills, skill];
			formData.skill_ids = selectedSkills.map((s) => s.id);
			// Remove from available
			availableSkills = availableSkills.filter((s) => s.id !== skill.id);
			skillSearchQuery = '';
		}
	}

	/**
	 * Remove skill from selection
	 */
	function removeSkill(skillId: number) {
		selectedSkills = selectedSkills.filter((s) => s.id !== skillId);
		formData.skill_ids = selectedSkills.map((s) => s.id);
	}

	/**
	 * Search cities
	 */
	async function handleCitySearch() {
		if (!citySearchQuery.trim()) {
			cities = [];
			return;
		}

		searchingCities = true;
		try {
			cities = await getCities({ search: citySearchQuery });
		} catch (error) {
			console.error('Failed to search cities:', error);
		} finally {
			searchingCities = false;
		}
	}

	/**
	 * Handle form submission
	 */
	async function handleSubmit(e: Event) {
		e.preventDefault();

		// Validation
		if (!formData.name.trim()) {
			toast.error('Please enter project name');
			return;
		}

		if (!formData.description.trim()) {
			toast.error('Please enter project description');
			return;
		}

		if (formData.skill_ids.length === 0) {
			toast.error('Please add at least one skill');
			return;
		}

		loading = true;

		try {
			// Clean up undefined/empty values
			const submitData: ProjectCreateUpdate = {
				name: formData.name,
				description: formData.description,
				skill_ids: formData.skill_ids,
				from_date: formData.from_date || undefined,
				to_date: formData.to_date || undefined,
				location_id: formData.location_id || undefined,
				role: formData.role || undefined,
				size: formData.size || undefined
			};

			if (project) {
				// Update existing project
				await updateProject(project.id, submitData);
				toast.success('Project updated successfully!');
			} else {
				// Add new project
				await addProject(submitData);
				toast.success('Project added successfully!');
			}

			onSuccess();
			handleClose();
		} catch (error: any) {
			console.error('Failed to save project:', error);
			const errorMsg =
				error?.response?.data?.detail ||
				error?.response?.data?.error ||
				'Failed to save project. Please try again.';
			toast.error(errorMsg);
		} finally {
			loading = false;
		}
	}

	/**
	 * Close modal and reset form
	 */
	function handleClose() {
		onClose();
		formData = {
			name: '',
			from_date: '',
			to_date: '',
			skill_ids: [],
			description: '',
			location_id: undefined,
			role: '',
			size: undefined
		};
		selectedSkills = [];
		availableSkills = [];
		cities = [];
		skillSearchQuery = '';
		citySearchQuery = '';
	}

	/**
	 * Close modal when clicking outside
	 */
	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			handleClose();
		}
	}
</script>

{#if isOpen}
	<div
		class="fixed inset-0 z-50 overflow-y-auto"
		aria-labelledby="modal-title"
		role="dialog"
		aria-modal="true"
	>
		<!-- Backdrop -->
		<button
			type="button"
			class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity cursor-default"
			onclick={handleBackdropClick}
			aria-label="Close modal"
			tabindex="-1"
		></button>

		<!-- Modal -->
		<div class="flex min-h-screen items-center justify-center p-4">
			<div
				class="relative w-full max-w-3xl transform overflow-hidden rounded-lg bg-white shadow-xl transition-all"
			>
				<!-- Header -->
				<div class="flex items-center justify-between border-b border-gray-200 px-4 md:px-6 py-4">
					<div class="flex items-center gap-3">
						<div class="p-2 bg-blue-50 rounded-lg">
							<Rocket class="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
						</div>
						<h3 class="text-lg md:text-xl font-semibold text-gray-900" id="modal-title">
							{project ? 'Edit Project' : 'Add Project'}
						</h3>
					</div>
					<button
						type="button"
						onclick={handleClose}
						class="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-500"
					>
						<X class="w-5 h-5 md:w-6 md:h-6" />
					</button>
				</div>

				<!-- Form -->
				<form onsubmit={handleSubmit} class="px-4 md:px-6 py-4 md:py-6 space-y-4 md:space-y-6">
					<!-- Project Name -->
					<div>
						<label for="name" class="block text-sm font-medium text-gray-700 mb-1">
							Project Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="name"
							bind:value={formData.name}
							placeholder="e.g., E-commerce Platform"
							class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							required
						/>
					</div>

					<!-- Description -->
					<div>
						<label for="description" class="block text-sm font-medium text-gray-700 mb-1">
							Description <span class="text-red-500">*</span>
						</label>
						<textarea
							id="description"
							bind:value={formData.description}
							placeholder="Describe your project, your responsibilities, and key achievements..."
							rows="4"
							class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base resize-none"
							required
						></textarea>
					</div>

					<!-- Skills -->
					<div>
						<label for="project-skill-search" class="block text-sm font-medium text-gray-700 mb-1">
							Technologies Used <span class="text-red-500">*</span>
						</label>

						<!-- Selected Skills -->
						{#if selectedSkills.length > 0}
							<div class="flex flex-wrap gap-2 mb-3">
								{#each selectedSkills as skill (skill.id)}
									<span
										class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-blue-50 text-blue-700 border border-blue-200"
									>
										{skill.name}
										<button
											type="button"
											onclick={() => removeSkill(skill.id)}
											class="hover:text-blue-900"
											aria-label="Remove skill"
										>
											<Trash2 class="w-3.5 h-3.5" />
										</button>
									</span>
								{/each}
							</div>
						{/if}

						<!-- Skill Search -->
						<div class="relative">
							<input
								type="text"
								id="project-skill-search"
								placeholder="Search technologies (e.g., React, Python, AWS)..."
								bind:value={skillSearchQuery}
								oninput={handleSkillSearch}
								class="w-full px-3 md:px-4 py-2 md:py-2.5 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							/>
							<div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
								<Search class="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
							</div>
						</div>

						<!-- Available Skills Dropdown -->
						{#if availableSkills.length > 0}
							<div
								class="mt-2 max-h-48 overflow-y-auto border border-gray-300 rounded-lg bg-white shadow-lg"
							>
								{#each availableSkills as skill (skill.id)}
									<button
										type="button"
										onclick={() => addSkill(skill)}
										class="w-full px-3 md:px-4 py-2 text-left text-sm md:text-base hover:bg-blue-50 transition-colors flex items-center justify-between"
									>
										<span>{skill.name}</span>
										<Plus class="w-4 h-4 text-blue-600" />
									</button>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Role and Team Size -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="role" class="block text-sm font-medium text-gray-700 mb-1">
								Your Role
							</label>
							<input
								type="text"
								id="role"
								bind:value={formData.role}
								placeholder="e.g., Full Stack Developer"
								class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							/>
						</div>

						<div>
							<label for="size" class="block text-sm font-medium text-gray-700 mb-1">
								Team Size
							</label>
							<input
								type="number"
								id="size"
								bind:value={formData.size}
								placeholder="e.g., 4"
								min="1"
								class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							/>
						</div>
					</div>

					<!-- Date Range -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="from_date" class="block text-sm font-medium text-gray-700 mb-1">
								Start Date
							</label>
							<input
								type="date"
								id="from_date"
								bind:value={formData.from_date}
								class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							/>
						</div>

						<div>
							<label for="to_date" class="block text-sm font-medium text-gray-700 mb-1">
								End Date
							</label>
							<input
								type="date"
								id="to_date"
								bind:value={formData.to_date}
								class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							/>
							<p class="mt-1 text-xs text-gray-500">Leave blank if ongoing</p>
						</div>
					</div>

					<!-- Location -->
					<div>
						<label for="location" class="block text-sm font-medium text-gray-700 mb-1">
							Project Location
						</label>
						<div class="relative">
							<input
								type="text"
								placeholder="Search city..."
								bind:value={citySearchQuery}
								oninput={handleCitySearch}
								class="w-full px-3 md:px-4 py-2 md:py-2.5 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							/>
							<div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
								<Search class="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
							</div>
						</div>

						{#if cities.length > 0}
							<select
								id="location"
								bind:value={formData.location_id}
								class="mt-2 w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							>
								<option value={undefined}>Select location...</option>
								{#each cities as city}
									<option value={city.id}>
										{city.name}, {city.state_name}
									</option>
								{/each}
							</select>
						{/if}
					</div>

					<!-- Action Buttons -->
					<div class="flex flex-col-reverse md:flex-row gap-3 pt-4">
						<button
							type="button"
							onclick={handleClose}
							class="w-full md:w-auto px-4 md:px-6 py-2 md:py-2.5 border border-gray-300 rounded-lg text-sm md:text-base font-medium text-gray-700 hover:bg-gray-50 transition-colors"
							disabled={loading}
						>
							Cancel
						</button>
						<button
							type="submit"
							class="w-full md:flex-1 px-4 md:px-6 py-2 md:py-2.5 bg-blue-600 text-white rounded-lg text-sm md:text-base font-medium hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors"
							disabled={loading}
						>
							{loading ? 'Saving...' : project ? 'Update Project' : 'Add Project'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

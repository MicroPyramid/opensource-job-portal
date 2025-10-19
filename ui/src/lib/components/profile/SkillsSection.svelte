<script lang="ts">
	import { onMount } from 'svelte';
	import { Code, Plus, X, Edit2, Trash2, Save, Loader, Search } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import {
		searchSkills,
		getMySkills,
		addTechnicalSkill,
		updateTechnicalSkill,
		deleteTechnicalSkill,
		type Skill,
		type TechnicalSkill
	} from '$lib/api/skills';

	// User's current skills
	let userSkills: TechnicalSkill[] = [];
	let loading = true;
	let saving = false;

	// Add/Edit skill form
	let showAddForm = false;
	let editingSkillId: number | null = null;
	let skillSearch = '';
	let searchResults: Skill[] = [];
	let searchingSkills = false;
	let showSearchDropdown = false;

	// Form data
	let formData = {
		skill: null as number | null,
		skillName: '', // For display only
		year: undefined as number | undefined,
		month: undefined as number | undefined,
		last_used: '',
		version: '',
		proficiency: '' as '' | 'Poor' | 'Average' | 'Good' | 'Expert',
		is_major: false
	};

	const proficiencyLevels = [
		{ value: 'Poor', label: 'Beginner', color: 'bg-red-100 text-red-700' },
		{ value: 'Average', label: 'Intermediate', color: 'bg-yellow-100 text-yellow-700' },
		{ value: 'Good', label: 'Advanced', color: 'bg-blue-100 text-blue-700' },
		{ value: 'Expert', label: 'Expert', color: 'bg-green-100 text-green-700' }
	];

	onMount(async () => {
		await loadUserSkills();
	});

	async function loadUserSkills() {
		try {
			loading = true;
			userSkills = await getMySkills();
		} catch (err) {
			console.error('Failed to load skills:', err);
			toast.error('Failed to load skills');
		} finally {
			loading = false;
		}
	}

	async function handleSearchSkills(search: string) {
		if (!search || search.length < 2) {
			searchResults = [];
			return;
		}

		try {
			searchingSkills = true;
			searchResults = await searchSkills({ search });
		} catch (err) {
			console.error('Failed to search skills:', err);
		} finally {
			searchingSkills = false;
		}
	}

	function selectSkill(skill: Skill) {
		formData.skill = skill.id;
		formData.skillName = skill.name;
		skillSearch = skill.name;
		showSearchDropdown = false;
		searchResults = [];
	}

	function openAddForm() {
		resetForm();
		showAddForm = true;
		editingSkillId = null;
	}

	function openEditForm(skill: TechnicalSkill) {
		formData = {
			skill: skill.skill.id,
			skillName: skill.skill.name,
			year: skill.year,
			month: skill.month,
			last_used: skill.last_used || '',
			version: skill.version || '',
			proficiency: (skill.proficiency as '' | 'Poor' | 'Average' | 'Good' | 'Expert') || '',
			is_major: skill.is_major
		};
		skillSearch = skill.skill.name;
		editingSkillId = skill.id;
		showAddForm = true;
	}

	function closeForm() {
		showAddForm = false;
		editingSkillId = null;
		resetForm();
	}

	function resetForm() {
		formData = {
			skill: null,
			skillName: '',
			year: undefined,
			month: undefined,
			last_used: '',
			version: '',
			proficiency: '',
			is_major: false
		};
		skillSearch = '';
		searchResults = [];
	}

	async function handleSaveSkill() {
		// Validation
		if (!formData.skill) {
			toast.error('Please select a skill');
			return;
		}

		if (formData.year !== undefined && (formData.year < 0 || formData.year > 50)) {
			toast.error('Years must be between 0 and 50');
			return;
		}

		if (formData.month !== undefined && (formData.month < 0 || formData.month > 11)) {
			toast.error('Months must be between 0 and 11');
			return;
		}

		try {
			saving = true;

			const payload: any = {
				skill: formData.skill
			};

			// Only include fields that have values
			if (formData.year !== undefined) payload.year = formData.year;
			if (formData.month !== undefined) payload.month = formData.month;
			if (formData.last_used) payload.last_used = formData.last_used;
			if (formData.version) payload.version = formData.version;
			if (formData.proficiency) payload.proficiency = formData.proficiency;
			payload.is_major = formData.is_major;

			if (editingSkillId) {
				// Update existing skill
				await updateTechnicalSkill(editingSkillId, payload);
				toast.success('Skill updated successfully!');
			} else {
				// Add new skill
				await addTechnicalSkill(payload);
				toast.success('Skill added successfully!');
			}

			await loadUserSkills();
			closeForm();
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to save skill';
			toast.error(errorMessage);
			console.error('Save skill error:', err);
		} finally {
			saving = false;
		}
	}

	async function handleDeleteSkill(skillId: number, skillName: string) {
		if (!confirm(`Are you sure you want to remove "${skillName}" from your profile?`)) {
			return;
		}

		try {
			await deleteTechnicalSkill(skillId);
			toast.success('Skill removed successfully!');
			await loadUserSkills();
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to delete skill';
			toast.error(errorMessage);
			console.error('Delete skill error:', err);
		}
	}

	function formatExperience(year?: number, month?: number): string {
		if (year === undefined && month === undefined) return 'Not specified';
		const years = year ? `${year}y` : '';
		const months = month ? `${month}m` : '';
		return [years, months].filter(Boolean).join(' ');
	}

	function getProficiencyColor(proficiency?: string): string {
		const level = proficiencyLevels.find((l) => l.value === proficiency);
		return level?.color || 'bg-gray-100 text-gray-700';
	}

	function getProficiencyLabel(proficiency?: string): string {
		const level = proficiencyLevels.find((l) => l.value === proficiency);
		return level?.label || proficiency || 'Not specified';
	}

	// Search when user types
	$: handleSearchSkills(skillSearch);
</script>

<div class="bg-white rounded-lg shadow-sm p-6">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
			<Code class="w-5 h-5" />
			Technical Skills
		</h2>
		<button
			type="button"
			onclick={openAddForm}
			class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
		>
			<Plus class="w-4 h-4" />
			Add Skill
		</button>
	</div>

	<!-- Loading State -->
	{#if loading}
		<div class="flex items-center justify-center py-8">
			<Loader class="w-6 h-6 animate-spin text-blue-600" />
			<p class="ml-3 text-gray-600">Loading skills...</p>
		</div>
	{:else if userSkills.length === 0 && !showAddForm}
		<!-- Empty State -->
		<div class="text-center py-8">
			<Code class="w-12 h-12 mx-auto text-gray-400 mb-3" />
			<p class="text-gray-600 mb-4">No skills added yet</p>
			<button
				type="button"
				onclick={openAddForm}
				class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				<Plus class="w-4 h-4" />
				Add Your First Skill
			</button>
		</div>
	{:else}
		<!-- Skills Grid -->
		<div class="grid md:grid-cols-2 gap-4 mb-4">
			{#each userSkills as skill}
				<div class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
					<div class="flex items-start justify-between mb-2">
						<div class="flex-1">
							<h3 class="font-semibold text-gray-900 flex items-center gap-2">
								{skill.skill.name}
								{#if skill.is_major}
									<span class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
										Major
									</span>
								{/if}
							</h3>
							{#if skill.version}
								<p class="text-xs text-gray-500 mt-1">Version: {skill.version}</p>
							{/if}
						</div>
						<div class="flex items-center gap-1">
							<button
								type="button"
								onclick={() => openEditForm(skill)}
								class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
								title="Edit skill"
							>
								<Edit2 class="w-4 h-4" />
							</button>
							<button
								type="button"
								onclick={() => handleDeleteSkill(skill.id, skill.skill.name)}
								class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
								title="Remove skill"
							>
								<Trash2 class="w-4 h-4" />
							</button>
						</div>
					</div>

					<div class="grid grid-cols-2 gap-2 text-sm">
						<div>
							<p class="text-gray-500">Experience</p>
							<p class="font-medium text-gray-900">{formatExperience(skill.year, skill.month)}</p>
						</div>
						<div>
							<p class="text-gray-500">Proficiency</p>
							<span class="inline-block px-2 py-0.5 rounded text-xs font-medium {getProficiencyColor(skill.proficiency)}">
								{getProficiencyLabel(skill.proficiency)}
							</span>
						</div>
					</div>

					{#if skill.last_used}
						<p class="text-xs text-gray-500 mt-2">Last used: {skill.last_used}</p>
					{/if}
				</div>
			{/each}
		</div>
	{/if}

	<!-- Add/Edit Form Modal -->
	{#if showAddForm}
		<div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
			<div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
				<div class="p-6">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-xl font-semibold text-gray-900">
							{editingSkillId ? 'Edit Skill' : 'Add Skill'}
						</h3>
						<button
							type="button"
							onclick={closeForm}
							class="p-1 text-gray-400 hover:text-gray-600 rounded"
						>
							<X class="w-5 h-5" />
						</button>
					</div>

					<div class="space-y-4">
						<!-- Skill Search -->
						<div>
							<label for="skill_search" class="block text-sm font-medium text-gray-700 mb-2">
								Skill Name <span class="text-red-500">*</span>
							</label>
							<div class="relative">
								<div class="relative">
									<input
										type="text"
										id="skill_search"
										bind:value={skillSearch}
										onfocus={() => (showSearchDropdown = true)}
										onblur={() => setTimeout(() => (showSearchDropdown = false), 200)}
										placeholder="Search for a skill... (type at least 2 characters)"
										class="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
										disabled={editingSkillId !== null}
									/>
									<Search class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
								</div>

								{#if searchingSkills}
									<div class="absolute right-3 top-3">
										<Loader class="w-4 h-4 animate-spin text-gray-400" />
									</div>
								{/if}

								<!-- Search Dropdown -->
								{#if showSearchDropdown && searchResults.length > 0 && !editingSkillId}
									<div
										class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
									>
										{#each searchResults as skill}
											<button
												type="button"
												onclick={() => selectSkill(skill)}
												class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center justify-between"
											>
												<div>
													<div class="font-medium">{skill.name}</div>
													<div class="text-xs text-gray-500 capitalize">{skill.skill_type}</div>
												</div>
											</button>
										{/each}
									</div>
								{/if}
							</div>
							{#if editingSkillId}
								<p class="mt-1 text-xs text-gray-500">Skill cannot be changed when editing</p>
							{/if}
						</div>

						<!-- Experience -->
						<div class="grid grid-cols-2 gap-4">
							<div>
								<label for="years" class="block text-sm font-medium text-gray-700 mb-2">
									Years of Experience
								</label>
								<input
									type="number"
									id="years"
									bind:value={formData.year}
									min="0"
									max="50"
									placeholder="0-50"
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								/>
							</div>
							<div>
								<label for="months" class="block text-sm font-medium text-gray-700 mb-2">
									Months
								</label>
								<input
									type="number"
									id="months"
									bind:value={formData.month}
									min="0"
									max="11"
									placeholder="0-11"
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								/>
							</div>
						</div>

						<!-- Proficiency -->
						<div>
							<label for="proficiency" class="block text-sm font-medium text-gray-700 mb-2">
								Proficiency Level
							</label>
							<select
								id="proficiency"
								bind:value={formData.proficiency}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							>
								<option value="">Select proficiency</option>
								{#each proficiencyLevels as level}
									<option value={level.value}>{level.label}</option>
								{/each}
							</select>
						</div>

						<!-- Version -->
						<div>
							<label for="version" class="block text-sm font-medium text-gray-700 mb-2">
								Version (Optional)
							</label>
							<input
								type="text"
								id="version"
								bind:value={formData.version}
								placeholder="e.g., 5.0, ES6, 3.x"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>

						<!-- Last Used -->
						<div>
							<label for="last_used" class="block text-sm font-medium text-gray-700 mb-2">
								Last Used (Optional)
							</label>
							<input
								type="date"
								id="last_used"
								bind:value={formData.last_used}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>

						<!-- Is Major Skill -->
						<div>
							<label class="flex items-center gap-2 cursor-pointer">
								<input
									type="checkbox"
									bind:checked={formData.is_major}
									class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
								/>
								<div>
									<p class="font-medium text-gray-900">Major Skill</p>
									<p class="text-sm text-gray-600">Mark this as one of your primary skills</p>
								</div>
							</label>
						</div>
					</div>

					<!-- Form Actions -->
					<div class="flex items-center justify-end gap-3 mt-6 pt-4 border-t">
						<button
							type="button"
							onclick={closeForm}
							class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
							disabled={saving}
						>
							Cancel
						</button>
						<button
							type="button"
							onclick={handleSaveSkill}
							disabled={saving || !formData.skill}
							class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
						>
							{#if saving}
								<Loader class="w-4 h-4 animate-spin" />
								Saving...
							{:else}
								<Save class="w-4 h-4" />
								{editingSkillId ? 'Update Skill' : 'Add Skill'}
							{/if}
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

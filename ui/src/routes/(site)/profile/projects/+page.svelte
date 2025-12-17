<script lang="ts">
	import { onMount } from 'svelte';
	import { Rocket, Plus, FolderOpen } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import { getMyProjects, deleteProject } from '$lib/api/projects';
	import type { Project } from '$lib/api/projects';
	import ProjectCard from '$lib/components/profile/ProjectCard.svelte';
	import AddProjectModal from '$lib/components/profile/AddProjectModal.svelte';

	// State
	let projectList: Project[] = $state([]);
	let loading = $state(true);
	let isModalOpen = $state(false);
	let selectedProject: Project | null = $state(null);

	/**
	 * Load projects on mount
	 */
	onMount(async () => {
		await loadProjects();
	});

	/**
	 * Fetch user's projects
	 */
	async function loadProjects() {
		loading = true;
		try {
			projectList = await getMyProjects();
		} catch (error) {
			console.error('Failed to load projects:', error);
			toast.error('Failed to load projects');
		} finally {
			loading = false;
		}
	}

	/**
	 * Open modal to add new project
	 */
	function handleAddProject() {
		selectedProject = null;
		isModalOpen = true;
	}

	/**
	 * Open modal to edit project
	 */
	function handleEditProject(project: Project) {
		selectedProject = project;
		isModalOpen = true;
	}

	/**
	 * Delete project with confirmation
	 */
	async function handleDeleteProject(id: number) {
		if (!confirm('Are you sure you want to delete this project?')) {
			return;
		}

		try {
			await deleteProject(id);
			toast.success('Project deleted successfully!');
			await loadProjects();
		} catch (error) {
			console.error('Failed to delete project:', error);
			toast.error('Failed to delete project. Please try again.');
		}
	}

	/**
	 * Handle successful add/edit
	 */
	async function handleSuccess() {
		await loadProjects();
	}

	/**
	 * Close modal
	 */
	function handleCloseModal() {
		isModalOpen = false;
		selectedProject = null;
	}
</script>

<svelte:head>
	<title>Projects - PeelJobs</title>
</svelte:head>


	
		<!-- Header -->
		<div class="mb-6 md:mb-8">
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 md:p-3 bg-blue-600 rounded-lg">
					<Rocket class="w-6 h-6 md:w-8 md:h-8 text-white" />
				</div>
				<div>
					<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Projects</h1>
					<p class="text-sm md:text-base text-gray-600 mt-1">
						Showcase your portfolio and accomplishments
					</p>
				</div>
			</div>
		</div>

		<!-- Add Project Button -->
		<div class="mb-6">
			<button
				type="button"
				onclick={handleAddProject}
				class="w-full md:w-auto inline-flex items-center justify-center gap-2 px-4 md:px-6 py-2.5 md:py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm md:text-base"
			>
				<Plus class="w-4 h-4 md:w-5 md:h-5" />
				<span>Add Project</span>
			</button>
		</div>

		<!-- Project List -->
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="text-center">
					<div
						class="inline-block w-8 h-8 md:w-12 md:h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"
					></div>
					<p class="mt-4 text-sm md:text-base text-gray-600">Loading projects...</p>
				</div>
			</div>
		{:else if projectList.length === 0}
			<!-- Empty State -->
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 md:p-12 text-center">
				<div
					class="mx-auto w-16 h-16 md:w-20 md:h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4"
				>
					<FolderOpen class="w-8 h-8 md:w-10 md:h-10 text-gray-400" />
				</div>
				<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-2">No projects added yet</h3>
				<p class="text-sm md:text-base text-gray-600 mb-6 max-w-md mx-auto">
					Add projects to showcase your work, skills, and achievements. Projects help recruiters
					understand your practical experience.
				</p>
				<button
					type="button"
					onclick={handleAddProject}
					class="inline-flex items-center gap-2 px-4 md:px-6 py-2.5 md:py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm md:text-base"
				>
					<Plus class="w-4 h-4 md:w-5 md:h-5" />
					<span>Add Your First Project</span>
				</button>
			</div>
		{:else}
			<!-- Project Cards -->
			<div class="space-y-4 md:space-y-6">
				{#each projectList as project (project.id)}
					<ProjectCard {project} onEdit={handleEditProject} onDelete={handleDeleteProject} />
				{/each}
			</div>

			<!-- Summary -->
			<div class="mt-6 md:mt-8 p-4 md:p-6 bg-blue-50 border border-blue-200 rounded-lg">
				<div class="flex items-start gap-3">
					<Rocket class="w-5 h-5 md:w-6 md:h-6 text-blue-600 shrink-0 mt-0.5" />
					<div>
						<h3 class="text-sm md:text-base font-semibold text-gray-900 mb-1">
							{projectList.length} {projectList.length === 1 ? 'Project' : 'Projects'} Showcased
						</h3>
						<p class="text-xs md:text-sm text-gray-600">
							Your projects demonstrate your skills and experience to potential employers. Keep
							them updated with your latest work!
						</p>
					</div>
				</div>
			</div>
		{/if}
<!-- Add/Edit Project Modal -->
<AddProjectModal
	bind:isOpen={isModalOpen}
	onClose={handleCloseModal}
	onSuccess={handleSuccess}
	project={selectedProject}
/>

<script lang="ts">
	import { onMount } from 'svelte';
	import { Briefcase, Plus, X, Edit2, Trash2, Save, Loader, Calendar, Building2 } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import {
		getMyEmploymentHistory,
		addEmploymentHistory,
		updateEmploymentHistory,
		deleteEmploymentHistory,
		type EmploymentHistory
	} from '$lib/api/employment';

	// User's employment history
	let employmentHistory: EmploymentHistory[] = [];
	let loading = true;
	let saving = false;

	// Add/Edit form
	let showAddForm = false;
	let editingEmploymentId: number | null = null;

	// Form data
	let formData = {
		company: '',
		designation: '',
		from_date: '',
		to_date: '',
		current_job: false,
		job_profile: ''
	};

	onMount(async () => {
		await loadEmploymentHistory();
	});

	async function loadEmploymentHistory() {
		try {
			loading = true;
			employmentHistory = await getMyEmploymentHistory();
		} catch (err) {
			console.error('Failed to load employment history:', err);
			toast.error('Failed to load employment history');
		} finally {
			loading = false;
		}
	}

	function openAddForm() {
		resetForm();
		showAddForm = true;
		editingEmploymentId = null;
	}

	function openEditForm(employment: EmploymentHistory) {
		formData = {
			company: employment.company,
			designation: employment.designation,
			from_date: employment.from_date,
			to_date: employment.to_date || '',
			current_job: employment.current_job,
			job_profile: employment.job_profile
		};
		editingEmploymentId = employment.id;
		showAddForm = true;
	}

	function closeForm() {
		showAddForm = false;
		editingEmploymentId = null;
		resetForm();
	}

	function resetForm() {
		formData = {
			company: '',
			designation: '',
			from_date: '',
			to_date: '',
			current_job: false,
			job_profile: ''
		};
	}

	function handleCurrentJobChange() {
		if (formData.current_job) {
			formData.to_date = '';
		}
	}

	async function handleSaveEmployment() {
		// Validation
		if (!formData.company.trim()) {
			toast.error('Company name is required');
			return;
		}

		if (!formData.designation.trim()) {
			toast.error('Designation is required');
			return;
		}

		if (!formData.from_date) {
			toast.error('Start date is required');
			return;
		}

		if (!formData.current_job && !formData.to_date) {
			toast.error('End date is required for past jobs');
			return;
		}

		if (!formData.job_profile.trim()) {
			toast.error('Job profile/description is required');
			return;
		}

		try {
			saving = true;

			const payload: any = {
				company: formData.company.trim(),
				designation: formData.designation.trim(),
				from_date: formData.from_date,
				current_job: formData.current_job,
				job_profile: formData.job_profile.trim()
			};

			// Only include to_date if not current job
			if (!formData.current_job && formData.to_date) {
				payload.to_date = formData.to_date;
			}

			if (editingEmploymentId) {
				// Update existing employment
				await updateEmploymentHistory(editingEmploymentId, payload);
				toast.success('Employment record updated successfully!');
			} else {
				// Add new employment
				await addEmploymentHistory(payload);
				toast.success('Employment record added successfully!');
			}

			await loadEmploymentHistory();
			closeForm();
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to save employment record';
			toast.error(errorMessage);
			console.error('Save employment error:', err);
		} finally {
			saving = false;
		}
	}

	async function handleDeleteEmployment(employmentId: number, company: string) {
		if (!confirm(`Are you sure you want to remove your employment at "${company}"?`)) {
			return;
		}

		try {
			await deleteEmploymentHistory(employmentId);
			toast.success('Employment record removed successfully!');
			await loadEmploymentHistory();
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to delete employment record';
			toast.error(errorMessage);
			console.error('Delete employment error:', err);
		}
	}

	function formatDate(dateString?: string): string {
		if (!dateString) return 'Present';
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
	}

	// Watch current_job checkbox
	$: if (formData.current_job) {
		formData.to_date = '';
	}
</script>

<div class="bg-white rounded-lg shadow-sm p-6">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
			<Briefcase class="w-5 h-5" />
			Employment History
		</h2>
		<button
			type="button"
			onclick={openAddForm}
			class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
		>
			<Plus class="w-4 h-4" />
			Add Experience
		</button>
	</div>

	<!-- Loading State -->
	{#if loading}
		<div class="flex items-center justify-center py-8">
			<Loader class="w-6 h-6 animate-spin text-blue-600" />
			<p class="ml-3 text-gray-600">Loading employment history...</p>
		</div>
	{:else if employmentHistory.length === 0 && !showAddForm}
		<!-- Empty State -->
		<div class="text-center py-8">
			<Briefcase class="w-12 h-12 mx-auto text-gray-400 mb-3" />
			<p class="text-gray-600 mb-4">No employment history added yet</p>
			<button
				type="button"
				onclick={openAddForm}
				class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				<Plus class="w-4 h-4" />
				Add Your First Job
			</button>
		</div>
	{:else}
		<!-- Timeline View -->
		<div class="space-y-6">
			{#each employmentHistory as employment, index}
				<div class="relative pl-8 pb-6 {index < employmentHistory.length - 1 ? 'border-l-2 border-gray-200' : ''}">
					<!-- Timeline dot -->
					<div class="absolute left-0 top-0 -translate-x-1/2 w-4 h-4 rounded-full {employment.current_job ? 'bg-green-500' : 'bg-blue-500'} ring-4 ring-white"></div>

					<div class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
						<div class="flex items-start justify-between mb-2">
							<div class="flex-1">
								<h3 class="font-semibold text-gray-900 text-lg flex items-center gap-2">
									{employment.designation}
									{#if employment.current_job}
										<span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
											Current
										</span>
									{/if}
								</h3>
								<p class="text-blue-600 font-medium flex items-center gap-1 mt-1">
									<Building2 class="w-4 h-4" />
									{employment.company}
								</p>
								<p class="text-sm text-gray-500 flex items-center gap-1 mt-1">
									<Calendar class="w-4 h-4" />
									{formatDate(employment.from_date)} - {formatDate(employment.to_date)}
									{#if employment.duration}
										<span class="text-gray-400">• {employment.duration}</span>
									{/if}
								</p>
							</div>
							<div class="flex items-center gap-1">
								<button
									type="button"
									onclick={() => openEditForm(employment)}
									class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
									title="Edit employment"
								>
									<Edit2 class="w-4 h-4" />
								</button>
								<button
									type="button"
									onclick={() => handleDeleteEmployment(employment.id, employment.company)}
									class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
									title="Remove employment"
								>
									<Trash2 class="w-4 h-4" />
								</button>
							</div>
						</div>

						<!-- Job Profile -->
						<div class="mt-3 text-sm text-gray-700 whitespace-pre-line">
							{employment.job_profile}
						</div>
					</div>
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
							{editingEmploymentId ? 'Edit Employment' : 'Add Employment'}
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
						<!-- Company Name -->
						<div>
							<label for="company" class="block text-sm font-medium text-gray-700 mb-2">
								Company Name <span class="text-red-500">*</span>
							</label>
							<input
								type="text"
								id="company"
								bind:value={formData.company}
								placeholder="e.g., Google, Microsoft"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>

						<!-- Designation -->
						<div>
							<label for="designation" class="block text-sm font-medium text-gray-700 mb-2">
								Designation/Job Title <span class="text-red-500">*</span>
							</label>
							<input
								type="text"
								id="designation"
								bind:value={formData.designation}
								placeholder="e.g., Senior Software Engineer"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>

						<!-- Dates -->
						<div class="grid grid-cols-2 gap-4">
							<div>
								<label for="from_date" class="block text-sm font-medium text-gray-700 mb-2">
									Start Date <span class="text-red-500">*</span>
								</label>
								<input
									type="date"
									id="from_date"
									bind:value={formData.from_date}
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								/>
							</div>
							<div>
								<label for="to_date" class="block text-sm font-medium text-gray-700 mb-2">
									End Date {formData.current_job ? '(Not applicable)' : '*'}
								</label>
								<input
									type="date"
									id="to_date"
									bind:value={formData.to_date}
									disabled={formData.current_job}
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
								/>
							</div>
						</div>

						<!-- Current Job Checkbox -->
						<div>
							<label class="flex items-center gap-2 cursor-pointer">
								<input
									type="checkbox"
									bind:checked={formData.current_job}
									onchange={handleCurrentJobChange}
									class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
								/>
								<div>
									<p class="font-medium text-gray-900">I currently work here</p>
									<p class="text-sm text-gray-600">Check this if this is your current job</p>
								</div>
							</label>
						</div>

						<!-- Job Profile/Description -->
						<div>
							<label for="job_profile" class="block text-sm font-medium text-gray-700 mb-2">
								Job Profile/Description <span class="text-red-500">*</span>
							</label>
							<textarea
								id="job_profile"
								bind:value={formData.job_profile}
								rows="5"
								placeholder="Describe your key responsibilities, achievements, and projects..."
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							></textarea>
							<p class="mt-1 text-xs text-gray-500">
								Include your main responsibilities, achievements, and technologies used
							</p>
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
							onclick={handleSaveEmployment}
							disabled={saving}
							class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
						>
							{#if saving}
								<Loader class="w-4 h-4 animate-spin" />
								Saving...
							{:else}
								<Save class="w-4 h-4" />
								{editingEmploymentId ? 'Update Employment' : 'Add Employment'}
							{/if}
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

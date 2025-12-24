<script lang="ts">
	import { onMount } from 'svelte';
	import { Briefcase, Plus, X, Pencil, Trash2, Save, Loader, Calendar, Building2 } from '@lucide/svelte';
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

<div class="p-5 lg:p-6">
	<div class="flex items-center justify-between mb-6">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
				<Briefcase size={20} class="text-primary-600" />
			</div>
			<div>
				<h2 class="text-lg font-semibold text-gray-900">Employment History</h2>
				<p class="text-sm text-gray-600">Your work experience</p>
			</div>
		</div>
		<button
			type="button"
			onclick={openAddForm}
			class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors elevation-1 text-sm"
		>
			<Plus size={18} />
			<span class="hidden sm:inline">Add Experience</span>
		</button>
	</div>

	<!-- Loading State -->
	{#if loading}
		<div class="flex flex-col items-center justify-center py-12">
			<div class="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mb-4"></div>
			<p class="text-gray-600">Loading employment history...</p>
		</div>
	{:else if employmentHistory.length === 0 && !showAddForm}
		<!-- Empty State -->
		<div class="text-center py-12">
			<div class="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-6">
				<Briefcase size={36} class="text-gray-400" />
			</div>
			<h3 class="text-xl font-semibold text-gray-900 mb-2">No employment history added yet</h3>
			<p class="text-gray-600 mb-6 max-w-md mx-auto">
				Add your work experience to showcase your professional background to potential employers.
			</p>
			<button
				type="button"
				onclick={openAddForm}
				class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors elevation-1"
			>
				<Plus size={18} />
				<span>Add Your First Job</span>
			</button>
		</div>
	{:else}
		<!-- Timeline View -->
		<div class="space-y-4 mb-6">
			{#each employmentHistory as employment, index}
				<div
					class="relative pl-8 animate-fade-in-up"
					style="opacity: 0; animation-delay: {index * 50}ms;"
				>
					<!-- Timeline line -->
					{#if index < employmentHistory.length - 1}
						<div class="absolute left-[7px] top-6 bottom-0 w-0.5 bg-gray-200"></div>
					{/if}
					<!-- Timeline dot -->
					<div class="absolute left-0 top-1.5 w-4 h-4 rounded-full {employment.current_job ? 'bg-success-500' : 'bg-primary-500'} ring-4 ring-white"></div>

					<div class="bg-surface-50 border border-gray-100 rounded-2xl p-5 hover:border-primary-200 hover:bg-white transition-all">
						<div class="flex items-start justify-between mb-3">
							<div class="flex-1">
								<h3 class="font-semibold text-gray-900 text-lg flex flex-wrap items-center gap-2">
									{employment.designation}
									{#if employment.current_job}
										<span class="text-xs bg-success-50 text-success-700 px-2.5 py-1 rounded-full border border-success-200">
											Current
										</span>
									{/if}
								</h3>
								<p class="text-primary-600 font-medium flex items-center gap-1.5 mt-1.5">
									<Building2 size={16} />
									{employment.company}
								</p>
								<p class="text-sm text-gray-500 flex items-center gap-1.5 mt-1.5">
									<Calendar size={14} />
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
									class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-colors"
									title="Edit employment"
								>
									<Pencil size={16} />
								</button>
								<button
									type="button"
									onclick={() => handleDeleteEmployment(employment.id, employment.company)}
									class="p-2 text-gray-400 hover:text-error-600 hover:bg-error-50 rounded-xl transition-colors"
									title="Remove employment"
								>
									<Trash2 size={16} />
								</button>
							</div>
						</div>

						<!-- Job Profile -->
						<div class="mt-3 pt-3 border-t border-gray-100 text-sm text-gray-700 whitespace-pre-line leading-relaxed">
							{employment.job_profile}
						</div>
					</div>
				</div>
			{/each}
		</div>

		<!-- Summary Card -->
		<div class="p-5 bg-primary-50 border border-primary-100 rounded-2xl">
			<div class="flex items-start gap-4">
				<div class="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center flex-shrink-0">
					<Briefcase size={22} class="text-primary-600" />
				</div>
				<div>
					<h3 class="font-semibold text-gray-900 mb-1">
						{employmentHistory.length} {employmentHistory.length === 1 ? 'Position' : 'Positions'} Added
					</h3>
					<p class="text-sm text-gray-600">
						Keep your employment history updated to showcase your career progression to recruiters.
					</p>
				</div>
			</div>
		</div>
	{/if}

	<!-- Add/Edit Form Modal -->
	{#if showAddForm}
		<div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
			<div class="bg-white rounded-2xl elevation-4 max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-scale-in">
				<!-- Modal Header -->
				<div class="flex items-center justify-between p-5 lg:p-6 border-b border-gray-100">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
							<Briefcase size={20} class="text-primary-600" />
						</div>
						<h3 class="text-lg font-semibold text-gray-900">
							{editingEmploymentId ? 'Edit Employment' : 'Add Employment'}
						</h3>
					</div>
					<button
						type="button"
						onclick={closeForm}
						class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
					>
						<X size={20} />
					</button>
				</div>

				<!-- Modal Body -->
				<div class="p-5 lg:p-6 space-y-5">
					<!-- Company Name -->
					<div>
						<label for="company" class="block text-sm font-medium text-gray-700 mb-2">
							Company Name <span class="text-error-500">*</span>
						</label>
						<input
							type="text"
							id="company"
							bind:value={formData.company}
							placeholder="e.g., Google, Microsoft"
							class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
						/>
					</div>

					<!-- Designation -->
					<div>
						<label for="designation" class="block text-sm font-medium text-gray-700 mb-2">
							Designation/Job Title <span class="text-error-500">*</span>
						</label>
						<input
							type="text"
							id="designation"
							bind:value={formData.designation}
							placeholder="e.g., Senior Software Engineer"
							class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
						/>
					</div>

					<!-- Dates -->
					<div class="grid grid-cols-2 gap-4">
						<div>
							<label for="from_date" class="block text-sm font-medium text-gray-700 mb-2">
								Start Date <span class="text-error-500">*</span>
							</label>
							<input
								type="date"
								id="from_date"
								bind:value={formData.from_date}
								class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
							/>
						</div>
						<div>
							<label for="to_date" class="block text-sm font-medium text-gray-700 mb-2">
								End Date {formData.current_job ? '' : ''}
							</label>
							<input
								type="date"
								id="to_date"
								bind:value={formData.to_date}
								disabled={formData.current_job}
								class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
							/>
						</div>
					</div>

					<!-- Current Job Checkbox -->
					<div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
						<label class="flex items-start gap-3 cursor-pointer">
							<input
								type="checkbox"
								bind:checked={formData.current_job}
								onchange={handleCurrentJobChange}
								class="w-5 h-5 mt-0.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
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
							Job Profile/Description <span class="text-error-500">*</span>
						</label>
						<textarea
							id="job_profile"
							bind:value={formData.job_profile}
							rows="5"
							placeholder="Describe your key responsibilities, achievements, and projects..."
							class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none resize-none"
						></textarea>
						<p class="mt-2 text-xs text-gray-500">
							Include your main responsibilities, achievements, and technologies used
						</p>
					</div>
				</div>

				<!-- Modal Footer -->
				<div class="flex items-center justify-end gap-3 p-5 lg:p-6 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
					<button
						type="button"
						onclick={closeForm}
						class="px-5 py-2.5 text-gray-700 bg-white border border-gray-200 rounded-full font-medium hover:bg-gray-50 transition-colors"
						disabled={saving}
					>
						Cancel
					</button>
					<button
						type="button"
						onclick={handleSaveEmployment}
						disabled={saving}
						class="px-5 py-2.5 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 elevation-1"
					>
						{#if saving}
							<Loader size={18} class="animate-spin" />
							Saving...
						{:else}
							<Save size={18} />
							{editingEmploymentId ? 'Update Employment' : 'Add Employment'}
						{/if}
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>

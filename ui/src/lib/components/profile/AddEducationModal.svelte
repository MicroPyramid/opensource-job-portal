<script lang="ts">
	import { X, GraduationCap, Search } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import type {
		EducationDetails,
		EducationDetailsCreateUpdate,
		Qualification,
		Degree,
		EducationInstitute
	} from '$lib/api/education';
	import {
		addEducation,
		updateEducation,
		getQualifications,
		getDegrees,
		searchInstitutes
	} from '$lib/api/education';
	import { onMount } from 'svelte';

	interface Props {
		isOpen: boolean;
		onClose: () => void;
		onSuccess: () => void;
		education?: EducationDetails | null;
	}

	let { isOpen = $bindable(), onClose, onSuccess, education = null }: Props = $props();

	// Form state
	let formData = $state<EducationDetailsCreateUpdate>({
		institute_id: 0,
		degree_id: 0,
		from_date: '',
		to_date: '',
		score: '',
		current_education: false
	});

	// Lookup data
	let qualifications: Qualification[] = $state([]);
	let degrees: Degree[] = $state([]);
	let institutes: EducationInstitute[] = $state([]);

	// UI state
	let loading = $state(false);
	let loadingLookups = $state(false);
	let selectedQualificationId = $state<number>(0);
	let instituteSearchQuery = $state('');
	let degreeSearchQuery = $state('');
	let searchingInstitutes = $state(false);

	// Reactive degree filtering based on selected qualification
	let filteredDegrees = $derived(
		selectedQualificationId
			? degrees.filter((d) => d.qualification.id === selectedQualificationId)
			: degrees
	);

	/**
	 * Load lookup data on mount
	 */
	onMount(async () => {
		await loadLookupData();
	});

	/**
	 * Load qualifications, degrees, and institutes
	 */
	async function loadLookupData() {
		loadingLookups = true;
		try {
			const [qualData, degreeData, instituteData] = await Promise.all([
				getQualifications(),
				getDegrees(),
				searchInstitutes({ limit: 50 })
			]);

			qualifications = qualData;
			degrees = degreeData;
			institutes = instituteData;
		} catch (error) {
			console.error('Failed to load lookup data:', error);
			toast.error('Failed to load form data. Please try again.');
		} finally {
			loadingLookups = false;
		}
	}

	/**
	 * Search institutes based on query
	 */
	async function handleInstituteSearch() {
		if (!instituteSearchQuery.trim()) {
			await searchInstitutes({ limit: 50 }).then((data) => (institutes = data));
			return;
		}

		searchingInstitutes = true;
		try {
			institutes = await searchInstitutes({
				search: instituteSearchQuery,
				limit: 50
			});
		} catch (error) {
			console.error('Failed to search institutes:', error);
		} finally {
			searchingInstitutes = false;
		}
	}

	/**
	 * Filter degrees when qualification changes
	 */
	async function handleQualificationChange() {
		if (selectedQualificationId) {
			try {
				degrees = await getDegrees({ qualification_id: selectedQualificationId });
			} catch (error) {
				console.error('Failed to filter degrees:', error);
			}
		}
		// Reset degree selection when qualification changes
		formData.degree_id = 0;
	}

	/**
	 * Initialize form with education data (for editing)
	 */
	$effect(() => {
		if (isOpen && education) {
			// Editing mode
			formData = {
				institute_id: education.institute_id || 0,
				degree_id: education.degree_id || 0,
				from_date: education.from_date,
				to_date: education.to_date || '',
				score: education.score,
				current_education: education.current_education
			};

			// Find qualification ID from degree
			const degree = degrees.find((d) => d.id === education.degree_id);
			if (degree) {
				selectedQualificationId = degree.qualification.id;
			}
		} else if (isOpen) {
			// Adding mode - reset form
			formData = {
				institute_id: 0,
				degree_id: 0,
				from_date: '',
				to_date: '',
				score: '',
				current_education: false
			};
			selectedQualificationId = 0;
		}
	});

	/**
	 * Handle current education checkbox
	 */
	$effect(() => {
		if (formData.current_education) {
			formData.to_date = '';
		}
	});

	/**
	 * Handle form submission
	 */
	async function handleSubmit(e: Event) {
		e.preventDefault();

		// Validation
		if (!formData.institute_id) {
			toast.error('Please select an institute');
			return;
		}

		if (!formData.degree_id) {
			toast.error('Please select a degree');
			return;
		}

		if (!formData.from_date) {
			toast.error('Please enter start date');
			return;
		}

		if (!formData.current_education && !formData.to_date) {
			toast.error('Please enter end date or mark as current education');
			return;
		}

		loading = true;

		try {
			if (education) {
				// Update existing education
				await updateEducation(education.id, formData);
				toast.success('Education updated successfully!');
			} else {
				// Add new education
				await addEducation(formData);
				toast.success('Education added successfully!');
			}

			onSuccess();
			handleClose();
		} catch (error: any) {
			console.error('Failed to save education:', error);
			const errorMsg =
				error?.response?.data?.detail ||
				error?.response?.data?.error ||
				'Failed to save education. Please try again.';
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
			institute_id: 0,
			degree_id: 0,
			from_date: '',
			to_date: '',
			score: '',
			current_education: false
		};
		selectedQualificationId = 0;
		instituteSearchQuery = '';
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
				class="relative w-full max-w-2xl transform overflow-hidden rounded-lg bg-white shadow-xl transition-all"
			>
				<!-- Header -->
				<div class="flex items-center justify-between border-b border-gray-200 px-4 md:px-6 py-4">
					<div class="flex items-center gap-3">
						<div class="p-2 bg-blue-50 rounded-lg">
							<GraduationCap class="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
						</div>
						<h3 class="text-lg md:text-xl font-semibold text-gray-900" id="modal-title">
							{education ? 'Edit Education' : 'Add Education'}
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
					<!-- Qualification Selection -->
					<div>
						<label for="qualification" class="block text-sm font-medium text-gray-700 mb-1">
							Qualification Type <span class="text-red-500">*</span>
						</label>
						<select
							id="qualification"
							bind:value={selectedQualificationId}
							onchange={handleQualificationChange}
							class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							required
							disabled={loadingLookups}
						>
							<option value={0}>Select qualification type...</option>
							{#each qualifications as qual}
								<option value={qual.id}>{qual.name}</option>
							{/each}
						</select>
					</div>

					<!-- Degree Selection -->
					<div>
						<label for="degree" class="block text-sm font-medium text-gray-700 mb-1">
							Degree <span class="text-red-500">*</span>
						</label>
						<select
							id="degree"
							bind:value={formData.degree_id}
							class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							required
							disabled={!selectedQualificationId || loadingLookups}
						>
							<option value={0}>Select degree...</option>
							{#each filteredDegrees as degree}
								<option value={degree.id}>
									{degree.specialization} ({degree.degree_type})
								</option>
							{/each}
						</select>
						{#if !selectedQualificationId}
							<p class="mt-1 text-xs text-gray-500">Please select qualification type first</p>
						{/if}
					</div>

					<!-- Institute Selection -->
					<div>
						<label for="institute" class="block text-sm font-medium text-gray-700 mb-1">
							Institute <span class="text-red-500">*</span>
						</label>
						<div class="relative">
							<input
								type="text"
								placeholder="Search institute..."
								bind:value={instituteSearchQuery}
								oninput={handleInstituteSearch}
								class="w-full px-3 md:px-4 py-2 md:py-2.5 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							/>
							<div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
								<Search class="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
							</div>
						</div>
						<select
							id="institute"
							bind:value={formData.institute_id}
							class="mt-2 w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
							required
							disabled={loadingLookups || searchingInstitutes}
						>
							<option value={0}>Select institute...</option>
							{#each institutes as institute}
								<option value={institute.id}>
									{institute.name} {institute.city_name ? `(${institute.city_name})` : ''}
								</option>
							{/each}
						</select>
					</div>

					<!-- Date Range -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="from_date" class="block text-sm font-medium text-gray-700 mb-1">
								Start Date <span class="text-red-500">*</span>
							</label>
							<input
								type="date"
								id="from_date"
								bind:value={formData.from_date}
								class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
								required
							/>
						</div>

						<div>
							<label for="to_date" class="block text-sm font-medium text-gray-700 mb-1">
								End Date {#if !formData.current_education}<span class="text-red-500">*</span>{/if}
							</label>
							<input
								type="date"
								id="to_date"
								bind:value={formData.to_date}
								disabled={formData.current_education}
								class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed text-sm md:text-base"
								required={!formData.current_education}
							/>
						</div>
					</div>

					<!-- Current Education Checkbox -->
					<div class="flex items-center gap-2">
						<input
							type="checkbox"
							id="current_education"
							bind:checked={formData.current_education}
							class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
						/>
						<label for="current_education" class="text-sm font-medium text-gray-700">
							Currently pursuing this education
						</label>
					</div>

					<!-- Score -->
					<div>
						<label for="score" class="block text-sm font-medium text-gray-700 mb-1">
							Score / GPA
						</label>
						<input
							type="text"
							id="score"
							bind:value={formData.score}
							placeholder="e.g., 8.5 GPA, 85%, First Class"
							class="w-full px-3 md:px-4 py-2 md:py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm md:text-base"
						/>
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
							disabled={loading || loadingLookups}
						>
							{loading ? 'Saving...' : education ? 'Update Education' : 'Add Education'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

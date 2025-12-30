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
		current_education: false,
		custom_institute_name: ''
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
	let isOtherInstitute = $state(false);

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
				current_education: education.current_education,
				custom_institute_name: ''
			};
			isOtherInstitute = false;

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
				current_education: false,
				custom_institute_name: ''
			};
			selectedQualificationId = 0;
			isOtherInstitute = false;
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
		if (!isOtherInstitute && !formData.institute_id) {
			toast.error('Please select an institute or choose "Other"');
			return;
		}

		if (isOtherInstitute && !formData.custom_institute_name?.trim()) {
			toast.error('Please enter your institute name');
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
			// Prepare data for submission
			const submitData = { ...formData };
			if (isOtherInstitute) {
				// Clear institute_id when using custom name
				delete submitData.institute_id;
			} else {
				// Clear custom name when using selected institute
				delete submitData.custom_institute_name;
			}

			if (education) {
				// Update existing education
				await updateEducation(education.id, submitData);
				toast.success('Education updated successfully!');
			} else {
				// Add new education
				await addEducation(submitData);
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
			current_education: false,
			custom_institute_name: ''
		};
		selectedQualificationId = 0;
		instituteSearchQuery = '';
		isOtherInstitute = false;
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
			class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity cursor-default animate-fade-in"
			onclick={handleBackdropClick}
			aria-label="Close modal"
			tabindex="-1"
		></button>

		<!-- Modal -->
		<div class="flex min-h-screen items-center justify-center p-4">
			<div
				class="relative w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white elevation-4 transition-all animate-scale-in"
			>
				<!-- Header -->
				<div class="flex items-center justify-between border-b border-gray-100 p-5 lg:p-6">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
							<GraduationCap size={20} class="text-primary-600" />
						</div>
						<h3 class="text-lg font-semibold text-gray-900" id="modal-title">
							{education ? 'Edit Education' : 'Add Education'}
						</h3>
					</div>
					<button
						type="button"
						onclick={handleClose}
						class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
					>
						<X size={20} />
					</button>
				</div>

				<!-- Form -->
				<form onsubmit={handleSubmit} class="p-5 lg:p-6 space-y-5">
					<!-- Qualification Selection -->
					<div>
						<label for="qualification" class="block text-sm font-medium text-gray-700 mb-2">
							Qualification Type <span class="text-error-500">*</span>
						</label>
						<select
							id="qualification"
							bind:value={selectedQualificationId}
							onchange={handleQualificationChange}
							class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none appearance-none"
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
						<label for="degree" class="block text-sm font-medium text-gray-700 mb-2">
							Degree <span class="text-error-500">*</span>
						</label>
						<select
							id="degree"
							bind:value={formData.degree_id}
							class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none appearance-none disabled:bg-gray-100 disabled:cursor-not-allowed"
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
							<p class="mt-2 text-xs text-gray-500">Please select qualification type first</p>
						{/if}
					</div>

					<!-- Institute Selection -->
					<div>
						<label for="institute" class="block text-sm font-medium text-gray-700 mb-2">
							Institute <span class="text-error-500">*</span>
						</label>

						{#if !isOtherInstitute}
							<div class="relative">
								<span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
									<Search size={18} class="text-gray-400" />
								</span>
								<input
									type="text"
									placeholder="Search institute..."
									bind:value={instituteSearchQuery}
									oninput={handleInstituteSearch}
									class="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
								/>
							</div>
							<select
								id="institute"
								bind:value={formData.institute_id}
								class="mt-3 w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none appearance-none disabled:bg-gray-100 disabled:cursor-not-allowed"
								disabled={loadingLookups || searchingInstitutes}
							>
								<option value={0}>Select institute...</option>
								{#each institutes as institute}
									<option value={institute.id}>
										{institute.name} {institute.city_name ? `(${institute.city_name})` : ''}
									</option>
								{/each}
							</select>
							<button
								type="button"
								onclick={() => { isOtherInstitute = true; formData.institute_id = 0; }}
								class="mt-2 text-sm text-primary-600 hover:text-primary-700 font-medium"
							>
								Can't find your institute? Click here to enter manually
							</button>
						{:else}
							<input
								type="text"
								id="custom_institute"
								bind:value={formData.custom_institute_name}
								placeholder="Enter your institute name..."
								class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
							/>
							<button
								type="button"
								onclick={() => { isOtherInstitute = false; formData.custom_institute_name = ''; }}
								class="mt-2 text-sm text-primary-600 hover:text-primary-700 font-medium"
							>
								← Back to search from list
							</button>
						{/if}
					</div>

					<!-- Date Range -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="from_date" class="block text-sm font-medium text-gray-700 mb-2">
								Start Date <span class="text-error-500">*</span>
							</label>
							<input
								type="date"
								id="from_date"
								bind:value={formData.from_date}
								class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
								required
							/>
						</div>

						<div>
							<label for="to_date" class="block text-sm font-medium text-gray-700 mb-2">
								End Date {#if !formData.current_education}<span class="text-error-500">*</span>{/if}
							</label>
							<input
								type="date"
								id="to_date"
								bind:value={formData.to_date}
								disabled={formData.current_education}
								class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
								required={!formData.current_education}
							/>
						</div>
					</div>

					<!-- Current Education Checkbox -->
					<div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
						<label class="flex items-start gap-3 cursor-pointer">
							<input
								type="checkbox"
								id="current_education"
								bind:checked={formData.current_education}
								class="w-5 h-5 mt-0.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
							/>
							<div>
								<p class="font-medium text-gray-900">Currently pursuing</p>
								<p class="text-sm text-gray-600">Check this if you are currently pursuing this education</p>
							</div>
						</label>
					</div>

					<!-- Score -->
					<div>
						<label for="score" class="block text-sm font-medium text-gray-700 mb-2">
							Score / GPA
						</label>
						<input
							type="text"
							id="score"
							bind:value={formData.score}
							placeholder="e.g., 8.5 GPA, 85%, First Class"
							class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
						/>
					</div>

					<!-- Action Buttons -->
					<div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
						<button
							type="button"
							onclick={handleClose}
							class="px-5 py-2.5 text-gray-700 bg-white border border-gray-200 rounded-full font-medium hover:bg-gray-50 transition-colors"
							disabled={loading}
						>
							Cancel
						</button>
						<button
							type="submit"
							class="px-5 py-2.5 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed elevation-1"
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

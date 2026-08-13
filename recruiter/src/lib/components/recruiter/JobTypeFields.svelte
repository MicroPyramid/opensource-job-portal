<script lang="ts">
	/**
	 * The extra fields a walk-in or government post needs.
	 *
	 * The API has accepted these since the job serializer was written, but no
	 * form ever rendered them, so neither type could be posted from the
	 * dashboard at all — despite `walk-in` being the second most common type in
	 * the data and having its own landing pages on the job seeker site.
	 *
	 * Two render modes, because the create form is a wizard: `hidden` emits the
	 * named inputs that actually submit, so the values survive stepping away
	 * from the section that shows them. Render one of each per form — the
	 * visible one where it belongs, the hidden one alongside the other hidden
	 * inputs. Nothing is emitted for a type that has no extra fields.
	 */
	import { GOVERNMENT_JOB_TYPES } from '$lib/constants/jobs';
	import type { JobTypeSpecificFields } from '$lib/types';

	let {
		jobType,
		values = $bindable(),
		hidden = false,
		idPrefix = 'job'
	}: {
		jobType: string;
		values: JobTypeSpecificFields;
		hidden?: boolean;
		idPrefix?: string;
	} = $props();

	const WALKIN_FIELDS = [
		'walkin_contactinfo',
		'walkin_show_contact_info',
		'walkin_from_date',
		'walkin_to_date',
		'walkin_time'
	] as const;

	const GOVERNMENT_FIELDS = [
		'govt_job_type',
		'application_fee',
		'selection_process',
		'how_to_apply',
		'important_dates',
		'govt_from_date',
		'govt_to_date',
		'govt_exam_date',
		'age_relaxation'
	] as const;

	const submitted = $derived(
		jobType === 'walk-in' ? WALKIN_FIELDS : jobType === 'government' ? GOVERNMENT_FIELDS : []
	);

	const inputClass =
		'w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary';
</script>

{#if hidden}
	{#each submitted as name}
		<input type="hidden" {name} value={values[name]} />
	{/each}
{:else if jobType === 'walk-in'}
	<div class="space-y-4">
		<div>
			<h3 class="font-semibold text-black">Walk-in Details</h3>
			<p class="text-sm text-muted">When and where candidates should turn up.</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<div>
				<label for="{idPrefix}-walkin-from" class="block text-sm font-medium text-muted mb-2">
					From Date
				</label>
				<input
					id="{idPrefix}-walkin-from"
					type="date"
					bind:value={values.walkin_from_date}
					class={inputClass}
				/>
			</div>

			<div>
				<label for="{idPrefix}-walkin-to" class="block text-sm font-medium text-muted mb-2">
					To Date
				</label>
				<input
					id="{idPrefix}-walkin-to"
					type="date"
					bind:value={values.walkin_to_date}
					class={inputClass}
				/>
			</div>

			<div>
				<label for="{idPrefix}-walkin-time" class="block text-sm font-medium text-muted mb-2">
					Time
				</label>
				<input
					id="{idPrefix}-walkin-time"
					type="time"
					bind:value={values.walkin_time}
					class={inputClass}
				/>
			</div>
		</div>

		<div>
			<label for="{idPrefix}-walkin-contact" class="block text-sm font-medium text-muted mb-2">
				Contact Details
			</label>
			<textarea
				id="{idPrefix}-walkin-contact"
				rows="3"
				bind:value={values.walkin_contactinfo}
				placeholder="Name, phone number and venue address"
				class={inputClass}
			></textarea>
		</div>

		<label class="flex items-center gap-3 text-sm text-muted">
			<input
				type="checkbox"
				bind:checked={values.walkin_show_contact_info}
				class="w-4 h-4 rounded border-border text-primary focus:ring-primary/20"
			/>
			Show these contact details publicly on the job listing
		</label>
	</div>
{:else if jobType === 'government'}
	<div class="space-y-4">
		<div>
			<h3 class="font-semibold text-black">Government Job Details</h3>
			<p class="text-sm text-muted">Notification dates, fees and the selection process.</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<div>
				<label for="{idPrefix}-govt-type" class="block text-sm font-medium text-muted mb-2">
					Government Level
				</label>
				<!--
					No blank option: govt_job_type is a choice field with no blank=True,
					so an empty value is a 400 from the serializer. It defaults to
					Central, same as the model.
				-->
				<select id="{idPrefix}-govt-type" bind:value={values.govt_job_type} class={inputClass}>
					{#each GOVERNMENT_JOB_TYPES as level}
						<option value={level.value}>{level.label}</option>
					{/each}
				</select>
			</div>

			<div>
				<label for="{idPrefix}-govt-fee" class="block text-sm font-medium text-muted mb-2">
					Application Fee
				</label>
				<!-- IntegerField on the model, so digits only -->
				<input
					id="{idPrefix}-govt-fee"
					type="number"
					min="0"
					bind:value={values.application_fee}
					placeholder="500"
					class={inputClass}
				/>
			</div>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<div>
				<label for="{idPrefix}-govt-from" class="block text-sm font-medium text-muted mb-2">
					Applications Open
				</label>
				<input
					id="{idPrefix}-govt-from"
					type="date"
					bind:value={values.govt_from_date}
					class={inputClass}
				/>
			</div>

			<div>
				<label for="{idPrefix}-govt-to" class="block text-sm font-medium text-muted mb-2">
					Applications Close
				</label>
				<input
					id="{idPrefix}-govt-to"
					type="date"
					bind:value={values.govt_to_date}
					class={inputClass}
				/>
			</div>

			<div>
				<label for="{idPrefix}-govt-exam" class="block text-sm font-medium text-muted mb-2">
					Exam Date
				</label>
				<input
					id="{idPrefix}-govt-exam"
					type="date"
					bind:value={values.govt_exam_date}
					class={inputClass}
				/>
			</div>
		</div>

		<div>
			<label for="{idPrefix}-govt-selection" class="block text-sm font-medium text-muted mb-2">
				Selection Process
			</label>
			<textarea
				id="{idPrefix}-govt-selection"
				rows="3"
				bind:value={values.selection_process}
				placeholder="e.g., Written exam, followed by interview and document verification"
				class={inputClass}
			></textarea>
		</div>

		<div>
			<label for="{idPrefix}-govt-apply" class="block text-sm font-medium text-muted mb-2">
				How to Apply
			</label>
			<textarea
				id="{idPrefix}-govt-apply"
				rows="3"
				bind:value={values.how_to_apply}
				placeholder="Steps candidates should follow, including the official portal"
				class={inputClass}
			></textarea>
		</div>

		<div>
			<label for="{idPrefix}-govt-dates" class="block text-sm font-medium text-muted mb-2">
				Important Dates
			</label>
			<textarea
				id="{idPrefix}-govt-dates"
				rows="2"
				bind:value={values.important_dates}
				placeholder="Any other dates candidates need — admit card, results"
				class={inputClass}
			></textarea>
		</div>

		<div>
			<label for="{idPrefix}-govt-age" class="block text-sm font-medium text-muted mb-2">
				Age Relaxation
			</label>
			<input
				id="{idPrefix}-govt-age"
				type="text"
				bind:value={values.age_relaxation}
				placeholder="e.g., 5 years for SC/ST, 3 years for OBC"
				class={inputClass}
			/>
		</div>
	</div>
{/if}

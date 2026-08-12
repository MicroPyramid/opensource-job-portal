<script lang="ts">
	import { getContext } from 'svelte';
	import { enhance } from '$app/forms';
	import { Building2, Mail, UserCircle } from '@lucide/svelte';
	import { Button } from '$lib/components/ui';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	let { data, form } = $props();

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-lg';

	let accountType = $state<'company' | 'recruiter'>('company');
	let loading = $state(false);

	let error = $derived(form?.error || '');
	let values = $derived((form?.values ?? {}) as Record<string, string>);

	// Must match the ChoiceField in GoogleCompleteSerializer — the value is the
	// wire format, the text is only for reading.
	const companySizes = [
		{ value: '1-10', label: '1-10 employees' },
		{ value: '11-20', label: '11-20 employees' },
		{ value: '21-50', label: '21-50 employees' },
		{ value: '50-200', label: '50-200 employees' },
		{ value: '200+', label: '200+ employees' }
	];

	const industries = [
		'Technology',
		'Finance',
		'Healthcare',
		'Education',
		'Retail',
		'Manufacturing',
		'Consulting',
		'Media',
		'Real Estate',
		'Other'
	];

	const inputClass =
		'w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary';
</script>

<svelte:head>
	<title>Finish signing up - PeelJobs Recruiter</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<div class="bg-white rounded-lg shadow-sm border border-border p-6 sm:p-8">
	<h1 class="text-2xl font-semibold text-black">Almost there</h1>
	<p class="mt-1 text-sm text-muted">
		We have your Google details. Tell us where you are hiring and your account is ready.
	</p>

	<!-- What Google gave us. Shown so it is obvious which account is being
	     created, but not editable — it comes from the signed token, not the form. -->
	<div class="mt-6 flex items-center gap-3 p-3 bg-surface rounded-lg">
		<UserCircle class="w-5 h-5 text-muted flex-shrink-0" />
		<div class="min-w-0">
			<p class="text-sm font-medium text-black truncate">
				{data.firstName}
				{data.lastName}
			</p>
			<p class="text-xs text-muted truncate flex items-center gap-1">
				<Mail class="w-3 h-3 flex-shrink-0" />
				{data.email}
			</p>
		</div>
	</div>

	{#if error}
		<div
			class="mt-4 p-3 bg-error-light border border-error/30 text-error rounded-lg text-sm whitespace-pre-line"
		>
			{error}
		</div>
	{/if}

	<form
		method="POST"
		use:enhance={() => {
			loading = true;
			return async ({ update }) => {
				loading = false;
				await update({ reset: false });
			};
		}}
		class="mt-6 space-y-4"
	>
		<fieldset>
			<legend class="block text-sm font-medium text-muted mb-2">I am</legend>
			<div class="grid grid-cols-2 gap-3">
				<label
					class="flex items-center gap-2 px-3 py-2.5 border rounded-lg cursor-pointer text-sm transition-colors {accountType ===
					'company'
						? 'border-primary bg-primary/5 text-black'
						: 'border-border text-muted hover:bg-surface'}"
				>
					<input
						type="radio"
						name="account_type"
						value="company"
						bind:group={accountType}
						class="sr-only"
					/>
					<Building2 class="w-4 h-4" />
					Hiring for a company
				</label>

				<label
					class="flex items-center gap-2 px-3 py-2.5 border rounded-lg cursor-pointer text-sm transition-colors {accountType ===
					'recruiter'
						? 'border-primary bg-primary/5 text-black'
						: 'border-border text-muted hover:bg-surface'}"
				>
					<input
						type="radio"
						name="account_type"
						value="recruiter"
						bind:group={accountType}
						class="sr-only"
					/>
					<UserCircle class="w-4 h-4" />
					Independent recruiter
				</label>
			</div>
		</fieldset>

		{#if accountType === 'company'}
			<div>
				<label for="company_name" class="block text-sm font-medium text-muted mb-2">
					Company name
				</label>
				<input
					type="text"
					id="company_name"
					name="company_name"
					required
					value={values.company_name ?? ''}
					placeholder="Acme Inc."
					class={inputClass}
				/>
			</div>

			<div>
				<label for="company_website" class="block text-sm font-medium text-muted mb-2">
					Company website
				</label>
				<input
					type="url"
					id="company_website"
					name="company_website"
					required
					value={values.company_website ?? ''}
					placeholder="https://acme.com"
					class={inputClass}
				/>
			</div>

			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
				<div>
					<label for="company_industry" class="block text-sm font-medium text-muted mb-2">
						Industry
					</label>
					<select
						id="company_industry"
						name="company_industry"
						value={values.company_industry ?? ''}
						class={inputClass}
					>
						<option value="">Select…</option>
						{#each industries as industry (industry)}
							<option value={industry}>{industry}</option>
						{/each}
					</select>
				</div>

				<div>
					<label for="company_size" class="block text-sm font-medium text-muted mb-2">
						Company size
					</label>
					<select
						id="company_size"
						name="company_size"
						value={values.company_size ?? ''}
						class={inputClass}
					>
						<option value="">Select…</option>
						{#each companySizes as size (size.value)}
							<option value={size.value}>{size.label}</option>
						{/each}
					</select>
				</div>
			</div>
		{/if}

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
			<div>
				<label for="job_title" class="block text-sm font-medium text-muted mb-2">
					Your job title <span class="text-muted/70">(optional)</span>
				</label>
				<input
					type="text"
					id="job_title"
					name="job_title"
					value={values.job_title ?? ''}
					placeholder="Talent Lead"
					class={inputClass}
				/>
			</div>

			<div>
				<label for="phone" class="block text-sm font-medium text-muted mb-2">
					Phone <span class="text-muted/70">(optional)</span>
				</label>
				<input
					type="tel"
					id="phone"
					name="phone"
					value={values.phone ?? ''}
					placeholder="+91 98765 43210"
					class={inputClass}
				/>
			</div>
		</div>

		<label class="flex items-start gap-2 cursor-pointer pt-2">
			<input
				type="checkbox"
				name="agree_to_terms"
				required
				class="mt-0.5 w-4 h-4 text-primary border-border rounded focus:ring-primary/20 focus:ring-2"
			/>
			<span class="text-sm text-muted">
				I agree to the
				<a href="/terms/" class="text-primary hover:text-primary-hover">Terms of Service</a>
				and
				<a href="/privacy/" class="text-primary hover:text-primary-hover">Privacy Policy</a>
			</span>
		</label>

		<Button type="submit" size="lg" {loading} class="w-full">
			{loading ? 'Creating your account…' : 'Create account'}
		</Button>
	</form>

	<p class="mt-6 text-center text-sm text-muted">
		Wrong account?
		<a href="/login/" class="font-medium text-primary hover:text-primary-hover">Start over</a>
	</p>
</div>

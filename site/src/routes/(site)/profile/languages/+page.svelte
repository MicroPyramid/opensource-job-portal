<script lang="ts">
	import { onMount } from 'svelte';
	import { Languages, Plus, Trash2, Loader } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';
	import {
		getLanguageOptions,
		getMyLanguages,
		addLanguage,
		updateLanguage,
		deleteLanguage,
		type LanguageOption,
		type UserLanguage
	} from '$lib/api/languages';

	let options: LanguageOption[] = $state([]);
	let myLanguages: UserLanguage[] = $state([]);
	let loading = $state(true);
	let saving = $state(false);
	// Row id awaiting delete confirmation. Inline rather than confirm(), which
	// blocks the page and cannot be styled.
	let confirmingDelete: number | null = $state(null);

	let newLanguage = $state({ language: 0, read: true, write: false, speak: false });

	// Only offer languages the user has not already added — the API rejects
	// duplicates, so showing them would just produce an error.
	let available = $derived(
		options.filter((option) => !myLanguages.some((entry) => entry.language === option.id))
	);

	onMount(load);

	async function load() {
		loading = true;
		try {
			[options, myLanguages] = await Promise.all([getLanguageOptions(), getMyLanguages()]);
		} catch (error) {
			console.error('Failed to load languages:', error);
			toast.error('Failed to load languages');
		} finally {
			loading = false;
		}
	}

	async function handleAdd(event: SubmitEvent) {
		event.preventDefault();

		if (!newLanguage.language) {
			toast.error('Pick a language');
			return;
		}
		if (!newLanguage.read && !newLanguage.write && !newLanguage.speak) {
			toast.error('Select at least one of read, write or speak');
			return;
		}

		try {
			saving = true;
			await addLanguage(newLanguage);
			toast.success('Language added');
			newLanguage = { language: 0, read: true, write: false, speak: false };
			await load();
		} catch (error) {
			console.error('Failed to add language:', error);
			toast.error(error instanceof Error ? error.message : 'Failed to add language');
		} finally {
			saving = false;
		}
	}

	async function toggle(entry: UserLanguage, field: 'read' | 'write' | 'speak') {
		const next = { ...entry, [field]: !entry[field] };

		if (!next.read && !next.write && !next.speak) {
			toast.error('Keep at least one of read, write or speak — or remove the language');
			return;
		}

		try {
			await updateLanguage(entry.id, { [field]: next[field] });
			myLanguages = myLanguages.map((item) => (item.id === entry.id ? next : item));
		} catch (error) {
			console.error('Failed to update language:', error);
			toast.error('Failed to update language');
		}
	}

	async function handleDelete(id: number) {
		try {
			await deleteLanguage(id);
			toast.success('Language removed');
			confirmingDelete = null;
			await load();
		} catch (error) {
			console.error('Failed to remove language:', error);
			toast.error('Failed to remove language');
		}
	}
</script>

<svelte:head>
	<title>Languages | PeelJobs</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<div class="mx-auto max-w-3xl px-4 py-8">
	<div class="mb-6 flex items-center gap-3">
		<div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50">
			<Languages size={20} class="text-primary-600" />
		</div>
		<div>
			<h1 class="text-lg font-semibold text-gray-900">Languages</h1>
			<p class="text-sm text-gray-600">Languages you can read, write or speak</p>
		</div>
	</div>

	{#if loading}
		<div class="flex justify-center py-12">
			<Loader size={28} class="animate-spin text-primary-600" />
		</div>
	{:else}
		<div class="mb-6 overflow-hidden rounded-lg border border-border bg-white shadow-sm">
			{#if myLanguages.length === 0}
				<p class="px-5 py-8 text-center text-sm text-gray-600">
					You haven't added any languages yet.
				</p>
			{:else}
				<ul class="divide-y divide-border">
					{#each myLanguages as entry (entry.id)}
						<li class="flex flex-wrap items-center gap-4 px-5 py-4">
							<span class="min-w-32 font-medium text-gray-900">{entry.language_name}</span>

							<div class="flex flex-wrap gap-4">
								{#each ['read', 'write', 'speak'] as const as field}
									<label class="flex items-center gap-2 text-sm text-gray-700">
										<input
											type="checkbox"
											checked={entry[field]}
											onchange={() => toggle(entry, field)}
											class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
										/>
										<span class="capitalize">{field}</span>
									</label>
								{/each}
							</div>

							<div class="ml-auto">
								{#if confirmingDelete === entry.id}
									<div class="flex items-center gap-2">
										<button
											type="button"
											onclick={() => handleDelete(entry.id)}
											class="rounded-lg bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
										>
											Remove
										</button>
										<button
											type="button"
											onclick={() => (confirmingDelete = null)}
											class="rounded-lg px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900"
										>
											Cancel
										</button>
									</div>
								{:else}
									<button
										type="button"
										onclick={() => (confirmingDelete = entry.id)}
										aria-label="Remove {entry.language_name}"
										class="rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-600"
									>
										<Trash2 size={16} />
									</button>
								{/if}
							</div>
						</li>
					{/each}
				</ul>
			{/if}
		</div>

		{#if available.length > 0}
			<form
				onsubmit={handleAdd}
				class="rounded-lg border border-border bg-white p-5 shadow-sm"
				aria-labelledby="add-language-heading"
			>
				<h2 id="add-language-heading" class="mb-4 text-sm font-semibold text-gray-900">
					Add a language
				</h2>

				<div class="flex flex-wrap items-end gap-4">
					<div class="min-w-48 flex-1">
						<label class="mb-1 block text-sm font-medium text-gray-700" for="language-select">
							Language
						</label>
						<select
							id="language-select"
							bind:value={newLanguage.language}
							class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
						>
							<option value={0}>Select a language</option>
							{#each available as option (option.id)}
								<option value={option.id}>{option.name}</option>
							{/each}
						</select>
					</div>

					<div class="flex flex-wrap gap-4 pb-2">
						{#each ['read', 'write', 'speak'] as const as field}
							<label class="flex items-center gap-2 text-sm text-gray-700">
								<input
									type="checkbox"
									bind:checked={newLanguage[field]}
									class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
								/>
								<span class="capitalize">{field}</span>
							</label>
						{/each}
					</div>

					<button
						type="submit"
						disabled={saving}
						class="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-60"
					>
						{#if saving}
							<Loader size={16} class="animate-spin" />
						{:else}
							<Plus size={16} />
						{/if}
						Add
					</button>
				</div>
			</form>
		{/if}
	{/if}
</div>

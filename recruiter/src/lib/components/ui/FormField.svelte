<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		label?: string;
		error?: string;
		hint?: string;
		required?: boolean;
		children: Snippet;
		class?: string;
	}

	let {
		label,
		error,
		hint,
		required = false,
		children,
		class: className = ''
	}: Props = $props();
</script>

<div class="space-y-1.5 {className}">
	{#if label}
		<!-- svelte-ignore a11y_label_has_associated_control -->
		<label class="block text-sm font-medium text-black">
			{label}
			{#if required}
				<span class="text-error">*</span>
			{/if}
		</label>
	{/if}

	{@render children()}

	{#if error}
		<p class="text-sm text-error">{error}</p>
	{:else if hint}
		<p class="text-sm text-muted">{hint}</p>
	{/if}
</div>

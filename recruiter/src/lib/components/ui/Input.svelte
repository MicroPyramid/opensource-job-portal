<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLInputAttributes } from 'svelte/elements';

	type Size = 'sm' | 'md' | 'lg';

	interface Props extends HTMLInputAttributes {
		size?: Size;
		error?: boolean;
		iconLeft?: Snippet;
		iconRight?: Snippet;
		class?: string;
	}

	let {
		size = 'md',
		error = false,
		iconLeft,
		iconRight,
		class: className = '',
		...restProps
	}: Props = $props();

	const baseClasses =
		'w-full border bg-white transition-colors placeholder:text-muted/60 focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed';

	const sizeClasses: Record<Size, string> = {
		sm: 'h-8 px-3 text-sm rounded-lg',
		md: 'h-10 px-3 text-sm rounded-lg',
		lg: 'h-12 px-4 text-base rounded-lg'
	};

	const stateClasses = $derived(error ? 'border-error focus:border-error focus:ring-error/20' : 'border-border');

	const paddingLeft = $derived(iconLeft ? 'pl-10' : '');
	const paddingRight = $derived(iconRight ? 'pr-10' : '');

	const classes = $derived(
		`${baseClasses} ${sizeClasses[size]} ${stateClasses} ${paddingLeft} ${paddingRight} ${className}`
	);
</script>

<div class="relative">
	{#if iconLeft}
		<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-muted">
			{@render iconLeft()}
		</div>
	{/if}

	<input class={classes} {...restProps} />

	{#if iconRight}
		<div class="absolute inset-y-0 right-0 flex items-center pr-3 text-muted">
			{@render iconRight()}
		</div>
	{/if}
</div>

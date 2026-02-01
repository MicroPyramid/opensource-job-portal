<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLAttributes } from 'svelte/elements';

	interface Props extends HTMLAttributes<HTMLDivElement> {
		hover?: boolean;
		padding?: 'none' | 'sm' | 'md' | 'lg';
		children: Snippet;
		class?: string;
	}

	let {
		hover = false,
		padding = 'md',
		children,
		class: className = '',
		...restProps
	}: Props = $props();

	const baseClasses = 'bg-white border border-border rounded-lg';

	const hoverClasses = $derived(hover ? 'hover:shadow-md transition-shadow cursor-pointer' : 'shadow-sm');

	const paddingClasses: Record<string, string> = {
		none: '',
		sm: 'p-3',
		md: 'p-4',
		lg: 'p-6'
	};

	const classes = $derived(
		`${baseClasses} ${hoverClasses} ${paddingClasses[padding]} ${className}`
	);
</script>

<div class={classes} {...restProps}>
	{@render children()}
</div>

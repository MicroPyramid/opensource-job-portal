<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variant = 'primary' | 'success' | 'warning' | 'error' | 'neutral';
	type Size = 'sm' | 'md';

	interface Props {
		variant?: Variant;
		size?: Size;
		children: Snippet;
		class?: string;
	}

	let { variant = 'primary', size = 'md', children, class: className = '' }: Props = $props();

	const baseClasses = 'inline-flex items-center font-medium rounded';

	const sizeClasses: Record<Size, string> = {
		sm: 'px-1.5 py-0.5 text-[11px]',
		md: 'px-2 py-0.5 text-xs'
	};

	const variantClasses: Record<Variant, string> = {
		primary: 'bg-primary/10 text-primary',
		success: 'bg-success-light text-success',
		warning: 'bg-warning-light text-warning',
		error: 'bg-error-light text-error',
		neutral: 'bg-surface text-muted'
	};

	const classes = $derived(
		`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`
	);
</script>

<span class={classes}>
	{@render children()}
</span>

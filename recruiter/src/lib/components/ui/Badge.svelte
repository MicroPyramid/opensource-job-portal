<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variant = 'primary' | 'success' | 'warning' | 'error' | 'neutral';

	interface Props {
		variant?: Variant;
		children: Snippet;
		class?: string;
	}

	let { variant = 'primary', children, class: className = '' }: Props = $props();

	const baseClasses = 'inline-flex items-center px-2 py-0.5 text-xs font-medium rounded';

	const variantClasses: Record<Variant, string> = {
		primary: 'bg-primary/10 text-primary',
		success: 'bg-success-light text-success',
		warning: 'bg-warning-light text-warning',
		error: 'bg-error-light text-error',
		neutral: 'bg-surface text-muted'
	};

	const classes = $derived(`${baseClasses} ${variantClasses[variant]} ${className}`);
</script>

<span class={classes}>
	{@render children()}
</span>

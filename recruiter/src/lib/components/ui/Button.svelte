<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLAnchorAttributes, HTMLAttributes, HTMLButtonAttributes } from 'svelte/elements';

	type Variant = 'primary' | 'secondary' | 'ghost';
	type Size = 'sm' | 'md' | 'lg';

	// Renders as <a> when `href` is set, otherwise <button>. The base is the
	// element-agnostic HTMLAttributes so the rest props spread onto either tag;
	// the tag-specific attributes we actually support are listed explicitly.
	interface Props extends HTMLAttributes<HTMLElement> {
		variant?: Variant;
		size?: Size;
		loading?: boolean;
		disabled?: boolean;
		type?: HTMLButtonAttributes['type'];
		href?: HTMLAnchorAttributes['href'];
		target?: HTMLAnchorAttributes['target'];
		rel?: HTMLAnchorAttributes['rel'];
		download?: HTMLAnchorAttributes['download'];
		children: Snippet;
		class?: string;
	}

	let {
		variant = 'primary',
		size = 'md',
		loading = false,
		disabled = false,
		type = 'button',
		href,
		children,
		class: className = '',
		...restProps
	}: Props = $props();

	const baseClasses =
		'inline-flex items-center justify-center font-semibold transition-colors focus-visible:ring-2 focus-visible:ring-primary/20 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

	const variantClasses: Record<Variant, string> = {
		primary: 'bg-primary text-white hover:bg-primary-hover',
		secondary: 'border border-primary text-primary hover:bg-primary/5',
		ghost: 'text-muted hover:bg-surface'
	};

	const sizeClasses: Record<Size, string> = {
		sm: 'h-8 px-3 text-sm rounded-full gap-1.5',
		md: 'h-10 px-4 text-sm rounded-full gap-2',
		lg: 'h-12 px-6 text-base rounded-full gap-2'
	};

	const classes = $derived(
		`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`
	);
</script>

{#snippet content()}
	{#if loading}
		<svg
			class="h-4 w-4 animate-spin"
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24"
			aria-hidden="true"
		>
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
			></circle>
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			></path>
		</svg>
	{/if}
	{@render children()}
{/snippet}

{#if href}
	<a
		{href}
		class={classes}
		aria-disabled={disabled || loading ? 'true' : undefined}
		{...restProps}
	>
		{@render content()}
	</a>
{:else}
	<button class={classes} disabled={disabled || loading} {type} {...restProps}>
		{@render content()}
	</button>
{/if}

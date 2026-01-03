<script lang="ts">
	type Size = 'xs' | 'sm' | 'md' | 'lg';
	type Shape = 'circle' | 'rounded';

	interface Props {
		src?: string | null;
		alt?: string;
		size?: Size;
		shape?: Shape;
		fallback?: string;
		class?: string;
	}

	let {
		src = null,
		alt = '',
		size = 'md',
		shape = 'circle',
		fallback = '',
		class: className = ''
	}: Props = $props();

	const sizeClasses: Record<Size, string> = {
		xs: 'w-6 h-6 text-xs',
		sm: 'w-8 h-8 text-sm',
		md: 'w-12 h-12 text-base',
		lg: 'w-18 h-18 text-xl'
	};

	const shapeClasses: Record<Shape, string> = {
		circle: 'rounded-full',
		rounded: 'rounded-lg'
	};

	const initials = $derived(
		fallback ||
			alt
				.split(' ')
				.map((word) => word[0])
				.join('')
				.toUpperCase()
				.slice(0, 2)
	);

	const classes = $derived(
		`${sizeClasses[size]} ${shapeClasses[shape]} ${className}`
	);
</script>

{#if src}
	<img {src} {alt} class="{classes} object-cover" />
{:else}
	<div
		class="{classes} flex items-center justify-center bg-primary/10 text-primary font-medium"
	>
		{initials}
	</div>
{/if}

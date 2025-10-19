<script lang="ts">
	import { toast, type Toast } from '$lib/stores/toast';
	import { CheckCircle, AlertCircle, Info, AlertTriangle, X } from '@lucide/svelte';
	import { fade, fly } from 'svelte/transition';

	let toasts: Toast[] = [];

	toast.subscribe((store) => {
		toasts = store.toasts;
	});

	function getIcon(type: Toast['type']) {
		switch (type) {
			case 'success':
				return CheckCircle;
			case 'error':
				return AlertCircle;
			case 'warning':
				return AlertTriangle;
			case 'info':
			default:
				return Info;
		}
	}

	function getStyles(type: Toast['type']) {
		switch (type) {
			case 'success':
				return 'bg-green-50 border-green-200 text-green-800';
			case 'error':
				return 'bg-red-50 border-red-200 text-red-800';
			case 'warning':
				return 'bg-yellow-50 border-yellow-200 text-yellow-800';
			case 'info':
			default:
				return 'bg-blue-50 border-blue-200 text-blue-800';
		}
	}

	function getIconColor(type: Toast['type']) {
		switch (type) {
			case 'success':
				return 'text-green-600';
			case 'error':
				return 'text-red-600';
			case 'warning':
				return 'text-yellow-600';
			case 'info':
			default:
				return 'text-blue-600';
		}
	}
</script>

<!-- Toast Container -->
<div class="fixed top-4 right-4 z-50 flex flex-col gap-3 max-w-md">
	{#each toasts as toastItem (toastItem.id)}
		<div
			class="flex items-start gap-3 p-4 rounded-lg border shadow-lg {getStyles(toastItem.type)}"
			transition:fly={{ y: -20, duration: 300 }}
		>
			<svelte:component
				this={getIcon(toastItem.type)}
				class="w-5 h-5 flex-shrink-0 {getIconColor(toastItem.type)}"
			/>
			<p class="flex-1 text-sm font-medium">{toastItem.message}</p>
			<button
				onclick={() => toast.dismiss(toastItem.id)}
				class="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
				aria-label="Dismiss"
			>
				<X class="w-4 h-4" />
			</button>
		</div>
	{/each}
</div>

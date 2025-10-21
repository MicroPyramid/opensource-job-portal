<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	onMount(() => {
		// Check if user is authenticated (this would check for auth token/cookie)
		const isAuthenticated = false; // Replace with actual auth check

		if (isAuthenticated) {
			goto('/dashboard/');
		} else {
			goto('/login/');
		}
	});
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50">
	<div class="text-center">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
		<p class="mt-4 text-gray-600">Loading...</p>
	</div>
</div>

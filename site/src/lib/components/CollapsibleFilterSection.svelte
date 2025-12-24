<script lang="ts">
  import { ChevronDown, ChevronUp } from '@lucide/svelte';
  import type { Snippet } from 'svelte';

  interface Props {
    title: string;
    defaultExpanded?: boolean;
    hasActiveFilter?: boolean;
    children: Snippet;
  }

  let { title, defaultExpanded = true, hasActiveFilter = false, children }: Props = $props();

  let isExpanded = $state(true);

  // Sync with prop on mount
  $effect(() => {
    isExpanded = defaultExpanded;
  });

  function toggleExpanded() {
    isExpanded = !isExpanded;
  }
</script>

<div class="border-b border-gray-100">
  <!-- Header - Clickable to expand/collapse -->
  <button
    type="button"
    onclick={toggleExpanded}
    class="w-full px-4 py-3.5 flex items-center justify-between hover:bg-surface-50 transition-colors text-left group"
  >
    <h3 class="text-sm font-medium text-gray-900 flex items-center gap-2">
      <span>{title}</span>
      {#if hasActiveFilter}
        <span class="w-2 h-2 rounded-full bg-primary-600"></span>
      {/if}
    </h3>
    <div class="flex items-center">
      {#if isExpanded}
        <ChevronUp class="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
      {:else}
        <ChevronDown class="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
      {/if}
    </div>
  </button>

  <!-- Body - Collapsible -->
  {#if isExpanded}
    <div class="px-4 pb-4">
      {@render children()}
    </div>
  {/if}
</div>

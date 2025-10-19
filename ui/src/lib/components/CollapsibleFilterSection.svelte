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

  let isExpanded = $state(defaultExpanded);

  function toggleExpanded() {
    isExpanded = !isExpanded;
  }
</script>

<div class="border-b border-gray-200">
  <!-- Header - Clickable to expand/collapse -->
  <button
    type="button"
    onclick={toggleExpanded}
    class="w-full px-4 py-3 bg-white flex items-center justify-between hover:bg-gray-50 transition-colors text-left"
  >
    <h3 class="text-sm font-medium text-gray-900">{title}</h3>
    <div class="flex items-center gap-1">
      {#if isExpanded}
        <ChevronUp class="w-4 h-4 text-gray-500" />
      {:else}
        <ChevronDown class="w-4 h-4 text-gray-500" />
      {/if}
    </div>
  </button>

  <!-- Body - Collapsible -->
  {#if isExpanded}
    <div class="px-4 pb-4 bg-white">
      {@render children()}
    </div>
  {/if}
</div>

<script lang="ts">
  import type { Component } from 'svelte';
  import { ChevronDown, ChevronUp } from '@lucide/svelte';

  interface FilterOption {
    name: string;
    value: string;
    count: number;
    checked: boolean;
  }

  interface Props {
    title: string;
    icon: Component;
    options: FilterOption[];
    showMoreButton?: boolean;
    onToggle: (value: string) => void;
    onShowMore?: () => void;
    maxVisible?: number;
    defaultExpanded?: boolean;
  }

  let {
    title,
    icon: Icon,
    options,
    showMoreButton = false,
    onToggle,
    onShowMore,
    maxVisible = 5,
    defaultExpanded = true
  }: Props = $props();

  let isExpanded = $state(true);

  // Sync with prop on mount
  $effect(() => {
    isExpanded = defaultExpanded;
  });

  const selectedCount = $derived(options.filter(opt => opt.checked).length);
  const visibleOptions = $derived(options.slice(0, maxVisible));

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
    <h3 class="text-sm font-medium text-gray-900 flex items-center gap-2">
      <Icon class="w-4 h-4 text-gray-600" />
      {title}
    </h3>
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
      <div class="space-y-2">
        {#each visibleOptions as option (option.value)}
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={option.checked}
              onchange={() => onToggle(option.value)}
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
              aria-label="Filter by {option.name}"
            />
            <span class="text-gray-700 flex-1 text-sm">{option.name}</span>
            <span class="text-gray-500 text-xs">({option.count.toLocaleString()})</span>
          </label>
        {/each}
      </div>

      {#if showMoreButton && options.length > maxVisible}
        <div class="mt-3">
          <button
            type="button"
            onclick={onShowMore}
            class="text-blue-600 hover:underline text-sm flex items-center gap-1"
          >
            View all {options.length} {title.toLowerCase()}
            <ChevronDown class="w-3.5 h-3.5" />
          </button>
        </div>
      {/if}
    </div>
  {/if}
</div>

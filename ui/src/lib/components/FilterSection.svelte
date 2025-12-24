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

<div class="border-b border-gray-100">
  <!-- Header - Clickable to expand/collapse -->
  <button
    type="button"
    onclick={toggleExpanded}
    class="w-full px-4 py-3.5 flex items-center justify-between hover:bg-surface-50 transition-colors text-left group"
  >
    <h3 class="text-sm font-medium text-gray-900 flex items-center gap-2.5">
      <div class="w-8 h-8 rounded-xl bg-primary-50 flex items-center justify-center">
        <Icon class="w-4 h-4 text-primary-600" />
      </div>
      <span>{title}</span>
      {#if selectedCount > 0}
        <span class="px-2 py-0.5 bg-primary-600 text-white text-xs font-medium rounded-full">
          {selectedCount}
        </span>
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
      <div class="space-y-1">
        {#each visibleOptions as option (option.value)}
          <label class="flex items-center gap-3 cursor-pointer py-2 px-2 -mx-2 rounded-xl hover:bg-surface-50 transition-colors group/item">
            <input
              type="checkbox"
              checked={option.checked}
              onchange={() => onToggle(option.value)}
              class="w-4 h-4 text-primary-600 border-gray-300 rounded-lg focus:ring-primary-500 focus:ring-2 cursor-pointer transition-colors"
              aria-label="Filter by {option.name}"
            />
            <span class="text-gray-700 flex-1 text-sm group-hover/item:text-gray-900 transition-colors">{option.name}</span>
            <span class="text-gray-400 text-xs font-medium bg-gray-100 px-2 py-0.5 rounded-full">
              {option.count.toLocaleString()}
            </span>
          </label>
        {/each}
      </div>

      {#if showMoreButton && options.length > maxVisible}
        <div class="mt-3 pt-3 border-t border-gray-100">
          <button
            type="button"
            onclick={onShowMore}
            class="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center gap-1.5 px-2 py-1.5 -mx-2 rounded-lg hover:bg-primary-50 transition-colors"
          >
            View all {options.length} {title.toLowerCase()}
            <ChevronDown class="w-4 h-4" />
          </button>
        </div>
      {/if}
    </div>
  {/if}
</div>

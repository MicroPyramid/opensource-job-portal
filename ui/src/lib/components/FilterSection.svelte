<script lang="ts">
  import type { Component } from 'svelte';

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
  }

  let {
    title,
    icon: Icon,
    options,
    showMoreButton = false,
    onToggle,
    onShowMore,
    maxVisible = 5
  }: Props = $props();

  const selectedCount = $derived(options.filter(opt => opt.checked).length);
  const visibleOptions = $derived(options.slice(0, maxVisible));
</script>

<div class="border border-gray-200 rounded-lg overflow-hidden">
  <!-- Header -->
  <div class="p-4 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
    <h3 class="font-medium text-gray-800 flex items-center gap-2">
      <Icon class="w-5 h-5 text-blue-600" />
      {title}
    </h3>
    {#if selectedCount > 0}
      <span class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
        {selectedCount}/{options.length}
      </span>
    {/if}
  </div>

  <!-- Body -->
  <div class="p-4 bg-white">
    <div class="space-y-2">
      {#each visibleOptions as option (option.value)}
        <label class="flex items-center space-x-2 text-sm cursor-pointer min-h-[44px] hover:bg-gray-50 -mx-2 px-2 rounded transition-colors">
          <input
            type="checkbox"
            checked={option.checked}
            onchange={() => onToggle(option.value)}
            class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 focus:ring-2"
            aria-label="Filter by {option.name}"
          />
          <span class="text-gray-700 flex-1">{option.name}</span>
          <span class="text-gray-500 text-sm">({option.count.toLocaleString()})</span>
        </label>
      {/each}
    </div>

    {#if showMoreButton && options.length > maxVisible}
      <div class="mt-3">
        <button
          type="button"
          onclick={onShowMore}
          class="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
        >
          Show more {title.toLowerCase()} →
        </button>
      </div>
    {/if}
  </div>
</div>

<script lang="ts">
  import { X } from '@lucide/svelte';

  interface FilterChip {
    label: string;
    value: string;
    type: 'location' | 'skill' | 'industry' | 'education' | 'job_type' | 'salary' | 'experience' | 'remote';
  }

  interface Props {
    chips: FilterChip[];
    onRemove: (chip: FilterChip) => void;
    onClearAll?: () => void;
  }

  let { chips, onRemove, onClearAll }: Props = $props();
</script>

{#if chips.length > 0}
  <div class="flex flex-wrap items-center gap-2 mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
    <span class="text-sm font-medium text-gray-700">Active Filters:</span>

    {#each chips as chip (chip.type + chip.value)}
      <button
        type="button"
        onclick={() => onRemove(chip)}
        class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-blue-300 text-blue-700 rounded-full text-sm hover:bg-blue-100 hover:border-blue-400 transition-all group"
      >
        <span>{chip.label}</span>
        <X class="w-3.5 h-3.5 text-blue-500 group-hover:text-blue-700" />
      </button>
    {/each}

    {#if onClearAll && chips.length > 1}
      <button
        type="button"
        onclick={onClearAll}
        class="ml-auto inline-flex items-center gap-1 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-full text-sm font-medium transition-colors"
      >
        <X class="w-4 h-4" />
        Clear All
      </button>
    {/if}
  </div>
{/if}

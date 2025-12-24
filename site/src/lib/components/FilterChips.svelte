<script lang="ts">
  import { X, SlidersHorizontal } from '@lucide/svelte';

  interface FilterChip {
    label: string;
    value: string;
    type: 'location' | 'skill' | 'industry' | 'education' | 'job_type' | 'salary' | 'experience' | 'remote' | 'fresher';
  }

  interface Props {
    chips: FilterChip[];
    onRemove: (chip: FilterChip) => void;
    onClearAll?: () => void;
  }

  let { chips, onRemove, onClearAll }: Props = $props();

  // Get chip color based on type
  function getChipStyle(type: FilterChip['type']): string {
    const styles: Record<FilterChip['type'], string> = {
      location: 'bg-primary-50 text-primary-700 border-primary-200',
      skill: 'bg-success-500/10 text-success-600 border-success-500/20',
      industry: 'bg-warning-500/10 text-warning-600 border-warning-500/20',
      education: 'bg-purple-50 text-purple-700 border-purple-200',
      job_type: 'bg-cyan-50 text-cyan-700 border-cyan-200',
      salary: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      experience: 'bg-amber-50 text-amber-700 border-amber-200',
      remote: 'bg-indigo-50 text-indigo-700 border-indigo-200',
      fresher: 'bg-pink-50 text-pink-700 border-pink-200'
    };
    return styles[type] || 'bg-gray-100 text-gray-700 border-gray-200';
  }
</script>

{#if chips.length > 0}
  <div class="flex flex-wrap items-center gap-2 mb-6 p-4 bg-surface-50 border border-gray-100 rounded-2xl">
    <div class="flex items-center gap-2 text-sm font-medium text-gray-600 mr-2">
      <SlidersHorizontal class="w-4 h-4" />
      <span>Filters:</span>
    </div>

    {#each chips as chip (chip.type + chip.value)}
      <button
        type="button"
        onclick={() => onRemove(chip)}
        class="inline-flex items-center gap-1.5 px-3 py-1.5 border rounded-full text-sm font-medium transition-all hover:opacity-80 group {getChipStyle(chip.type)}"
      >
        <span>{chip.label}</span>
        <X class="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 transition-opacity" />
      </button>
    {/each}

    {#if onClearAll && chips.length > 1}
      <button
        type="button"
        onclick={onClearAll}
        class="ml-auto inline-flex items-center gap-1.5 px-4 py-1.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full text-sm font-medium transition-colors"
      >
        <X class="w-4 h-4" />
        Clear All
      </button>
    {/if}
  </div>
{/if}

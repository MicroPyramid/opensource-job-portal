<script lang="ts">
  import { X, Search } from '@lucide/svelte';

  interface FilterOption {
    name: string;
    value: string;
    count: number;
    checked: boolean;
  }

  interface Props {
    title: string;
    options: FilterOption[];
    isOpen: boolean;
    onClose: () => void;
    onToggle: (value: string) => void;
    onApply: () => void;
  }

  let {
    title,
    options,
    isOpen = $bindable(),
    onClose,
    onToggle,
    onApply
  }: Props = $props();

  let searchTerm = $state('');

  const filteredOptions = $derived(
    options.filter(opt =>
      opt.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  const selectedCount = $derived(options.filter(opt => opt.checked).length);

  function handleClose() {
    searchTerm = '';
    onClose();
  }

  function handleApply() {
    searchTerm = '';
    onApply();
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  }
</script>

{#if isOpen}
  <!-- Modal Backdrop -->
  <div
    class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
    onclick={handleBackdropClick}
    onkeydown={(e) => {
      if (e.key === 'Escape') {
        handleClose();
      }
    }}
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
    tabindex="-1"
  >
    <!-- Modal Content -->
    <div
      class="bg-white rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
      role="document"
    >
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <h2 id="modal-title" class="text-xl font-semibold text-gray-800">
            Select {title}
          </h2>
          {#if selectedCount > 0}
            <span class="bg-blue-100 text-blue-700 text-sm px-3 py-1 rounded-full font-medium">
              {selectedCount} selected
            </span>
          {/if}
        </div>
        <button
          type="button"
          onclick={handleClose}
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Close modal"
        >
          <X class="w-6 h-6 text-gray-600" />
        </button>
      </div>

      <!-- Search -->
      <div class="p-6 border-b border-gray-200">
        <div class="relative">
          <input
            type="text"
            bind:value={searchTerm}
            placeholder="Search {title.toLowerCase()}..."
            class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
          />
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        </div>
      </div>

      <!-- Options Grid -->
      <div class="flex-1 overflow-y-auto p-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
          {#each filteredOptions as option (option.value)}
            <label
              class="flex items-center space-x-2 text-sm cursor-pointer min-h-[44px] hover:bg-gray-50 p-2 rounded transition-colors"
              data-location-name={option.name.toLowerCase()}
            >
              <input
                type="checkbox"
                checked={option.checked}
                onchange={() => onToggle(option.value)}
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 focus:ring-2"
                aria-label="Filter by {option.name}"
              />
              <span class="text-gray-700 flex-1">{option.name}</span>
              <span class="text-gray-500 text-xs">({option.count.toLocaleString()})</span>
            </label>
          {/each}
        </div>

        {#if filteredOptions.length === 0}
          <div class="text-center py-12">
            <Search class="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <p class="text-gray-600">No {title.toLowerCase()} found matching "{searchTerm}"</p>
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-200 flex gap-3">
        <button
          type="button"
          onclick={handleClose}
          class="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
        >
          Cancel
        </button>
        <button
          type="button"
          onclick={handleApply}
          class="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
        >
          Apply Filters
        </button>
      </div>
    </div>
  </div>
{/if}

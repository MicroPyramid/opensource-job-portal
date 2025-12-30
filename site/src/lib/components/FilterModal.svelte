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
    closeOnSelect?: boolean; // New prop to close after selection
  }

  let {
    title,
    options,
    isOpen = $bindable(),
    onClose,
    onToggle,
    onApply,
    closeOnSelect = false
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

  function handleToggle(value: string) {
    onToggle(value);
    // If closeOnSelect is true, close the modal after toggling
    if (closeOnSelect) {
      // Close immediately using multiple methods to ensure it works
      searchTerm = '';
      isOpen = false;
      onClose();
    }
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
    class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in"
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
      class="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col elevation-4 animate-scale-in"
      role="document"
    >
      <!-- Header -->
      <div class="p-6 border-b border-gray-100 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <h2 id="modal-title" class="text-xl font-semibold text-gray-900">
            Select {title}
          </h2>
          {#if selectedCount > 0}
            <span class="bg-primary-50 text-primary-700 text-sm px-3 py-1 rounded-full font-medium">
              {selectedCount} selected
            </span>
          {/if}
        </div>
        <button
          type="button"
          onclick={handleClose}
          class="p-2 hover:bg-gray-100 rounded-full transition-colors"
          aria-label="Close modal"
        >
          <X class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <!-- Search -->
      <div class="p-6 border-b border-gray-100">
        <div class="relative">
          <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search class="w-5 h-5 text-gray-400" />
          </span>
          <input
            type="text"
            bind:value={searchTerm}
            placeholder="Search {title.toLowerCase()}..."
            class="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
          />
        </div>
      </div>

      <!-- Options Grid -->
      <div class="flex-1 overflow-y-auto p-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
          {#each filteredOptions as option (option.value)}
            <label
              class="flex items-center gap-3 text-sm cursor-pointer min-h-[48px] hover:bg-surface-50 p-3 rounded-xl transition-colors border border-transparent {option.checked ? 'bg-primary-50 border-primary-200' : ''}"
              data-location-name={option.name.toLowerCase()}
            >
              <input
                type="checkbox"
                checked={option.checked}
                onchange={() => handleToggle(option.value)}
                class="w-4 h-4 text-primary-600 rounded-lg border-gray-300 focus:ring-primary-500 focus:ring-2"
                aria-label="Filter by {option.name}"
              />
              <span class="text-gray-700 flex-1 {option.checked ? 'text-primary-700 font-medium' : ''}">{option.name}</span>
              <span class="text-gray-400 text-xs font-medium">({option.count.toLocaleString()})</span>
            </label>
          {/each}
        </div>

        {#if filteredOptions.length === 0}
          <div class="text-center py-16">
            <div class="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <Search class="w-8 h-8 text-gray-400" />
            </div>
            <p class="text-gray-600 font-medium">No {title.toLowerCase()} found</p>
            <p class="text-gray-500 text-sm mt-1">Try a different search term</p>
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-100 flex gap-3 bg-surface-50 rounded-b-2xl">
        <button
          type="button"
          onclick={handleClose}
          class="flex-1 px-6 py-3 border border-gray-200 text-gray-700 rounded-full hover:bg-white hover:border-gray-300 transition-all font-medium"
        >
          Cancel
        </button>
        <button
          type="button"
          onclick={handleApply}
          class="flex-1 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-full transition-colors font-medium elevation-1 hover:elevation-2"
        >
          Apply Filters
        </button>
      </div>
    </div>
  </div>
{/if}

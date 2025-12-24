<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, Loader2 } from '@lucide/svelte';

  export let placeholder: string = 'Type to search...';
  export let value: string = '';
  export let icon: any = null;
  export let id: string = '';
  export let suggestions: Array<{ id: number; name: string; jobs_count?: number }> = [];
  export let loading: boolean = false;
  export let showJobCount: boolean = true;
  export let inputClass: string = '';

  const dispatch = createEventDispatcher<{
    search: string;
    select: { id: number; name: string };
    clear: void;
  }>();

  let showDropdown = false;
  let selectedIndex = -1;
  let inputElement: HTMLInputElement;

  // Debounce function
  let debounceTimer: ReturnType<typeof setTimeout>;
  function debounce(callback: () => void, delay: number = 300) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(callback, delay);
  }

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    value = target.value;
    selectedIndex = -1;

    debounce(() => {
      if (value.trim().length >= 2) {
        dispatch('search', value.trim());
        showDropdown = true;
      } else {
        showDropdown = false;
      }
    }, 300);
  }

  function handleSelect(suggestion: { id: number; name: string }) {
    value = suggestion.name;
    dispatch('select', suggestion);
    showDropdown = false;
    selectedIndex = -1;
  }

  function handleClear() {
    value = '';
    showDropdown = false;
    selectedIndex = -1;
    dispatch('clear');
    inputElement?.focus();
  }

  function handleKeydown(event: KeyboardEvent) {
    if (!showDropdown || suggestions.length === 0) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        selectedIndex = Math.min(selectedIndex + 1, suggestions.length - 1);
        break;
      case 'ArrowUp':
        event.preventDefault();
        selectedIndex = Math.max(selectedIndex - 1, -1);
        break;
      case 'Enter':
        event.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSelect(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        event.preventDefault();
        showDropdown = false;
        selectedIndex = -1;
        break;
    }
  }

  function handleFocus() {
    if (value.trim().length >= 2 && suggestions.length > 0) {
      showDropdown = true;
    }
  }

  function handleBlur(event: FocusEvent) {
    setTimeout(() => {
      showDropdown = false;
      selectedIndex = -1;
    }, 200);
  }

  onMount(() => {
    return () => {
      clearTimeout(debounceTimer);
    };
  });
</script>

<div class="relative w-full">
  <div class="relative group">
    {#if icon}
      <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <svelte:component this={icon} class="text-gray-400 group-focus-within:text-primary-600 transition-colors" size={18} />
      </span>
    {/if}

    <input
      bind:this={inputElement}
      {id}
      type="text"
      bind:value
      {placeholder}
      oninput={handleInput}
      onkeydown={handleKeydown}
      onfocus={handleFocus}
      onblur={handleBlur}
      class="w-full {icon ? 'pl-11' : 'pl-4'} {value ? 'pr-11' : 'pr-4'} py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200 outline-none {inputClass}"
      autocomplete="off"
    />

    <!-- Clear or Loading indicator -->
    {#if loading}
      <span class="absolute inset-y-0 right-0 pr-4 flex items-center">
        <Loader2 size={18} class="text-primary-600 animate-spin" />
      </span>
    {:else if value}
      <button
        type="button"
        onclick={handleClear}
        class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Clear input"
      >
        <X size={18} />
      </button>
    {/if}
  </div>

  <!-- Dropdown -->
  {#if showDropdown && (suggestions.length > 0 || loading)}
    <div class="absolute z-50 w-full mt-2 bg-white rounded-xl elevation-3 overflow-hidden animate-scale-in origin-top">
      {#if loading}
        <div class="px-4 py-4 flex items-center justify-center gap-2 text-gray-500">
          <Loader2 size={18} class="animate-spin text-primary-600" />
          <span class="text-sm">Searching...</span>
        </div>
      {:else if suggestions.length > 0}
        <ul class="py-2 max-h-64 overflow-y-auto">
          {#each suggestions as suggestion, index}
            <li>
              <button
                type="button"
                onclick={() => handleSelect(suggestion)}
                class="w-full px-4 py-2.5 text-left transition-colors flex items-center justify-between group/item {selectedIndex === index ? 'bg-primary-50' : 'hover:bg-gray-50'}"
              >
                <span class="text-sm font-medium text-gray-900 group-hover/item:text-primary-700 {selectedIndex === index ? 'text-primary-700' : ''}">
                  {suggestion.name}
                </span>
                {#if showJobCount && suggestion.jobs_count !== undefined}
                  <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                    {suggestion.jobs_count} jobs
                  </span>
                {/if}
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  {/if}
</div>

<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X } from '@lucide/svelte';

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

    // Debounce the search
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
    // Delay to allow click on dropdown item
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
  <div class="relative">
    {#if icon}
      <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svelte:component this={icon} class="text-gray-400" size={18} />
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
      class="w-full {icon ? 'pl-10' : 'pl-4'} {value ? 'pr-10' : 'pr-4'} py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700 bg-gray-50 focus:bg-white transition-colors duration-200 {inputClass}"
      autocomplete="off"
    />

    {#if value}
      <button
        type="button"
        onclick={handleClear}
        class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Clear input"
      >
        <X size={18} />
      </button>
    {/if}
  </div>

  {#if showDropdown && (suggestions.length > 0 || loading)}
    <div class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
      {#if loading}
        <div class="px-4 py-3 text-sm text-gray-500 text-center">
          Loading...
        </div>
      {:else if suggestions.length > 0}
        <ul class="py-1">
          {#each suggestions as suggestion, index}
            <li>
              <button
                type="button"
                onclick={() => handleSelect(suggestion)}
                class="w-full px-4 py-2 text-left hover:bg-blue-50 transition-colors cursor-pointer {selectedIndex === index ? 'bg-blue-50' : ''}"
              >
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-800 font-medium">{suggestion.name}</span>
                  {#if showJobCount && suggestion.jobs_count !== undefined}
                    <span class="text-xs text-gray-500 ml-2">{suggestion.jobs_count} jobs</span>
                  {/if}
                </div>
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  {/if}
</div>

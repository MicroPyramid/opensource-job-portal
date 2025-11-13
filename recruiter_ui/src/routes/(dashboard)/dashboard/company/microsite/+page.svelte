<script lang="ts">
	import {
		Plus,
		Edit,
		Trash2,
		ExternalLink,
		Eye,
		EyeOff,
		GripVertical,
		Menu,
		Globe,
		Link,
		CheckCircle,
		XCircle
	} from '@lucide/svelte';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import type { PageData, ActionData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	// State management
	let showAddDialog = $state(false);
	let showEditDialog = $state(false);
	let showDeleteDialog = $state(false);
	let selectedMenu = $state<any>(null);
	let submitting = $state(false);

	// Form state
	let menuForm = $state({
		title: '',
		url: '',
		is_active: true
	});

	// Watch for form submission results
	$effect(() => {
		if (form?.success) {
			submitting = false;

			if (form.action === 'create') {
				showAddDialog = false;
				resetForm();
			} else if (form.action === 'update') {
				showEditDialog = false;
				selectedMenu = null;
			} else if (form.action === 'delete') {
				showDeleteDialog = false;
				selectedMenu = null;
			}
		} else if (form?.success === false) {
			submitting = false;
		}
	});

	function resetForm() {
		menuForm.title = '';
		menuForm.url = '';
		menuForm.is_active = true;
	}

	function openEditDialog(menu: any) {
		selectedMenu = menu;
		menuForm.title = menu.title;
		menuForm.url = menu.url;
		menuForm.is_active = menu.is_active;
		showEditDialog = true;
	}

	function openDeleteDialog(menu: any) {
		selectedMenu = menu;
		showDeleteDialog = true;
	}

	function getCompanyPageUrl() {
		if (data.company?.slug) {
			return `/company/${data.company.slug}/`;
		}
		return '#';
	}
</script>

<svelte:head>
	<title>Company Microsite - PeelJobs</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
		<div>
			<h1 class="text-2xl md:text-3xl font-bold text-gray-900">Company Microsite</h1>
			<p class="text-gray-600 mt-1">Manage custom menu items for your company page</p>
		</div>
		<div class="flex gap-3">
			{#if data.company?.slug}
				<a
					href={getCompanyPageUrl()}
					target="_blank"
					class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
				>
					<Globe class="w-4 h-4" />
					View Company Page
				</a>
			{/if}
			<button
				onclick={() => (showAddDialog = true)}
				class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
			>
				<Plus class="w-4 h-4" />
				Add Menu Item
			</button>
		</div>
	</div>

	<!-- Success/Error Messages -->
	{#if form?.success}
		<div class="bg-green-50 border border-green-200 text-green-800 rounded-lg p-4">
			<div class="flex items-center gap-2">
				<CheckCircle class="w-5 h-5" />
				<span>{form.message}</span>
			</div>
		</div>
	{/if}

	{#if form?.error}
		<div class="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
			<div class="flex items-center gap-2">
				<XCircle class="w-5 h-5" />
				<span>{form.error}</span>
			</div>
		</div>
	{/if}

	<!-- Menu Items List -->
	{#if data.menus.length === 0}
		<div class="bg-white rounded-lg border border-gray-200 p-12 text-center">
			<Menu class="w-12 h-12 text-gray-400 mx-auto mb-4" />
			<h3 class="text-lg font-semibold text-gray-900 mb-2">No menu items yet</h3>
			<p class="text-gray-600 mb-6">Create custom menu items for your company page</p>
			<button
				onclick={() => (showAddDialog = true)}
				class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				<Plus class="w-4 h-4" />
				Add First Menu Item
			</button>
		</div>
	{:else}
		<div class="bg-white rounded-lg border border-gray-200">
			<div class="p-6 border-b border-gray-200">
				<h2 class="text-lg font-semibold text-gray-900">Menu Items ({data.menus.length})</h2>
			</div>

			<div class="divide-y divide-gray-200">
				{#each data.menus as menu, index}
					<div class="p-4 hover:bg-gray-50 transition-colors">
						<div class="flex items-center justify-between gap-4">
							<!-- Drag Handle -->
							<div class="text-gray-400 cursor-move">
								<GripVertical class="w-5 h-5" />
							</div>

							<!-- Menu Info -->
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-3">
									<h3 class="text-base font-semibold text-gray-900">{menu.title}</h3>
									{#if menu.is_active}
										<span class="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
											<Eye class="w-3 h-3" />
											Active
										</span>
									{:else}
										<span class="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded">
											<EyeOff class="w-3 h-3" />
											Inactive
										</span>
									{/if}
								</div>
								<a
									href={menu.url}
									target="_blank"
									class="text-sm text-blue-600 hover:text-blue-700 hover:underline flex items-center gap-1 mt-1"
								>
									<Link class="w-3 h-3" />
									{menu.url}
								</a>
								<div class="text-xs text-gray-500 mt-1">Order: {menu.order || index + 1}</div>
							</div>

							<!-- Actions -->
							<div class="flex items-center gap-2">
								<!-- Toggle Status -->
								<form
									method="POST"
									action="?/toggleMenuStatus"
									use:enhance={() => {
										return async ({ result }) => {
											if (result.type === 'success') {
												await invalidateAll();
											}
										};
									}}
								>
									<input type="hidden" name="menu_id" value={menu.id} />
									<button
										type="submit"
										class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
										title={menu.is_active ? 'Deactivate' : 'Activate'}
									>
										{#if menu.is_active}
											<EyeOff class="w-4 h-4" />
										{:else}
											<Eye class="w-4 h-4" />
										{/if}
									</button>
								</form>

								<!-- Edit -->
								<button
									onclick={() => openEditDialog(menu)}
									class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
									title="Edit"
								>
									<Edit class="w-4 h-4" />
								</button>

								<!-- Delete -->
								<button
									onclick={() => openDeleteDialog(menu)}
									class="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
									title="Delete"
								>
									<Trash2 class="w-4 h-4" />
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<!-- Add Menu Dialog -->
{#if showAddDialog}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
		<div class="bg-white rounded-lg max-w-md w-full p-6">
			<h2 class="text-xl font-bold text-gray-900 mb-4">Add Menu Item</h2>

			<form
				method="POST"
				action="?/createMenu"
				use:enhance={() => {
					submitting = true;
					return async ({ update }) => {
						await update();
					};
				}}
			>
				<div class="space-y-4">
					<div>
						<label for="title" class="block text-sm font-medium text-gray-700 mb-1">
							Menu Title <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="title"
							name="title"
							bind:value={menuForm.title}
							required
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							placeholder="e.g., About Us"
						/>
					</div>

					<div>
						<label for="url" class="block text-sm font-medium text-gray-700 mb-1">
							URL <span class="text-red-500">*</span>
						</label>
						<input
							type="url"
							id="url"
							name="url"
							bind:value={menuForm.url}
							required
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							placeholder="https://example.com/about"
						/>
					</div>

					<div class="flex items-center gap-2">
						<input
							type="checkbox"
							id="is_active"
							name="is_active"
							bind:checked={menuForm.is_active}
							value="true"
							class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
						/>
						<label for="is_active" class="text-sm text-gray-700">Active (visible on company page)</label>
					</div>
				</div>

				<div class="flex gap-3 mt-6">
					<button
						type="button"
						onclick={() => {
							showAddDialog = false;
							resetForm();
						}}
						class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
						disabled={submitting}
					>
						Cancel
					</button>
					<button
						type="submit"
						class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
						disabled={submitting}
					>
						{submitting ? 'Creating...' : 'Create Menu'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Edit Menu Dialog -->
{#if showEditDialog && selectedMenu}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
		<div class="bg-white rounded-lg max-w-md w-full p-6">
			<h2 class="text-xl font-bold text-gray-900 mb-4">Edit Menu Item</h2>

			<form
				method="POST"
				action="?/updateMenu"
				use:enhance={() => {
					submitting = true;
					return async ({ update }) => {
						await update();
					};
				}}
			>
				<input type="hidden" name="menu_id" value={selectedMenu.id} />

				<div class="space-y-4">
					<div>
						<label for="edit_title" class="block text-sm font-medium text-gray-700 mb-1">
							Menu Title <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="edit_title"
							name="title"
							bind:value={menuForm.title}
							required
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div>
						<label for="edit_url" class="block text-sm font-medium text-gray-700 mb-1">
							URL <span class="text-red-500">*</span>
						</label>
						<input
							type="url"
							id="edit_url"
							name="url"
							bind:value={menuForm.url}
							required
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<div class="flex items-center gap-2">
						<input
							type="checkbox"
							id="edit_is_active"
							name="is_active"
							bind:checked={menuForm.is_active}
							value="true"
							class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
						/>
						<label for="edit_is_active" class="text-sm text-gray-700">Active (visible on company page)</label>
					</div>
				</div>

				<div class="flex gap-3 mt-6">
					<button
						type="button"
						onclick={() => {
							showEditDialog = false;
							selectedMenu = null;
							resetForm();
						}}
						class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
						disabled={submitting}
					>
						Cancel
					</button>
					<button
						type="submit"
						class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
						disabled={submitting}
					>
						{submitting ? 'Updating...' : 'Update Menu'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Delete Confirmation Dialog -->
{#if showDeleteDialog && selectedMenu}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
		<div class="bg-white rounded-lg max-w-md w-full p-6">
			<h2 class="text-xl font-bold text-gray-900 mb-4">Delete Menu Item</h2>
			<p class="text-gray-600 mb-6">
				Are you sure you want to delete "<strong>{selectedMenu.title}</strong>"? This action cannot be undone.
			</p>

			<form
				method="POST"
				action="?/deleteMenu"
				use:enhance={() => {
					submitting = true;
					return async ({ update }) => {
						await update();
					};
				}}
			>
				<input type="hidden" name="menu_id" value={selectedMenu.id} />

				<div class="flex gap-3">
					<button
						type="button"
						onclick={() => {
							showDeleteDialog = false;
							selectedMenu = null;
						}}
						class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
						disabled={submitting}
					>
						Cancel
					</button>
					<button
						type="submit"
						class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
						disabled={submitting}
					>
						{submitting ? 'Deleting...' : 'Delete'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

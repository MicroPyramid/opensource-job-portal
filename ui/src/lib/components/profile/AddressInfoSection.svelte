<script lang="ts">
	import { MapPin } from '@lucide/svelte';

	// Accept the full formData object, only use the fields we need
	export let formData: {
		address: string;
		permanent_address: string;
		pincode: string;
		[key: string]: any; // Allow other fields
	};
	export let validationErrors: Record<string, string> = {};

	let sameAsPermanent = false;

	function handleSameAsCurrentAddress() {
		if (sameAsPermanent) {
			formData.permanent_address = formData.address;
		}
	}
</script>

<div class="bg-white rounded-lg shadow-sm p-6">
	<h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
		<MapPin class="w-5 h-5" />
		Address Information
	</h2>

	<div class="grid md:grid-cols-2 gap-6">
		<!-- Current Address -->
		<div class="md:col-span-2">
			<label for="address" class="block text-sm font-medium text-gray-700 mb-2">
				Current Address
			</label>
			<textarea
				id="address"
				bind:value={formData.address}
				rows="3"
				placeholder="Enter your current residential address..."
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			></textarea>
		</div>

		<!-- Permanent Address -->
		<div class="md:col-span-2">
			<div class="flex items-center justify-between mb-2">
				<label for="permanent_address" class="block text-sm font-medium text-gray-700">
					Permanent Address
				</label>
				<label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
					<input
						type="checkbox"
						bind:checked={sameAsPermanent}
						onchange={handleSameAsCurrentAddress}
						class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
					/>
					Same as current address
				</label>
			</div>
			<textarea
				id="permanent_address"
				bind:value={formData.permanent_address}
				rows="3"
				placeholder="Enter your permanent address..."
				disabled={sameAsPermanent}
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
			></textarea>
		</div>

		<!-- PIN Code -->
		<div>
			<label for="pincode" class="block text-sm font-medium text-gray-700 mb-2">
				PIN Code
			</label>
			<input
				id="pincode"
				type="text"
				bind:value={formData.pincode}
				maxlength="6"
				placeholder="e.g., 560001"
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				class:border-red-500={validationErrors.pincode}
			/>
			{#if validationErrors.pincode}
				<p class="mt-1 text-sm text-red-600">{validationErrors.pincode}</p>
			{/if}
		</div>
	</div>
</div>

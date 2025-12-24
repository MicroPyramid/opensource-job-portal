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

<div class="p-5 lg:p-6">
	<div class="flex items-center gap-3 mb-6">
		<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
			<MapPin size={20} class="text-primary-600" />
		</div>
		<div>
			<h2 class="text-lg font-semibold text-gray-900">Address Information</h2>
			<p class="text-sm text-gray-600">Your residential details</p>
		</div>
	</div>

	<div class="grid md:grid-cols-2 gap-5">
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
				class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none resize-none"
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
						class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
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
				class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
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
				class="w-full px-4 py-3 border rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white transition-all outline-none {validationErrors.pincode ? 'border-error-500 focus:border-error-500 focus:ring-2 focus:ring-error-500/20' : 'border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20'}"
			/>
			{#if validationErrors.pincode}
				<p class="mt-2 text-sm text-error-600">{validationErrors.pincode}</p>
			{/if}
		</div>
	</div>
</div>

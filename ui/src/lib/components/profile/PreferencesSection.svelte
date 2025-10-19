<script lang="ts">
	// Accept the full formData object, only use the fields we need
	export let formData: {
		relocation: boolean;
		is_looking_for_job: boolean;
		is_open_to_offers: boolean;
		email_notifications: boolean;
		show_email: boolean;
		[key: string]: any; // Allow other fields
	};
</script>

<div class="bg-white rounded-lg shadow-sm p-6">
	<h2 class="text-lg font-semibold text-gray-900 mb-4">Job Preferences</h2>

	<div class="space-y-4">
		<!-- Open to Relocation -->
		<label class="flex items-center gap-3 cursor-pointer">
			<input
				type="checkbox"
				bind:checked={formData.relocation}
				class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
			/>
			<div>
				<p class="font-medium text-gray-900">Open to Relocation</p>
				<p class="text-sm text-gray-600">Willing to relocate for the right opportunity</p>
			</div>
		</label>

		<!-- Actively Looking for Jobs -->
		<label class="flex items-center gap-3 cursor-pointer">
			<input
				type="checkbox"
				bind:checked={formData.is_looking_for_job}
				class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
			/>
			<div>
				<p class="font-medium text-gray-900">Actively Looking for Jobs</p>
				<p class="text-sm text-gray-600">Currently searching for new opportunities</p>
			</div>
		</label>

		<!-- Open to Offers -->
		<label class="flex items-center gap-3 cursor-pointer">
			<input
				type="checkbox"
				bind:checked={formData.is_open_to_offers}
				class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
			/>
			<div>
				<p class="font-medium text-gray-900">Open to Offers</p>
				<p class="text-sm text-gray-600">Open to hearing about new opportunities</p>
			</div>
		</label>

		<!-- Email Notifications -->
		<label class="flex items-center gap-3 cursor-pointer">
			<input
				type="checkbox"
				bind:checked={formData.email_notifications}
				class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
			/>
			<div>
				<p class="font-medium text-gray-900">Email Notifications</p>
				<p class="text-sm text-gray-600">Receive job alerts and updates via email</p>
			</div>
		</label>

		<!-- Show Email to Recruiters -->
		<label class="flex items-center gap-3 cursor-pointer">
			<input
				type="checkbox"
				bind:checked={formData.show_email}
				class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
			/>
			<div>
				<p class="font-medium text-gray-900">Show Email to Recruiters</p>
				<p class="text-sm text-gray-600">Allow recruiters to see your email address</p>
			</div>
		</label>
	</div>
</div>

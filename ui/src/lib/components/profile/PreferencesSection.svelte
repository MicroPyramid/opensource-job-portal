<script lang="ts">
	import { Settings } from '@lucide/svelte';

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

<div class="p-5 lg:p-6">
	<div class="flex items-center gap-3 mb-6">
		<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
			<Settings size={20} class="text-primary-600" />
		</div>
		<div>
			<h2 class="text-lg font-semibold text-gray-900">Job Preferences</h2>
			<p class="text-sm text-gray-600">Your job search preferences and settings</p>
		</div>
	</div>

	<div class="space-y-4">
		<!-- Open to Relocation -->
		<div class="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:bg-gray-100 transition-colors">
			<label class="flex items-start gap-3 cursor-pointer">
				<input
					type="checkbox"
					bind:checked={formData.relocation}
					class="w-5 h-5 mt-0.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
				/>
				<div>
					<p class="font-medium text-gray-900">Open to Relocation</p>
					<p class="text-sm text-gray-600">Willing to relocate for the right opportunity</p>
				</div>
			</label>
		</div>

		<!-- Actively Looking for Jobs -->
		<div class="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:bg-gray-100 transition-colors">
			<label class="flex items-start gap-3 cursor-pointer">
				<input
					type="checkbox"
					bind:checked={formData.is_looking_for_job}
					class="w-5 h-5 mt-0.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
				/>
				<div>
					<p class="font-medium text-gray-900">Actively Looking for Jobs</p>
					<p class="text-sm text-gray-600">Currently searching for new opportunities</p>
				</div>
			</label>
		</div>

		<!-- Open to Offers -->
		<div class="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:bg-gray-100 transition-colors">
			<label class="flex items-start gap-3 cursor-pointer">
				<input
					type="checkbox"
					bind:checked={formData.is_open_to_offers}
					class="w-5 h-5 mt-0.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
				/>
				<div>
					<p class="font-medium text-gray-900">Open to Offers</p>
					<p class="text-sm text-gray-600">Open to hearing about new opportunities</p>
				</div>
			</label>
		</div>

		<!-- Email Notifications -->
		<div class="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:bg-gray-100 transition-colors">
			<label class="flex items-start gap-3 cursor-pointer">
				<input
					type="checkbox"
					bind:checked={formData.email_notifications}
					class="w-5 h-5 mt-0.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
				/>
				<div>
					<p class="font-medium text-gray-900">Email Notifications</p>
					<p class="text-sm text-gray-600">Receive job alerts and updates via email</p>
				</div>
			</label>
		</div>

		<!-- Show Email to Recruiters -->
		<div class="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:bg-gray-100 transition-colors">
			<label class="flex items-start gap-3 cursor-pointer">
				<input
					type="checkbox"
					bind:checked={formData.show_email}
					class="w-5 h-5 mt-0.5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
				/>
				<div>
					<p class="font-medium text-gray-900">Show Email to Recruiters</p>
					<p class="text-sm text-gray-600">Allow recruiters to see your email address</p>
				</div>
			</label>
		</div>
	</div>
</div>

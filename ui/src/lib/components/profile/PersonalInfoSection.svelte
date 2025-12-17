<script lang="ts">
	import { User, Mail, Phone, Calendar } from '@lucide/svelte';

	// Accept the full formData object, only use the fields we need
	export let formData: {
		first_name: string;
		last_name: string;
		mobile: string;
		alternate_mobile: string;
		gender: string;
		dob: string;
		marital_status: string;
		nationality: string;
		[key: string]: any; // Allow other fields
	};
	export let email: string;
	export let validationErrors: Record<string, string> = {};
</script>

<div class="bg-white rounded-lg shadow-sm p-6">
	<h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
		<User class="w-5 h-5" />
		Personal Information
	</h2>

	<div class="grid md:grid-cols-2 gap-6">
		<!-- First Name -->
		<div>
			<label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
				First Name <span class="text-red-500">*</span>
			</label>
			<input
				id="first_name"
				type="text"
				bind:value={formData.first_name}
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				class:border-red-500={validationErrors.first_name}
				required
			/>
			{#if validationErrors.first_name}
				<p class="mt-1 text-sm text-red-600">{validationErrors.first_name}</p>
			{/if}
		</div>

		<!-- Last Name -->
		<div>
			<label for="last_name" class="block text-sm font-medium text-gray-700 mb-2">
				Last Name <span class="text-red-500">*</span>
			</label>
			<input
				id="last_name"
				type="text"
				bind:value={formData.last_name}
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				class:border-red-500={validationErrors.last_name}
				required
			/>
			{#if validationErrors.last_name}
				<p class="mt-1 text-sm text-red-600">{validationErrors.last_name}</p>
			{/if}
		</div>

		<!-- Email (Read-only) -->
		<div>
			<label for="email" class="block text-sm font-medium text-gray-700 mb-2">
				Email Address
			</label>
			<div
				class="flex items-center gap-2 px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg"
			>
				<Mail class="w-5 h-5 text-gray-400" />
				<span class="text-gray-600">{email}</span>
			</div>
			<p class="mt-1 text-xs text-gray-500">Email cannot be changed</p>
		</div>

		<!-- Mobile Number -->
		<div>
			<label for="mobile" class="block text-sm font-medium text-gray-700 mb-2">
				Mobile Number
			</label>
			<div
				class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-blue-500"
			>
				<Phone class="w-5 h-5 text-gray-400" />
				<input
					id="mobile"
					type="tel"
					bind:value={formData.mobile}
					placeholder="+91 9876543210"
					class="flex-1 outline-none"
					class:border-red-500={validationErrors.mobile}
				/>
			</div>
			{#if validationErrors.mobile}
				<p class="mt-1 text-sm text-red-600">{validationErrors.mobile}</p>
			{/if}
		</div>

		<!-- Alternate Mobile Number -->
		<div>
			<label for="alternate_mobile" class="block text-sm font-medium text-gray-700 mb-2">
				Alternate Mobile Number
			</label>
			<div
				class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-blue-500"
			>
				<Phone class="w-5 h-5 text-gray-400" />
				<input
					id="alternate_mobile"
					type="tel"
					bind:value={formData.alternate_mobile}
					placeholder="+91 9876543210"
					class="flex-1 outline-none"
					class:border-red-500={validationErrors.alternate_mobile}
				/>
			</div>
			{#if validationErrors.alternate_mobile}
				<p class="mt-1 text-sm text-red-600">{validationErrors.alternate_mobile}</p>
			{/if}
		</div>

		<!-- Gender -->
		<div>
			<label for="gender" class="block text-sm font-medium text-gray-700 mb-2"> Gender </label>
			<select
				id="gender"
				bind:value={formData.gender}
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			>
				<option value="">Select gender</option>
				<option value="M">Male</option>
				<option value="F">Female</option>
			</select>
		</div>

		<!-- Date of Birth -->
		<div>
			<label for="dob" class="block text-sm font-medium text-gray-700 mb-2">
				Date of Birth
			</label>
			<div
				class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-blue-500"
			>
				<Calendar class="w-5 h-5 text-gray-400" />
				<input id="dob" type="date" bind:value={formData.dob} class="flex-1 outline-none" />
			</div>
		</div>

		<!-- Marital Status -->
		<div>
			<label for="marital_status" class="block text-sm font-medium text-gray-700 mb-2">
				Marital Status
			</label>
			<select
				id="marital_status"
				bind:value={formData.marital_status}
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			>
				<option value="">Select status</option>
				<option value="Single">Single</option>
				<option value="Married">Married</option>
			</select>
		</div>

		<!-- Nationality -->
		<div>
			<label for="nationality" class="block text-sm font-medium text-gray-700 mb-2">
				Nationality
			</label>
			<input
				id="nationality"
				type="text"
				bind:value={formData.nationality}
				placeholder="e.g., Indian"
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			/>
		</div>
	</div>
</div>

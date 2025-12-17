<script lang="ts">
	import { Briefcase, DollarSign } from '@lucide/svelte';

	// Accept the full formData object, only use the fields we need
	export let formData: {
		job_role: string;
		profile_description: string;
		year: string;
		month: string;
		notice_period: string;
		current_salary: string;
		expected_salary: string;
		[key: string]: any; // Allow other fields
	};

	function formatExperience(year?: string, month?: string): string {
		if (!year && !month) return 'Not specified';
		const years = year ? `${year} year${parseInt(year) !== 1 ? 's' : ''}` : '';
		const months = month ? `${month} month${parseInt(month) !== 1 ? 's' : ''}` : '';
		return [years, months].filter(Boolean).join(' ');
	}
</script>

<div class="bg-white rounded-lg shadow-sm p-6">
	<h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
		<Briefcase class="w-5 h-5" />
		Professional Information
	</h2>

	<div class="grid md:grid-cols-2 gap-6">
		<!-- Job Role -->
		<div class="md:col-span-2">
			<label for="job_role" class="block text-sm font-medium text-gray-700 mb-2">
				Current/Desired Job Role
			</label>
			<input
				id="job_role"
				type="text"
				bind:value={formData.job_role}
				placeholder="e.g., Full Stack Developer"
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			/>
		</div>

		<!-- Professional Summary -->
		<div class="md:col-span-2">
			<label for="profile_description" class="block text-sm font-medium text-gray-700 mb-2">
				Professional Summary
			</label>
			<textarea
				id="profile_description"
				bind:value={formData.profile_description}
				rows="4"
				placeholder="Brief description of your professional background and goals..."
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			></textarea>
		</div>

		<!-- Total Experience -->
		<fieldset class="border-0 p-0 m-0">
			<legend class="block text-sm font-medium text-gray-700 mb-2">Total Experience</legend>
			<div class="grid grid-cols-2 gap-3">
				<div>
					<input
						type="number"
						bind:value={formData.year}
						min="0"
						max="50"
						placeholder="Years"
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					/>
				</div>
				<div>
					<input
						type="number"
						bind:value={formData.month}
						min="0"
						max="11"
						placeholder="Months"
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					/>
				</div>
			</div>
			<p class="mt-1 text-xs text-gray-500">
				{formatExperience(formData.year, formData.month)}
			</p>
		</fieldset>

		<!-- Notice Period -->
		<div>
			<label for="notice_period" class="block text-sm font-medium text-gray-700 mb-2">
				Notice Period
			</label>
			<input
				id="notice_period"
				type="text"
				bind:value={formData.notice_period}
				placeholder="e.g., 30 days, Immediate"
				class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			/>
		</div>

		<!-- Current Salary -->
		<div>
			<label for="current_salary" class="block text-sm font-medium text-gray-700 mb-2">
				Current Salary (Annual)
			</label>
			<div
				class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-blue-500"
			>
				<DollarSign class="w-5 h-5 text-gray-400" />
				<input
					id="current_salary"
					type="text"
					bind:value={formData.current_salary}
					placeholder="e.g., 500000"
					class="flex-1 outline-none"
				/>
			</div>
		</div>

		<!-- Expected Salary -->
		<div>
			<label for="expected_salary" class="block text-sm font-medium text-gray-700 mb-2">
				Expected Salary (Annual)
			</label>
			<div
				class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-blue-500"
			>
				<DollarSign class="w-5 h-5 text-gray-400" />
				<input
					id="expected_salary"
					type="text"
					bind:value={formData.expected_salary}
					placeholder="e.g., 800000"
					class="flex-1 outline-none"
				/>
			</div>
		</div>
	</div>
</div>

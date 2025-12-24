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

<div class="p-5 lg:p-6">
	<div class="flex items-center gap-3 mb-6">
		<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
			<Briefcase size={20} class="text-primary-600" />
		</div>
		<div>
			<h2 class="text-lg font-semibold text-gray-900">Professional Information</h2>
			<p class="text-sm text-gray-600">Your career details and preferences</p>
		</div>
	</div>

	<div class="grid md:grid-cols-2 gap-5">
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
				class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
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
				class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none resize-none"
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
						class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
					/>
				</div>
				<div>
					<input
						type="number"
						bind:value={formData.month}
						min="0"
						max="11"
						placeholder="Months"
						class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
					/>
				</div>
			</div>
			<p class="mt-2 text-xs text-gray-500">
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
				class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
			/>
		</div>

		<!-- Current Salary -->
		<div>
			<label for="current_salary" class="block text-sm font-medium text-gray-700 mb-2">
				Current Salary (Annual)
			</label>
			<div class="relative">
				<span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
					<DollarSign size={18} class="text-gray-400" />
				</span>
				<input
					id="current_salary"
					type="text"
					bind:value={formData.current_salary}
					placeholder="e.g., 500000"
					class="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
				/>
			</div>
		</div>

		<!-- Expected Salary -->
		<div>
			<label for="expected_salary" class="block text-sm font-medium text-gray-700 mb-2">
				Expected Salary (Annual)
			</label>
			<div class="relative">
				<span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
					<DollarSign size={18} class="text-gray-400" />
				</span>
				<input
					id="expected_salary"
					type="text"
					bind:value={formData.expected_salary}
					placeholder="e.g., 800000"
					class="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
				/>
			</div>
		</div>
	</div>
</div>

<script lang="ts">
	import { ShieldCheck, Loader, Mail, KeyRound } from '@lucide/svelte';
	import { toast } from '$lib/stores/toast';

	export let email: string = '';
	export let pendingEmail: string = '';

	let changingPassword = false;
	let changingEmail = false;

	let oldPassword = '';
	let newPassword = '';
	let confirmPassword = '';

	let newEmail = '';
	let emailPassword = '';
	// Set optimistically after a successful request so the "check your inbox"
	// notice survives without a profile refetch.
	let requestedEmail = '';

	$: awaitingConfirmation = requestedEmail || pendingEmail;

	/**
	 * Flatten DRF's error shapes into one line.
	 *
	 * The two endpoints do not agree: change-password wraps field errors in
	 * `error`, change-email returns them at the top level, and both can also
	 * return `non_field_errors`.
	 */
	function errorMessage(body: unknown, fallback: string): string {
		if (!body || typeof body !== 'object') return fallback;

		const payload = ('error' in body ? (body as Record<string, unknown>).error : body) as
			| Record<string, unknown>
			| undefined;
		if (!payload || typeof payload !== 'object') return fallback;

		if (typeof payload === 'string') return payload;

		for (const value of Object.values(payload)) {
			if (typeof value === 'string') return value;
			if (Array.isArray(value) && typeof value[0] === 'string') return value[0];
		}
		return fallback;
	}

	async function handlePasswordChange() {
		if (newPassword !== confirmPassword) {
			toast.error('New passwords do not match');
			return;
		}

		try {
			changingPassword = true;
			const response = await fetch('/api/auth/change-password/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					old_password: oldPassword,
					new_password: newPassword,
					confirm_password: confirmPassword
				})
			});
			const body = await response.json().catch(() => null);

			if (!response.ok) {
				toast.error(errorMessage(body, 'Could not change your password'));
				return;
			}

			toast.success(body?.message ?? 'Password changed successfully');
			oldPassword = newPassword = confirmPassword = '';
		} catch {
			toast.error('Could not change your password');
		} finally {
			changingPassword = false;
		}
	}

	async function handleEmailChange() {
		try {
			changingEmail = true;
			const response = await fetch('/api/auth/change-email/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ new_email: newEmail, password: emailPassword })
			});
			const body = await response.json().catch(() => null);

			if (!response.ok) {
				toast.error(errorMessage(body, 'Could not change your email address'));
				return;
			}

			toast.success(body?.message ?? 'Check your new inbox for a confirmation link');
			requestedEmail = body?.pending_email ?? newEmail;
			newEmail = emailPassword = '';
		} catch {
			toast.error('Could not change your email address');
		} finally {
			changingEmail = false;
		}
	}
</script>

<div class="p-5 lg:p-6">
	<div class="flex items-center gap-3 mb-6">
		<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
			<ShieldCheck size={20} class="text-primary-600" />
		</div>
		<div>
			<h2 class="text-lg font-semibold text-gray-900">Account & Security</h2>
			<p class="text-sm text-gray-600">Your sign-in email and password</p>
		</div>
	</div>

	<div class="grid gap-8 md:grid-cols-2">
		<!-- Email address -->
		<form
			class="space-y-4"
			on:submit|preventDefault={handleEmailChange}
			aria-labelledby="account-email-heading"
		>
			<div class="flex items-center gap-2">
				<Mail size={16} class="text-gray-500" />
				<h3 id="account-email-heading" class="text-sm font-semibold text-gray-900">
					Email address
				</h3>
			</div>

			<p class="text-sm text-gray-600">
				You sign in with <span class="font-medium text-gray-900">{email}</span>.
			</p>

			{#if awaitingConfirmation}
				<p class="text-sm rounded-lg bg-amber-50 text-amber-900 px-3 py-2">
					Waiting for you to confirm <span class="font-medium">{awaitingConfirmation}</span>. Your
					current address stays active until you do.
				</p>
			{/if}

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1" for="new-email">
					New email address
				</label>
				<input
					id="new-email"
					type="email"
					required
					bind:value={newEmail}
					autocomplete="email"
					class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1" for="email-password">
					Confirm with your password
				</label>
				<input
					id="email-password"
					type="password"
					required
					bind:value={emailPassword}
					autocomplete="current-password"
					class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
				/>
			</div>

			<button
				type="submit"
				disabled={changingEmail}
				class="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-60"
			>
				{#if changingEmail}
					<Loader size={16} class="animate-spin" />
				{/if}
				Send confirmation link
			</button>
		</form>

		<!-- Password -->
		<form
			class="space-y-4"
			on:submit|preventDefault={handlePasswordChange}
			aria-labelledby="account-password-heading"
		>
			<div class="flex items-center gap-2">
				<KeyRound size={16} class="text-gray-500" />
				<h3 id="account-password-heading" class="text-sm font-semibold text-gray-900">Password</h3>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1" for="old-password">
					Current password
				</label>
				<input
					id="old-password"
					type="password"
					required
					bind:value={oldPassword}
					autocomplete="current-password"
					class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1" for="new-password">
					New password
				</label>
				<input
					id="new-password"
					type="password"
					required
					minlength="8"
					bind:value={newPassword}
					autocomplete="new-password"
					class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1" for="confirm-password">
					Confirm new password
				</label>
				<input
					id="confirm-password"
					type="password"
					required
					minlength="8"
					bind:value={confirmPassword}
					autocomplete="new-password"
					class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
				/>
			</div>

			<button
				type="submit"
				disabled={changingPassword}
				class="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-60"
			>
				{#if changingPassword}
					<Loader size={16} class="animate-spin" />
				{/if}
				Change password
			</button>
		</form>
	</div>
</div>

"use client";

import { useActionState, useState } from "react";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Button, Input, FormField } from "@/components/ui";
import { loginAction, type LoginState } from "@/app/(auth)/login/actions";

const initialState: LoginState = {};

/**
 * Ports the <form use:enhance> block from (auth)/login/+page.svelte.
 *
 * `useActionState` replaces both `use:enhance` and the manual `loading` flag —
 * the pending state comes from the hook rather than being toggled by hand in the
 * submit callback. `form?.error` becomes `state.error`.
 */
export function LoginForm({ redirectTo }: { redirectTo: string }) {
  const [state, formAction, isPending] = useActionState(
    loginAction,
    initialState,
  );
  const [showPassword, setShowPassword] = useState(false);

  return (
    <form action={formAction} className="space-y-5">
      {/* Hidden field for redirect URL */}
      <input type="hidden" name="redirect_to" value={redirectTo} />

      {state.error && (
        <div className="bg-error-light border border-error/20 text-error px-4 py-3 rounded-lg text-sm whitespace-pre-line">
          {state.error}
        </div>
      )}

      <FormField label="Email Address">
        <Input
          type="email"
          id="email"
          name="email"
          defaultValue={state.email ?? ""}
          required
          disabled={isPending}
          placeholder="you@company.com"
          size="lg"
          iconLeft={<Mail className="w-5 h-5" />}
        />
      </FormField>

      <FormField label="Password">
        <div className="relative">
          <Input
            type={showPassword ? "text" : "password"}
            id="password"
            name="password"
            required
            disabled={isPending}
            placeholder="Enter your password"
            size="lg"
            className="pr-12"
            iconLeft={<Lock className="w-5 h-5" />}
          />
          <button
            type="button"
            onClick={() => setShowPassword((shown) => !shown)}
            disabled={isPending}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-black transition-colors disabled:opacity-50"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? (
              <EyeOff className="w-5 h-5" />
            ) : (
              <Eye className="w-5 h-5" />
            )}
          </button>
        </div>
      </FormField>

      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 cursor-pointer group">
          <input
            type="checkbox"
            name="remember_me"
            className="w-4 h-4 text-primary border-border rounded focus:ring-primary/20 focus:ring-2"
          />
          <span className="text-sm text-muted group-hover:text-black transition-colors">
            Remember me
          </span>
        </label>

        <a
          href="/forgot-password/"
          className="text-sm font-medium text-primary hover:text-primary-hover transition-colors"
        >
          Forgot password?
        </a>
      </div>

      <Button type="submit" size="lg" loading={isPending} className="w-full">
        {isPending ? "Signing in..." : "Sign In"}
      </Button>
    </form>
  );
}

export default LoginForm;

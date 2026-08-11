"use client";

import type { InputHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils/cn";
import { useFormField } from "@/components/ui/FormField";

type Size = "sm" | "md" | "lg";

const sizeClasses: Record<Size, string> = {
  sm: "h-8 px-3 text-sm rounded-lg",
  md: "h-10 px-3 text-sm rounded-lg",
  lg: "h-12 px-4 text-base rounded-lg",
};

// `size` is omitted because the native input `size` attribute is a number,
// while this component uses it for the visual scale.
export interface InputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "size"> {
  size?: Size;
  error?: boolean;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
}

/**
 * Ports the Svelte Input. `bind:value` becomes an ordinary controlled/uncontrolled
 * input — pass `value` + `onChange`, or `defaultValue`, or neither and read it
 * from the form on submit.
 *
 * When rendered inside a FormField it picks up that field's generated id and
 * error state, so the label association and `aria-describedby` come for free.
 */
export function Input({
  size = "md",
  error = false,
  iconLeft,
  iconRight,
  className,
  id,
  ...rest
}: InputProps) {
  const field = useFormField();

  const inputId = id ?? field.controlId;
  const hasError = error || Boolean(field.hasError);

  return (
    <div className="relative">
      {iconLeft && (
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-muted">
          {iconLeft}
        </div>
      )}

      <input
        id={inputId}
        aria-invalid={hasError || undefined}
        aria-describedby={field.descriptionId}
        className={cn(
          "w-full border bg-white transition-colors placeholder:text-muted/60 focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed",
          sizeClasses[size],
          hasError
            ? "border-error focus:border-error focus:ring-error/20"
            : "border-border",
          iconLeft && "pl-10",
          iconRight && "pr-10",
          className,
        )}
        {...rest}
      />

      {iconRight && (
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 text-muted">
          {iconRight}
        </div>
      )}
    </div>
  );
}

export default Input;

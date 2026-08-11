import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind classes, with later classes winning conflicts.
 *
 * The Svelte primitives built their class lists by template concatenation
 * (`${base} ${variant} ${className}`), which meant a caller passing
 * `class="p-8"` to a component whose base already set `p-4` got both — and CSS
 * source order, not the caller, decided the winner. `twMerge` resolves those
 * collisions properly so `className` reliably overrides.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

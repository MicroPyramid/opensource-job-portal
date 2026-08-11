import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

export interface AuthMainProps {
  /** Width constraint on the inner container. Defaults to the narrow form width. */
  containerClass?: string;
  /** Layout of the <main> element itself. Wider pages centre-align to the top. */
  mainClass?: string;
  children: ReactNode;
}

/**
 * The <main> region of the auth shell.
 *
 * In SvelteKit the layout owned this element and each page reached *up* into it
 * via `setContext('authLayout', …)` to widen the container — signup and login to
 * `max-w-6xl`, onboarding to `max-w-3xl`, the rest to `max-w-lg`.
 *
 * That inversion can't work under RSC: a layout renders before its children, so
 * a page cannot mutate it. Each page now renders this component directly and
 * passes the width it wants, which is both the idiomatic direction and one less
 * indirection to follow when reading a page.
 */
export function AuthMain({
  containerClass = "max-w-md",
  mainClass = "flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8",
  children,
}: AuthMainProps) {
  return (
    <main className={mainClass}>
      <div className={cn("w-full", containerClass)}>{children}</div>
    </main>
  );
}

/** The wide variant shared by login and signup. */
export const AUTH_MAIN_WIDE = "flex justify-center items-start py-8 px-4 sm:px-6 lg:px-8";

export default AuthMain;

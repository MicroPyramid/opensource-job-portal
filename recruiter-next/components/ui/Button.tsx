import Link from "next/link";
import type {
  AnchorHTMLAttributes,
  ButtonHTMLAttributes,
  ReactNode,
} from "react";
import { cn } from "@/lib/utils/cn";

type Variant = "primary" | "secondary" | "ghost";
type Size = "sm" | "md" | "lg";

const baseClasses =
  "inline-flex items-center justify-center font-semibold transition-colors focus-visible:ring-2 focus-visible:ring-primary/20 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

const variantClasses: Record<Variant, string> = {
  primary: "bg-primary text-white hover:bg-primary-hover",
  secondary: "border border-primary text-primary hover:bg-primary/5",
  ghost: "text-muted hover:bg-surface",
};

const sizeClasses: Record<Size, string> = {
  sm: "h-8 px-3 text-sm rounded-full gap-1.5",
  md: "h-10 px-4 text-sm rounded-full gap-2",
  lg: "h-12 px-6 text-base rounded-full gap-2",
};

interface CommonProps {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  children: ReactNode;
  className?: string;
}

type ButtonAsButton = CommonProps &
  Omit<ButtonHTMLAttributes<HTMLButtonElement>, keyof CommonProps> & {
    href?: undefined;
  };

type ButtonAsLink = CommonProps &
  Omit<AnchorHTMLAttributes<HTMLAnchorElement>, keyof CommonProps> & {
    href: string;
    disabled?: boolean;
  };

export type ButtonProps = ButtonAsButton | ButtonAsLink;

function Spinner() {
  return (
    <svg
      className="h-4 w-4 animate-spin"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

/**
 * Renders an `<a>` (via next/link) when `href` is set, otherwise a `<button>` —
 * matching the Svelte original. The discriminated union means TypeScript now
 * rejects button-only props on the link form and vice versa, which the original
 * `HTMLAttributes<HTMLElement>` base allowed through.
 */
export function Button(props: ButtonProps) {
  const {
    variant = "primary",
    size = "md",
    loading = false,
    children,
    className,
    ...rest
  } = props;

  const classes = cn(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    className,
  );

  const content = (
    <>
      {loading && <Spinner />}
      {children}
    </>
  );

  if (rest.href !== undefined) {
    const { href, disabled, ...anchorProps } =
      rest as ButtonAsLink;
    return (
      <Link
        href={href}
        className={classes}
        aria-disabled={disabled || loading ? "true" : undefined}
        {...anchorProps}
      >
        {content}
      </Link>
    );
  }

  const {
    type = "button",
    disabled,
    ...buttonProps
  } = rest as ButtonAsButton;

  return (
    <button
      type={type}
      className={classes}
      disabled={disabled || loading}
      {...buttonProps}
    >
      {content}
    </button>
  );
}

export default Button;

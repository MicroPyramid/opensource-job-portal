import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

type Variant = "primary" | "success" | "warning" | "error" | "neutral";
type Size = "sm" | "md";

const sizeClasses: Record<Size, string> = {
  sm: "px-1.5 py-0.5 text-[11px]",
  md: "px-2 py-0.5 text-xs",
};

const variantClasses: Record<Variant, string> = {
  primary: "bg-primary/10 text-primary",
  success: "bg-success-light text-success",
  warning: "bg-warning-light text-warning",
  error: "bg-error-light text-error",
  neutral: "bg-surface text-muted",
};

export interface BadgeProps {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
  className?: string;
}

export function Badge({
  variant = "primary",
  size = "md",
  children,
  className,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded",
        sizeClasses[size],
        variantClasses[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}

export default Badge;

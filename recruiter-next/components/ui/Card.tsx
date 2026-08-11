import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

type Padding = "none" | "sm" | "md" | "lg";

const paddingClasses: Record<Padding, string> = {
  none: "",
  sm: "p-3",
  md: "p-4",
  lg: "p-6",
};

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
  padding?: Padding;
  children: ReactNode;
}

export function Card({
  hover = false,
  padding = "md",
  children,
  className,
  ...rest
}: CardProps) {
  return (
    <div
      className={cn(
        "bg-white border border-border rounded-lg",
        hover ? "hover:shadow-md transition-shadow cursor-pointer" : "shadow-sm",
        paddingClasses[padding],
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

export default Card;

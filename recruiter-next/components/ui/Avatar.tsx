import { cn } from "@/lib/utils/cn";

type Size = "xs" | "sm" | "md" | "lg";
type Shape = "circle" | "rounded";

const sizeClasses: Record<Size, string> = {
  xs: "w-6 h-6 text-xs",
  sm: "w-8 h-8 text-sm",
  md: "w-12 h-12 text-base",
  lg: "w-18 h-18 text-xl",
};

const shapeClasses: Record<Shape, string> = {
  circle: "rounded-full",
  rounded: "rounded-lg",
};

export interface AvatarProps {
  src?: string | null;
  /** Person's name, used to derive the initials and as the image alt fallback. */
  name?: string;
  alt?: string;
  size?: Size;
  shape?: Shape;
  fallback?: string;
  className?: string;
}

export function Avatar({
  src = null,
  name = "",
  alt = "",
  size = "md",
  shape = "circle",
  fallback = "",
  className,
}: AvatarProps) {
  const label = alt || name;

  const initials =
    fallback ||
    label
      .split(" ")
      .filter(Boolean)
      .map((word) => word[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);

  const classes = cn(sizeClasses[size], shapeClasses[shape], className);

  if (src) {
    // Deliberately a plain <img>, not next/image — this matches the original and
    // degrades to a broken-image icon rather than an optimiser error.
    //
    // next/image is a post-parity follow-up because the source URLs are not
    // currently clean: all 3747 company logos are stored as absolute CDN URLs, so
    // Django prefixes MEDIA_URL onto them and emits "/media/https%3A/<host>/…",
    // which 404s. The optimiser would need those hosts allow-listed *and* the
    // double-prefix fixed server-side. See MIGRATION.md § Backend follow-ups.
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={src} alt={label} className={cn(classes, "object-cover")} />;
  }

  return (
    <div
      className={cn(
        classes,
        "flex items-center justify-center bg-primary/10 text-primary font-medium",
      )}
    >
      {initials}
    </div>
  );
}

export default Avatar;

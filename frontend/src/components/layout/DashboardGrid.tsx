import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

/**
 * Mobile-first dashboard grid: 1 column on mobile, 2 on tablet, 12 on desktop.
 * Children control their own span via `GridItem`.
 */
export function DashboardGrid({ children }: { children: ReactNode }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-5 lg:grid-cols-12">{children}</div>
  );
}

type Span = 3 | 4 | 5 | 6 | 8 | 12;

const SPAN_CLASSES: Record<Span, string> = {
  3: "lg:col-span-3",
  4: "lg:col-span-4",
  5: "lg:col-span-5",
  6: "lg:col-span-6",
  8: "lg:col-span-8",
  12: "sm:col-span-2 lg:col-span-12",
};

interface GridItemProps {
  span?: Span;
  fullWidthOnTablet?: boolean;
  className?: string;
  children: ReactNode;
}

export function GridItem({
  span = 4,
  fullWidthOnTablet = false,
  className,
  children,
}: GridItemProps) {
  return (
    <div
      className={cn(
        "flex min-w-0 flex-col",
        fullWidthOnTablet && "sm:col-span-2",
        SPAN_CLASSES[span],
        className,
      )}
    >
      {children}
    </div>
  );
}

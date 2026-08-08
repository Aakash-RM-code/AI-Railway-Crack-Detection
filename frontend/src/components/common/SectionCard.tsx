import type { ReactNode } from "react";
import { AlertCircle, Clock } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { formatTimeFromMs } from "@/utils/format";

interface SectionCardProps {
  title?: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  contentClassName?: string;
  /** Shows a skeleton placeholder while the first payload is in flight. */
  loading?: boolean;
  /** Shows an inline error state instead of the card body. */
  error?: boolean;
  errorMessage?: string;
  /** Called when the user taps "Retry" in the error state. */
  onRetry?: () => void;
  /** Epoch ms of the last successful fetch; renders a small "Updated" footer. */
  updatedAt?: number;
}

function CardSkeleton() {
  return (
    <div className="flex flex-col gap-3" aria-hidden>
      <Skeleton className="h-6 w-32" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
      <div className="mt-2 grid grid-cols-2 gap-3">
        <Skeleton className="h-14 w-full" />
        <Skeleton className="h-14 w-full" />
      </div>
    </div>
  );
}

/** Shared card shell used by every dashboard panel. */
export function SectionCard({
  title,
  description,
  actions,
  children,
  className,
  contentClassName,
  loading = false,
  error = false,
  errorMessage = "Telemetry unavailable. Retrying…",
  onRetry,
  updatedAt,
}: SectionCardProps) {
  const showBody = !loading && !error;

  return (
    <section
      className={cn(
        "flex min-w-0 flex-col rounded-xl border border-border bg-card shadow-card",
        className,
      )}
      aria-busy={loading || undefined}
    >
      {(title || actions) && (
        <header className="flex flex-wrap items-start justify-between gap-3 border-b border-border px-4 py-3 sm:px-5">
          <div className="min-w-0">
            {title && (
              <h2 className="truncate text-sm font-semibold tracking-tight text-foreground">
                {title}
              </h2>
            )}
            {description && <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </header>
      )}
      <div className={cn("flex-1 p-4 sm:p-5", showBody && contentClassName)}>
        {loading && <CardSkeleton />}
        {error && !loading && (
          <div
            role="status"
            className="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive"
          >
            <AlertCircle className="size-4 shrink-0" aria-hidden />
            <span className="min-w-0 flex-1">{errorMessage}</span>
            {onRetry && (
              <Button
                type="button"
                size="sm"
                variant="outline"
                className="ml-auto shrink-0 border-destructive/40 hover:border-destructive/60"
                onClick={onRetry}
              >
                Retry
              </Button>
            )}
          </div>
        )}
        {showBody && children}
      </div>
      {updatedAt !== undefined && updatedAt > 0 && !loading && !error && (
        <footer className="flex items-center justify-between gap-3 border-t border-border px-4 py-2.5 sm:px-5">
          <span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
            <Clock className="size-3" aria-hidden />
            Updated {formatTimeFromMs(updatedAt)}
          </span>
        </footer>
      )}
    </section>
  );
}

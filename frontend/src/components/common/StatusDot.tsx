import { cn } from "@/lib/utils";
import { CONNECTION_LABELS } from "@/constants/monitoring";
import type { ConnectionState } from "@/types/monitoring";

const STATE_STYLES: Record<ConnectionState, string> = {
  connected: "bg-success",
  connecting: "bg-warning animate-pulse",
  disconnected: "bg-muted-foreground",
  error: "bg-destructive",
};

interface StatusDotProps {
  state: ConnectionState;
  className?: string;
}

export function StatusDot({ state, className }: StatusDotProps) {
  return (
    <span
      role="img"
      aria-label={CONNECTION_LABELS[state]}
      className={cn("inline-block size-2 shrink-0 rounded-full", STATE_STYLES[state], className)}
    />
  );
}

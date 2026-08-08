import { StatusDot } from "@/components/common/StatusDot";
import { CONNECTION_LABELS } from "@/constants/monitoring";
import type { ConnectionState } from "@/types/monitoring";

interface ConnectionChipProps {
  label: string;
  state: ConnectionState;
}

export function ConnectionChip({ label, state }: ConnectionChipProps) {
  return (
    <div
      className="flex items-center gap-2 rounded-md border border-border bg-background/60 px-2.5 py-1.5"
      title={`${label}: ${CONNECTION_LABELS[state]}`}
    >
      <StatusDot state={state} />
      <span className="text-xs font-medium text-foreground">{label}</span>
      <span className="text-xs text-muted-foreground">{CONNECTION_LABELS[state]}</span>
    </div>
  );
}

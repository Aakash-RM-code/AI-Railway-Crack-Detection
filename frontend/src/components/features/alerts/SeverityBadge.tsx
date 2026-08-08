import { SEVERITY_LABELS, SEVERITY_TOKEN } from "@/constants/monitoring";
import { cn } from "@/lib/utils";
import type { Severity } from "@/types/monitoring";

type SeverityToken = "success" | "primary" | "warning" | "danger";

const TOKEN_STYLES: Record<SeverityToken, string> = {
  success: "border-success/40 bg-success/15 text-success",
  primary: "border-primary/40 bg-primary/15 text-primary",
  warning: "border-warning/40 bg-warning/15 text-warning",
  danger: "border-destructive/40 bg-destructive/15 text-destructive",
};

export function SeverityBadge({ severity, className }: { severity: Severity; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
        TOKEN_STYLES[SEVERITY_TOKEN[severity]],
        className,
      )}
    >
      {SEVERITY_LABELS[severity]}
    </span>
  );
}

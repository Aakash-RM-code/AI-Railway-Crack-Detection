import { cn } from "@/lib/utils";

interface LabeledValueProps {
  label: string;
  value: string | number;
  hint?: string;
  className?: string;
}

export function LabeledValue({ label, value, hint, className }: LabeledValueProps) {
  return (
    <div className={cn("min-w-0", className)}>
      <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="truncate text-sm font-medium text-foreground">{value}</p>
      {hint && <p className="truncate text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}

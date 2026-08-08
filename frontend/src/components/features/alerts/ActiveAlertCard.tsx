import { AlertTriangle, ShieldCheck } from "lucide-react";

import { LabeledValue } from "@/components/common/LabeledValue";
import { SectionCard } from "@/components/common/SectionCard";
import { SeverityBadge } from "@/components/features/alerts/SeverityBadge";
import { POLLING_INTERVALS } from "@/config/app";
import { CRACK_CLASS_LABELS } from "@/constants/monitoring";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import { formatConfidence, formatTime } from "@/utils/format";

export function ActiveAlertCard() {
  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["alert"],
    () => monitoringApi.getLatestAlert(),
    POLLING_INTERVALS.alert,
    undefined,
    "telemetry",
  );

  const critical = data?.severity === "HIGH" || data?.severity === "CRITICAL";
  const Icon = critical ? AlertTriangle : ShieldCheck;

  return (
    <SectionCard
      title="Active Alert"
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
      actions={data ? <SeverityBadge severity={data.severity} /> : null}
      contentClassName="flex flex-col gap-4"
    >
      <div className="flex items-start gap-3">
        <span
          className={`grid size-10 shrink-0 place-items-center rounded-lg ${
            critical ? "bg-destructive/15 text-destructive" : "bg-success/15 text-success"
          }`}
        >
          <Icon className={`size-5 ${critical ? "animate-pulse" : ""}`} aria-hidden />
        </span>
        <p className="min-w-0 text-sm text-foreground" aria-live="polite" aria-atomic="true">
          {data?.message ?? "Awaiting telemetry…"}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <LabeledValue
          label="Class"
          value={data?.crackClass ? CRACK_CLASS_LABELS[data.crackClass] : "None"}
        />
        <LabeledValue label="Confidence" value={formatConfidence(data?.confidence ?? 0)} />
        <LabeledValue label="Detected" value={data ? formatTime(data.timestamp) : "—"} />
        <LabeledValue label="Alert ID" value={data?.id ?? "—"} />
      </div>
    </SectionCard>
  );
}

import { Activity } from "lucide-react";

import { LabeledValue } from "@/components/common/LabeledValue";
import { SectionCard } from "@/components/common/SectionCard";
import { Progress } from "@/components/ui/progress";
import { POLLING_INTERVALS } from "@/config/app";
import { HEALTH_STATUS_LABELS } from "@/constants/monitoring";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import { formatDistance, formatTime } from "@/utils/format";
import type { HealthStatus } from "@/types/monitoring";

const STATUS_STYLES: Record<HealthStatus, string> = {
  excellent: "text-success",
  good: "text-success",
  warning: "text-warning",
  critical: "text-destructive",
};

export function TrackHealthCard() {
  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["track-health"],
    () => monitoringApi.getTrackHealth(),
    POLLING_INTERVALS.health,
    undefined,
    "telemetry",
  );

  const score = data?.overall ?? 0;

  return (
    <SectionCard
      title="Track Health"
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
      actions={<Activity className="size-4 text-muted-foreground" aria-hidden />}
      contentClassName="flex flex-col gap-4"
    >
      <div className="flex items-baseline gap-2">
        <span className="text-4xl font-semibold tracking-tight text-foreground">
          {Math.round(score)}
        </span>
        <span className="text-sm text-muted-foreground">/ 100</span>
        {data && (
          <span className={`ml-auto text-sm font-medium ${STATUS_STYLES[data.status]}`}>
            {HEALTH_STATUS_LABELS[data.status]}
          </span>
        )}
      </div>

      <Progress value={score} aria-label="Overall track health score" />

      <div className="grid grid-cols-2 gap-4">
        <LabeledValue label="Inspected" value={data ? formatDistance(data.inspectedMeters) : "—"} />
        <LabeledValue label="Updated" value={data ? formatTime(data.updatedAt) : "—"} />
      </div>
    </SectionCard>
  );
}

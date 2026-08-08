import { MapPin, Satellite } from "lucide-react";

import { LabeledValue } from "@/components/common/LabeledValue";
import { SectionCard } from "@/components/common/SectionCard";
import { POLLING_INTERVALS } from "@/config/app";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import { formatCoordinate, formatTime } from "@/utils/format";

export function GpsCard() {
  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["gps"],
    () => monitoringApi.getGps(),
    POLLING_INTERVALS.gps,
    undefined,
    "telemetry",
  );

  return (
    <SectionCard
      title="GPS Location"
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
      actions={
        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Satellite className="size-4" aria-hidden />
          {data?.satellites ?? 0} sats
        </span>
      }
      contentClassName="flex flex-col gap-4"
    >
      <div className="flex items-center gap-3 rounded-lg border border-border bg-background/60 p-3">
        <MapPin
          className={`size-5 ${data?.hasFix ? "text-primary" : "text-muted-foreground"}`}
          aria-hidden
        />
        <div className="min-w-0">
          <p className="truncate font-mono text-sm text-foreground">
            {data ? `${formatCoordinate(data.latitude)}, ${formatCoordinate(data.longitude)}` : "—"}
          </p>
          <p className="text-xs text-muted-foreground">
            {data?.hasFix ? "Fix acquired" : "No satellite fix"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <LabeledValue label="Latitude" value={data ? formatCoordinate(data.latitude) : "—"} />
        <LabeledValue label="Longitude" value={data ? formatCoordinate(data.longitude) : "—"} />
        <LabeledValue label="Updated" value={data ? formatTime(data.updatedAt) : "—"} />
        <LabeledValue label="Satellites" value={data?.satellites ?? 0} />
      </div>
    </SectionCard>
  );
}

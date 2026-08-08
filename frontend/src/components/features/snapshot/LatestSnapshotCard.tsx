import { ImageOff } from "lucide-react";

import { LabeledValue } from "@/components/common/LabeledValue";
import { SectionCard } from "@/components/common/SectionCard";
import { SeverityBadge } from "@/components/features/alerts/SeverityBadge";
import { POLLING_INTERVALS } from "@/config/app";
import { resolveApiUrl } from "@/config/endpoints";
import { CRACK_CLASS_LABELS } from "@/constants/monitoring";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import { formatTime } from "@/utils/format";

export function LatestSnapshotCard() {
  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["snapshot"],
    () => monitoringApi.getLatestSnapshot(),
    POLLING_INTERVALS.snapshot,
    undefined,
    "detections",
  );

  const snapshotUrl = resolveApiUrl(data?.imageUrl);

  return (
    <SectionCard
      title="Latest Snapshot"
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
      actions={data ? <SeverityBadge severity={data.severity} /> : null}
      contentClassName="flex flex-col gap-4"
    >
      <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-border bg-background">
        {snapshotUrl ? (
          <img
            src={snapshotUrl}
            alt={`Detection snapshot ${data?.id ?? ""}`}
            loading="lazy"
            className="size-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-muted-foreground">
            <ImageOff className="size-8" aria-hidden />
            <span className="text-xs">No snapshot available yet</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <LabeledValue
          label="Class"
          value={data?.crackClass ? CRACK_CLASS_LABELS[data.crackClass] : "None"}
        />
        <LabeledValue label="Captured" value={data ? formatTime(data.timestamp) : "—"} />
      </div>
    </SectionCard>
  );
}

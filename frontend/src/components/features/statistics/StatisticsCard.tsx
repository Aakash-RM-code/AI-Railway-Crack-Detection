import { AlertOctagon, Layers, Minus, TrendingUp, Unlink } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { SectionCard } from "@/components/common/SectionCard";
import { POLLING_INTERVALS } from "@/config/app";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import { formatNumber } from "@/utils/format";
import type { Statistics } from "@/types/monitoring";

const TILES: Array<{ key: keyof Statistics; label: string; icon: LucideIcon; accent: string }> = [
  { key: "totalDetections", label: "Total Detections", icon: TrendingUp, accent: "text-primary" },
  { key: "smallCrack", label: "Small Cracks", icon: Minus, accent: "text-success" },
  { key: "mediumCrack", label: "Medium Cracks", icon: Layers, accent: "text-warning" },
  { key: "largeCrack", label: "Large Cracks", icon: AlertOctagon, accent: "text-warning" },
  { key: "brokenChain", label: "Broken Chains", icon: Unlink, accent: "text-destructive" },
  {
    key: "criticalAlerts",
    label: "Critical Alerts",
    icon: AlertOctagon,
    accent: "text-destructive",
  },
];

export function StatisticsCard() {
  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["statistics"],
    () => monitoringApi.getStatistics(),
    POLLING_INTERVALS.statistics,
    undefined,
    "telemetry",
  );

  return (
    <SectionCard
      title="Detection Statistics"
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
    >
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {TILES.map(({ key, label, icon: Icon, accent }) => (
          <div key={key} className="rounded-lg border border-border bg-background/60 p-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">{label}</span>
              <Icon className={`size-4 ${accent}`} aria-hidden />
            </div>
            <p className="mt-2 text-2xl font-semibold tracking-tight text-foreground">
              {formatNumber(data?.[key] ?? 0)}
            </p>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

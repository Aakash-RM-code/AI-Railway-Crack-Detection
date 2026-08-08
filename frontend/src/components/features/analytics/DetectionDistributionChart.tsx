import { memo, useMemo } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { SectionCard } from "@/components/common/SectionCard";
import { POLLING_INTERVALS } from "@/config/app";
import { CRACK_CLASS_LABELS, DISTRIBUTION_SLICE_COLORS } from "@/constants/monitoring";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";

export const DetectionDistributionChart = memo(function DetectionDistributionChart() {
  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["distribution"],
    () => monitoringApi.getDetectionDistribution(),
    POLLING_INTERVALS.statistics,
  );

  const chartData = useMemo(
    () =>
      (data ?? []).map((slice) => ({
        name: CRACK_CLASS_LABELS[slice.crackClass],
        value: slice.count,
      })),
    [data],
  );

  return (
    <SectionCard
      title="Detection Distribution"
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
    >
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              innerRadius="55%"
              outerRadius="80%"
              paddingAngle={2}
              stroke="var(--color-card)"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={entry.name}
                  fill={DISTRIBUTION_SLICE_COLORS[index % DISTRIBUTION_SLICE_COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "var(--color-popover)",
                border: "1px solid var(--color-border)",
                borderRadius: "0.5rem",
                color: "var(--color-popover-foreground)",
                fontSize: "0.75rem",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <ul className="mt-2 grid grid-cols-2 gap-2">
        {chartData.map((entry, index) => (
          <li key={entry.name} className="flex items-center gap-2 text-xs text-muted-foreground">
            <span
              className="size-2.5 rounded-full"
              style={{
                background: DISTRIBUTION_SLICE_COLORS[index % DISTRIBUTION_SLICE_COLORS.length],
              }}
            />
            <span className="truncate">{entry.name}</span>
            <span className="ml-auto font-medium text-foreground">{entry.value}</span>
          </li>
        ))}
      </ul>
    </SectionCard>
  );
});

import { memo, useMemo } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { SectionCard } from "@/components/common/SectionCard";
import { POLLING_INTERVALS } from "@/config/app";
import { SEVERITY_TREND_SERIES } from "@/constants/monitoring";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import { formatTime } from "@/utils/format";

export const SeverityTrendChart = memo(function SeverityTrendChart() {
  const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["severity-trend"],
    () => monitoringApi.getSeverityTrend(),
    POLLING_INTERVALS.statistics,
  );

  const chartData = useMemo(
    () =>
      (data ?? []).map((point) => ({
        ...point,
        label: formatTime(point.timestamp).slice(0, 5),
      })),
    [data],
  );

  return (
    <SectionCard
      title="Severity Trend"
      description="Detections per interval"
      className="h-full"
      loading={isPending}
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
    >
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
            <defs>
              {SEVERITY_TREND_SERIES.map((series) => (
                <linearGradient
                  key={series.key}
                  id={`fill-${series.key}`}
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="0%" stopColor={series.color} stopOpacity={0.5} />
                  <stop offset="100%" stopColor={series.color} stopOpacity={0.04} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                background: "var(--color-popover)",
                border: "1px solid var(--color-border)",
                borderRadius: "0.5rem",
                color: "var(--color-popover-foreground)",
                fontSize: "0.75rem",
              }}
            />
            <Legend wrapperStyle={{ fontSize: "0.75rem" }} />
            {SEVERITY_TREND_SERIES.map((series) => (
              <Area
                key={series.key}
                type="monotone"
                dataKey={series.key}
                name={series.label}
                stackId="1"
                stroke={series.color}
                fill={`url(#fill-${series.key})`}
                strokeWidth={2}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </SectionCard>
  );
});

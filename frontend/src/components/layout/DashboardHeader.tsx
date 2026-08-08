import { Activity, TrainFront } from "lucide-react";

import { ConnectionChip } from "@/components/common/ConnectionChip";
import { StatusDot } from "@/components/common/StatusDot";
import { APP_CONFIG, POLLING_INTERVALS } from "@/config/app";
import { useClock } from "@/hooks/useClock";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import { formatUptime } from "@/utils/format";

export function DashboardHeader() {
  const now = useClock();
  const { data: status } = useLiveQuery(
    ["system-status"],
    () => monitoringApi.getSystemStatus(),
    POLLING_INTERVALS.systemStatus,
  );

  return (
    <header className="rounded-xl border border-border bg-card shadow-card">
      <div className="flex flex-col gap-4 p-4 sm:p-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-primary">
            <TrainFront className="size-5" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <h1 className="text-base font-semibold leading-tight tracking-tight text-foreground sm:text-lg lg:text-xl">
              {APP_CONFIG.name}
            </h1>
            <p className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <StatusDot state={status?.online === false ? "error" : "connected"} />
                {status?.online === false ? "System Offline" : "System Online"}
              </span>
              {status && (
                <span className="inline-flex items-center gap-1.5">
                  <Activity className="size-3" aria-hidden="true" />
                  Uptime {formatUptime(status.uptimeSeconds)}
                </span>
              )}
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3 lg:items-end">
          <div className="text-xs text-muted-foreground sm:text-sm" suppressHydrationWarning>
            {now ? (
              <span className="font-mono tabular-nums text-foreground">
                {now.toLocaleDateString(undefined, {
                  weekday: "short",
                  year: "numeric",
                  month: "short",
                  day: "2-digit",
                })}{" "}
                · {now.toLocaleTimeString(undefined, { hour12: false })}
              </span>
            ) : (
              <span className="font-mono text-muted-foreground">--</span>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {(status?.devices ?? []).map((device) => (
              <ConnectionChip key={device.id} label={device.label} state={device.state} />
            ))}
          </div>
        </div>
      </div>
    </header>
  );
}

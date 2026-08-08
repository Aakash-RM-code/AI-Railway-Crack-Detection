import { StatusDot } from "@/components/common/StatusDot";
import { APP_CONFIG, POLLING_INTERVALS } from "@/config/app";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";

export function DashboardFooter() {
  const { data: status } = useLiveQuery(
    ["system-status"],
    () => monitoringApi.getSystemStatus(),
    POLLING_INTERVALS.systemStatus,
  );

  return (
    <footer className="rounded-xl border border-border bg-card px-4 py-3 shadow-card sm:px-5">
      <div className="flex flex-col items-start justify-between gap-2 text-xs text-muted-foreground sm:flex-row sm:items-center">
        <p>Version {APP_CONFIG.version}</p>
        <p className="truncate">{APP_CONFIG.developer}</p>
        <p className="inline-flex items-center gap-1.5">
          <StatusDot state={status?.online === false ? "error" : "connected"} />
          {status?.online === false ? "Offline" : "All systems operational"}
        </p>
      </div>
    </footer>
  );
}

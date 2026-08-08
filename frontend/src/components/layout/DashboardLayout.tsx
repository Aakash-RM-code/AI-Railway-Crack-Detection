import type { ReactNode } from "react";
import { WifiOff } from "lucide-react";

import { DashboardFooter } from "@/components/layout/DashboardFooter";
import { DashboardHeader } from "@/components/layout/DashboardHeader";
import { POLLING_INTERVALS } from "@/config/app";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";

/** Page chrome: skip link, header, responsive content container, offline banner, footer. */
export function DashboardLayout({ children }: { children: ReactNode }) {
  const { data: status } = useLiveQuery(
    ["system-status"],
    () => monitoringApi.getSystemStatus(),
    POLLING_INTERVALS.systemStatus,
  );

  const offline = status?.online === false;

  return (
    <div className="min-h-screen bg-background">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground focus:shadow-lg"
      >
        Skip to content
      </a>
      <div className="mx-auto flex w-full max-w-[1600px] flex-col gap-4 px-3 py-4 sm:gap-5 sm:px-5 sm:py-6 lg:px-8">
        <DashboardHeader />
        {offline && (
          <div
            role="status"
            className="flex items-center gap-2 rounded-xl border border-destructive/40 bg-destructive/10 px-4 py-2.5 text-sm text-destructive"
          >
            <WifiOff className="size-4 shrink-0" aria-hidden />
            <span className="min-w-0">System offline — telemetry may be stale.</span>
          </div>
        )}
        <main id="main-content" tabIndex={-1} className="flex-1 outline-none">
          {children}
        </main>
        <DashboardFooter />
      </div>
    </div>
  );
}

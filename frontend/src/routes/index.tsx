import { createFileRoute } from "@tanstack/react-router";

import { ActiveAlertCard } from "@/components/features/alerts/ActiveAlertCard";
import { DetectionDistributionChart } from "@/components/features/analytics/DetectionDistributionChart";
import { SeverityTrendChart } from "@/components/features/analytics/SeverityTrendChart";
import { CameraFeedCard } from "@/components/features/camera/CameraFeedCard";
import { GpsCard } from "@/components/features/gps/GpsCard";
import { GsmCard } from "@/components/features/gsm/GsmCard";
import { TrackHealthCard } from "@/components/features/health/TrackHealthCard";
import { DetectionHistoryTable } from "@/components/features/history/DetectionHistoryTable";
import { RoverControlCard } from "@/components/features/rover/RoverControlCard";
import { LatestSnapshotCard } from "@/components/features/snapshot/LatestSnapshotCard";
import { StatisticsCard } from "@/components/features/statistics/StatisticsCard";
import { DashboardGrid, GridItem } from "@/components/layout/DashboardGrid";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { APP_CONFIG } from "@/config/app";

const TITLE = `${APP_CONFIG.name} | Live Dashboard`;
const DESCRIPTION =
  "Industrial dashboard for real-time railway crack detection, rover control, GPS/GSM telemetry and track health monitoring.";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESCRIPTION },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESCRIPTION },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  return (
    <DashboardLayout>
      <DashboardGrid>
        <GridItem span={8} fullWidthOnTablet>
          <CameraFeedCard />
        </GridItem>
        <GridItem span={4}>
          <RoverControlCard />
        </GridItem>
        <GridItem span={4}>
          <ActiveAlertCard />
        </GridItem>
        <GridItem span={4}>
          <TrackHealthCard />
        </GridItem>
        <GridItem span={4}>
          <GpsCard />
        </GridItem>
        <GridItem span={4}>
          <GsmCard />
        </GridItem>
        <GridItem span={8} fullWidthOnTablet>
          <StatisticsCard />
        </GridItem>
        <GridItem span={6} fullWidthOnTablet>
          <DetectionDistributionChart />
        </GridItem>
        <GridItem span={6} fullWidthOnTablet>
          <SeverityTrendChart />
        </GridItem>
        <GridItem span={4}>
          <LatestSnapshotCard />
        </GridItem>
        <GridItem span={8} fullWidthOnTablet>
          <DetectionHistoryTable />
        </GridItem>
      </DashboardGrid>
    </DashboardLayout>
  );
}

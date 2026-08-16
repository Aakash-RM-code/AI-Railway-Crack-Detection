import { useMutation, useQueryClient } from "@tanstack/react-query";

import { SectionCard } from "@/components/common/SectionCard";
import { StatusDot } from "@/components/common/StatusDot";
import { Button } from "@/components/ui/button";
import { POLLING_INTERVALS } from "@/config/app";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";

import { NativeVideoFeed } from "./NativeVideoFeed";

export function CameraFeedCard() {
  const queryClient = useQueryClient();

  const { data, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["camera"],
    () => monitoringApi.getCameraState(),
    POLLING_INTERVALS.camera,
    undefined,
    "camera-status",
  );

  const connect = useMutation({
    mutationFn: () => monitoringApi.connectCamera({ source: "esp32-cam" }),
    onSuccess: (state) => queryClient.setQueryData(["camera"], state),
  });
  const disconnect = useMutation({
    mutationFn: () => monitoringApi.disconnectCamera(),
    onSuccess: (state) => queryClient.setQueryData(["camera"], state),
  });

  const state = data?.state ?? "disconnected";
  const live = state === "connected";
  const nativeStreamUrl = data?.nativeStreamUrl ?? null;

  const cameraFps = data?.cameraFps ?? data?.fps ?? 0;
  const displayFps = data?.displayFps ?? 0;
  const inferenceFps = data?.inferenceFps ?? 0;

  return (
    <SectionCard
      title="Live Camera Feed"
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
      description="ESP32-CAM"
      className="h-full"
      actions={
        <div className="flex items-center gap-2 rounded-md border border-border px-2 py-1">
          <StatusDot state={state} />
          <span className="text-xs text-muted-foreground">
            {live ? `${Math.round(cameraFps)} FPS` : "Offline"}
          </span>
        </div>
      }
      contentClassName="flex flex-col gap-4"
    >
      <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-border bg-background">
        <NativeVideoFeed
          nativeStreamUrl={nativeStreamUrl ?? ""}
          enabled={live && !!nativeStreamUrl}
        />
        {live && (
          <span className="absolute left-3 top-3 z-10 flex items-center gap-2 rounded-md bg-background/80 px-2 py-1 text-xs font-medium text-foreground">
            <span className="size-2 animate-pulse rounded-full bg-destructive" /> LIVE
          </span>
        )}
        {data && (
          <span className="absolute bottom-3 right-3 z-10 rounded-md bg-background/80 px-2 py-1 text-xs text-muted-foreground">
            {data.width}×{data.height} · {Math.round(cameraFps)} cam · {Math.round(displayFps)} disp
            · {Math.round(inferenceFps)} AI
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Button
          size="sm"
          variant={live ? "default" : "outline"}
          disabled={connect.isPending || live}
          onClick={() => connect.mutate()}
        >
          Connect
        </Button>
        <Button
          size="sm"
          variant="ghost"
          disabled={!live || disconnect.isPending}
          onClick={() => disconnect.mutate()}
        >
          Disconnect
        </Button>
      </div>
    </SectionCard>
  );
}

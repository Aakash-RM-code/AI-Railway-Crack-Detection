import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload } from "lucide-react";
import { useRef } from "react";

import { SectionCard } from "@/components/common/SectionCard";
import { StatusDot } from "@/components/common/StatusDot";
import { Button } from "@/components/ui/button";
import { POLLING_INTERVALS } from "@/config/app";
import { CAMERA_SOURCE_LABELS } from "@/constants/monitoring";
import { useLiveQuery } from "@/hooks/useLiveQuery";
import { monitoringApi } from "@/services";
import type { CameraSource } from "@/types/monitoring";

import { MjpegPlayer } from "./MjpegPlayer";

const SOURCES: CameraSource[] = ["usb", "esp32-cam", "demo-video"];

export function CameraFeedCard() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data, isError, refetch, dataUpdatedAt } = useLiveQuery(
    ["camera"],
    () => monitoringApi.getCameraState(),
    POLLING_INTERVALS.camera,
    undefined,
    "camera-status",
  );

  const connect = useMutation({
    mutationFn: (source: CameraSource) => monitoringApi.connectCamera({ source }),
    onSuccess: (state) => queryClient.setQueryData(["camera"], state),
  });
  const disconnect = useMutation({
    mutationFn: () => monitoringApi.disconnectCamera(),
    onSuccess: (state) => queryClient.setQueryData(["camera"], state),
  });
  const uploadVideo = useMutation({
    mutationFn: (file: File) => monitoringApi.uploadDemoVideo(file),
    onSuccess: (state) => queryClient.setQueryData(["camera"], state),
  });

  const state = data?.state ?? "disconnected";
  const live = state === "connected";
  const busy = connect.isPending || uploadVideo.isPending;

  const handleSourceClick = (source: CameraSource) => {
    if (source === "demo-video") {
      // Open the native file picker for demo video upload
      fileInputRef.current?.click();
    } else {
      connect.mutate(source);
    }
  };

  const handleFileSelected = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadVideo.mutate(file);
    }
    // Reset the input so the same file can be re-selected
    event.target.value = "";
  };

  return (
    <SectionCard
      title="Live Camera Feed"
      error={isError}
      onRetry={refetch}
      updatedAt={dataUpdatedAt}
      description={data ? CAMERA_SOURCE_LABELS[data.source] : "Awaiting source"}
      className="h-full"
      actions={
        <div className="flex items-center gap-2 rounded-md border border-border px-2 py-1">
          <StatusDot state={state} />
          <span className="text-xs text-muted-foreground">
            {live ? `${data?.fps ?? 0} FPS` : "Offline"}
          </span>
        </div>
      }
      contentClassName="flex flex-col gap-4"
    >
      <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-border bg-background">
        <MjpegPlayer enabled={live} />
        {live && (
          <span className="absolute left-3 top-3 z-10 flex items-center gap-2 rounded-md bg-background/80 px-2 py-1 text-xs font-medium text-foreground">
            <span className="size-2 animate-pulse rounded-full bg-destructive" /> LIVE
          </span>
        )}
        {data && (
          <span className="absolute bottom-3 right-3 z-10 rounded-md bg-background/80 px-2 py-1 text-xs text-muted-foreground">
            {data.width}×{data.height}
          </span>
        )}
      </div>

      {/* Hidden file input for demo video upload */}
      <input
        ref={fileInputRef}
        type="file"
        accept="video/mp4,video/avi,video/quicktime,video/x-matroska,video/webm,.mp4,.avi,.mov,.mkv,.webm"
        className="hidden"
        onChange={handleFileSelected}
      />

      <div className="flex flex-wrap items-center gap-2">
        {SOURCES.map((source) => (
          <Button
            key={source}
            size="sm"
            variant={data?.source === source && live ? "default" : "outline"}
            disabled={busy}
            onClick={() => handleSourceClick(source)}
          >
            {source === "demo-video" && <Upload className="mr-1.5 size-3.5" aria-hidden />}
            {CAMERA_SOURCE_LABELS[source]}
          </Button>
        ))}
        <Button
          size="sm"
          variant="ghost"
          className="ml-auto"
          disabled={!live || disconnect.isPending}
          onClick={() => disconnect.mutate()}
        >
          Disconnect
        </Button>
      </div>
    </SectionCard>
  );
}

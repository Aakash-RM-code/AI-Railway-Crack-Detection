/**
 * MjpegPlayer — renders a live MJPEG stream from the FastAPI backend.
 *
 * Delegates all stream lifecycle to useMjpegStream.
 * Shows appropriate states: loading spinner, live feed, error overlay, and disconnected.
 * This component is layout-agnostic — it fills its container absolutely.
 */

import { AlertTriangle, Camera, CameraOff, Loader2 } from "lucide-react";
import { useMjpegStream } from "@/hooks/useMjpegStream";

interface MjpegPlayerProps {
  /** When true the stream URL is constructed and the <img> is mounted. */
  enabled: boolean;
}

export function MjpegPlayer({ enabled }: MjpegPlayerProps) {
  const { src, status, onLoad, onError } = useMjpegStream({ enabled });

  // ── Disconnected / idle ──────────────────────────────────────────
  if (!enabled) {
    return (
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-muted-foreground">
        <CameraOff className="size-8" aria-hidden />
        <span className="text-xs">No camera connected</span>
      </div>
    );
  }

  return (
    <>
      {/* Live MJPEG frame — always mounted while enabled so the browser keeps the connection */}
      {src && (
        <img
          key={src} // key change forces React to unmount/remount on reconnect revision bump
          src={src}
          alt="Live MJPEG camera feed"
          className="absolute inset-0 h-full w-full object-contain"
          onLoad={onLoad}
          onError={onError}
        />
      )}

      {/* Loading overlay — shown while the first frame hasn't arrived yet */}
      {status === "loading" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-background/70 text-muted-foreground">
          <Loader2 className="size-8 animate-spin" aria-hidden />
          <span className="text-xs">Connecting to stream…</span>
        </div>
      )}

      {/* Error overlay — shown briefly while scheduling a reconnect */}
      {status === "error" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-background/70 text-destructive">
          <AlertTriangle className="size-8" aria-hidden />
          <span className="text-xs">Stream interrupted — reconnecting…</span>
        </div>
      )}

      {/* Live indicator icon (top-left corner, behind the LIVE badge in CameraFeedCard) */}
      {status === "live" && (
        <Camera className="absolute bottom-12 left-3 size-5 text-primary opacity-40" aria-hidden />
      )}
    </>
  );
}

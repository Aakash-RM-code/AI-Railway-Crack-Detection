/**
 * useMjpegStream — manages the lifecycle of an MJPEG browser stream.
 *
 * Builds the full stream URL from the backend base URL, tracks live/error state,
 * and schedules automatic reconnection when the stream is interrupted.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { API_BASE_URL } from "@/config/endpoints";

const STREAM_PATH = "/api/camera/stream";
const RECONNECT_DELAY_MS = 3_000;

export type StreamStatus = "idle" | "loading" | "live" | "error";

interface UseMjpegStreamOptions {
  /** Whether the camera is connected and the pipeline is running. */
  enabled: boolean;
}

interface UseMjpegStreamResult {
  /** The fully qualified MJPEG URL to set as <img src>. null when not streaming. */
  src: string | null;
  status: StreamStatus;
  onLoad: () => void;
  onError: () => void;
}

export function useMjpegStream({ enabled }: UseMjpegStreamOptions): UseMjpegStreamResult {
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [revision, setRevision] = useState(0); // bumped on reconnect to force img reload
  const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearRetry = () => {
    if (retryTimer.current !== null) {
      clearTimeout(retryTimer.current);
      retryTimer.current = null;
    }
  };

  // Reset when enabled toggles
  useEffect(() => {
    if (!enabled) {
      clearRetry();
      setStatus("idle");
      return;
    }
    setStatus("loading");
    return clearRetry;
  }, [enabled]);

  const onLoad = useCallback(() => {
    clearRetry();
    setStatus("live");
  }, []);

  const onError = useCallback(() => {
    if (!enabled) return;
    setStatus("error");
    clearRetry();
    retryTimer.current = setTimeout(() => {
      // bump revision so React re-creates the img src and retriggers the request
      setRevision((r) => r + 1);
      setStatus("loading");
    }, RECONNECT_DELAY_MS);
  }, [enabled]);

  // Cache-busting: append revision so browser doesn't serve a stale/broken connection
  const src = enabled ? `${API_BASE_URL}${STREAM_PATH}?r=${revision}` : null;

  return { src, status, onLoad, onError };
}

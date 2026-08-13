/**
 * NativeVideoFeed — renders the ESP32-CAM native MJPEG stream directly in the
 * browser with a detection overlay, bypassing the backend video path entirely.
 *
 * If the browser cannot reach the camera, it falls back to the backend
 * byte-stream proxy (/api/camera/stream), which forwards the MJPEG bytes
 * verbatim. No React state changes per video frame — MJPEG <img> streams update
 * in place and the overlay is driven only by /ws/detections metadata.
 */

import { useCallback, useRef, useState } from "react";

import { API_BASE_URL } from "@/config/endpoints";
import { useDetectionOverlay } from "@/hooks/useDetectionOverlay";

import { DetectionOverlay } from "./DetectionOverlay";

const PROXY_PATH = "/api/camera/stream";

interface NativeVideoFeedProps {
  /** ESP32-CAM native MJPEG URL, e.g. http://10.169.144.41:80/stream */
  nativeStreamUrl: string;
  enabled: boolean;
}

export function NativeVideoFeed({ nativeStreamUrl, enabled }: NativeVideoFeedProps) {
  const [useProxy, setUseProxy] = useState(false);
  const [revision, setRevision] = useState(0);
  const imgRef = useRef<HTMLImageElement>(null);

  const boxes = useDetectionOverlay(enabled);

  // Native stream unreachable → switch to the backend byte proxy.
  const handleNativeError = useCallback(() => {
    setUseProxy(true);
  }, []);

  // Proxy interrupted → force a fresh request.
  const handleProxyError = useCallback(() => {
    setRevision((r) => r + 1);
  }, []);

  if (!enabled) return null;

  const src = useProxy ? `${API_BASE_URL}${PROXY_PATH}?r=${revision}` : nativeStreamUrl;

  return (
    <>
      <img
        key={useProxy ? `proxy-${revision}` : "native"}
        ref={imgRef}
        src={src}
        alt="Live ESP32-CAM feed"
        className="absolute inset-0 h-full w-full object-contain"
        onError={useProxy ? handleProxyError : handleNativeError}
      />
      <DetectionOverlay boxes={boxes} videoRef={imgRef} />
    </>
  );
}

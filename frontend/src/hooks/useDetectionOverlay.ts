/**
 * useDetectionOverlay — subscribes to the /ws/detections channel and holds the
 * newest detection boxes for the camera overlay.
 *
 * Boxes are cleared after a short staleness window so boxes do not linger on
 * the video once the object leaves the frame (the backend only pushes while
 * detections exist).
 */

import { useEffect, useRef, useState } from "react";

import { createRealtimeClient } from "@/services/realtime/client";
import type { DetectionBox, DetectionsMessage } from "@/types/monitoring";

const STALE_MS = 800;

export function useDetectionOverlay(enabled: boolean): DetectionBox[] {
  const [boxes, setBoxes] = useState<DetectionBox[]>([]);
  const clearTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!enabled) {
      setBoxes([]);
      return;
    }

    const client = createRealtimeClient("detections", {
      onMessage: (payload) => {
        const msg = payload as DetectionsMessage;
        if (!Array.isArray(msg.detections)) return;
        setBoxes(msg.detections);
        if (clearTimer.current !== null) clearTimeout(clearTimer.current);
        clearTimer.current = setTimeout(() => setBoxes([]), STALE_MS);
      },
    });

    client.start();
    return () => {
      client.stop();
      if (clearTimer.current !== null) clearTimeout(clearTimer.current);
      clearTimer.current = null;
      setBoxes([]);
    };
  }, [enabled]);

  return boxes;
}

/**
 * Per-channel realtime connection status store.
 *
 * A tiny external store (no provider context) so any hook/component can read
 * the live status of any channel and React Query polling can be gated on it.
 * Written this way to stay outside the React tree and keep the layer modular.
 */

import { useEffect, useState } from "react";

import type { RealtimeChannel, RealtimeStatus } from "./types";

export type RealtimeStatusMap = Record<RealtimeChannel, RealtimeStatus>;

const INITIAL_STATUS: RealtimeStatusMap = {
  telemetry: "offline",
  detections: "offline",
  "camera-status": "offline",
};

let statusMap: RealtimeStatusMap = INITIAL_STATUS;
const listeners = new Set<() => void>();

export function getRealtimeStatus(): RealtimeStatusMap {
  return statusMap;
}

export function getChannelStatus(channel: RealtimeChannel): RealtimeStatus {
  return statusMap[channel];
}

export function setChannelStatus(channel: RealtimeChannel, status: RealtimeStatus): void {
  if (statusMap[channel] === status) return;
  statusMap = { ...statusMap, [channel]: status };
  for (const listener of listeners) listener();
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

/**
 * Returns the current status of a channel, re-rendering on change.
 * A single WS channel "camera-status" is treated as the union for the camera
 * card; other channels map 1:1.
 */
export function useRealtimeStatus(channel: RealtimeChannel): RealtimeStatus {
  const [status, setStatus] = useState<RealtimeStatus>(() => getChannelStatus(channel));

  useEffect(() => {
    setStatus(getChannelStatus(channel));
    return subscribe(() => {
      setStatus(getChannelStatus(channel));
    });
  }, [channel]);

  return status;
}

/** True when the channel has received at least one valid message (live). */
export function useIsRealtimeLive(channel: RealtimeChannel | undefined): boolean {
  const status = useRealtimeStatus(channel ?? "telemetry");
  return channel === undefined ? false : status === "live";
}

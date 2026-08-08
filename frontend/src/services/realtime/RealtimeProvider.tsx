/**
 * RealtimeProvider — mounts one WebSocket client per channel and applies live
 * payloads into the React Query cache as partial merges.
 *
 * Merge strategy: each mapped field is `undefined` unless the WebSocket carried
 * it, and `setQueryData` merges the patch over the last known value (from REST
 * or a previous push). This keeps the frontend domain types complete even
 * though the WebSocket payloads are deliberately small subsets — and preserves
 * REST as the automatic fallback whenever a channel is not "live".
 *
 * Restore-points: when a channel is NOT live, the existing REST polling already
 * running through useLiveQuery keeps the same query keys fresh.
 */

import { useEffect, useRef } from "react";
import { useQueryClient, type QueryClient } from "@tanstack/react-query";

import { createRealtimeClient, type RealtimeClient } from "./client";
import {
  mapCameraStatus,
  mapDetectionsAlert,
  mapDetectionsSnapshot,
  mapTelemetryAlert,
  mapTelemetryCamera,
  mapTelemetryGps,
  mapTelemetryGsm,
  mapTelemetryHealth,
  mapTelemetryRover,
  mapTelemetryStatistics,
  type CameraStatusPayload,
  type DetectionsPayload,
  type TelemetryPayload,
} from "./mappers";
import type { RealtimeChannel } from "./types";

/** Merges a partial patch over the previous cache value, preserving unknowns. */
function mergeCache<T extends object>(prev: T | undefined, patch: Partial<T>): T {
  return { ...(prev ?? {}), ...patch } as T;
}

function patchQuery<T extends object>(
  queryClient: QueryClient,
  queryKey: string[],
  patch: Partial<T>,
) {
  if (patch === undefined) return;
  queryClient.setQueryData<T>(queryKey, (prev) => mergeCache(prev, patch));
}

function handleCameraStatus(queryClient: QueryClient, payload: CameraStatusPayload) {
  patchQuery(queryClient, ["camera"], mapCameraStatus(payload));
}

function handleTelemetry(queryClient: QueryClient, payload: TelemetryPayload) {
  const alert = mapTelemetryAlert(payload);
  if (alert) patchQuery(queryClient, ["alert"], alert);

  const camera = mapTelemetryCamera(payload);
  if (camera) patchQuery(queryClient, ["camera"], camera);

  patchQuery(queryClient, ["track-health"], mapTelemetryHealth(payload));
  patchQuery(queryClient, ["statistics"], mapTelemetryStatistics(payload));
  patchQuery(queryClient, ["rover"], mapTelemetryRover(payload));
  patchQuery(queryClient, ["gps"], mapTelemetryGps(payload));
  patchQuery(queryClient, ["gsm"], mapTelemetryGsm(payload));
}

function handleDetections(queryClient: QueryClient, payload: DetectionsPayload) {
  const alert = mapDetectionsAlert(payload);
  if (alert) patchQuery(queryClient, ["alert"], alert);

  const snapshot = mapDetectionsSnapshot(payload);
  if (snapshot) patchQuery(queryClient, ["snapshot"], snapshot);

  // A new detection arrived — refresh the paginated history table via REST.
  queryClient.invalidateQueries({ queryKey: ["detections"] });
}

export interface RealtimeProviderProps {
  children: React.ReactNode;
}

export function RealtimeProvider({ children }: RealtimeProviderProps) {
  const queryClient = useQueryClient();
  const clientsRef = useRef<Map<RealtimeChannel, RealtimeClient>>(new Map());

  useEffect(() => {
    if (typeof window === "undefined") return; // client-only

    const clients = new Map<RealtimeChannel, RealtimeClient>();

    clients.set(
      "camera-status",
      createRealtimeClient("camera-status", {
        onMessage: (payload) => handleCameraStatus(queryClient, payload as CameraStatusPayload),
      }),
    );

    clients.set(
      "telemetry",
      createRealtimeClient("telemetry", {
        onMessage: (payload) => handleTelemetry(queryClient, payload as TelemetryPayload),
      }),
    );

    clients.set(
      "detections",
      createRealtimeClient("detections", {
        onMessage: (payload) => handleDetections(queryClient, payload as DetectionsPayload),
      }),
    );

    for (const [, client] of clients) client.start();
    clientsRef.current = clients;

    return () => {
      for (const [, client] of clients) client.stop();
      clientsRef.current.clear();
    };
  }, [queryClient]);

  return children;
}

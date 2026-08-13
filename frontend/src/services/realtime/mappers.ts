/**
 * Mappers — translate raw WebSocket payloads into the frontend domain types
 * defined in `src/types/monitoring` so live updates share the same shape as
 * the REST responses. Any field the WebSocket does not carry is left undefined
 * so the cache merge (`setQueryData` updater) preserves the last REST value.
 */

import type {
  Alert,
  CameraState,
  CameraSource,
  ConnectionState,
  CrackClass,
  GpsFix,
  GsmStatus,
  RoverState,
  Snapshot,
  Statistics,
  TrackHealth,
} from "@/types/monitoring";

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

function mapSource(mode?: string): CameraSource {
  if (mode === "esp32cam" || mode === "esp32-cam") return "esp32-cam";
  if (mode === "demo" || mode === "demo-video") return "demo-video";
  return "usb";
}

function mapCrackClass(cls?: string | null): CrackClass | null {
  const name = (cls ?? "").toLowerCase();
  if (name.includes("small")) return "small_crack";
  if (name.includes("medium")) return "medium_crack";
  if (name.includes("large")) return "large_crack";
  if (name.includes("broken")) return "broken_chain";
  return null;
}

function parseResolution(resolution?: string): { width?: number; height?: number } {
  if (!resolution) return {};
  const match = resolution.match(/(\d+)\s*[x×]\s*(\d+)/);
  if (!match) return {};
  return { width: Number(match[1]), height: Number(match[2]) };
}

function connectionFrom(running: boolean | undefined, error?: string | null): ConnectionState {
  if (error) return "error";
  return running ? "connected" : "disconnected";
}

function nowIso(): string {
  return new Date().toISOString();
}

/**
 * Strips keys whose value is `undefined` and returns a clean `Partial<T>`.
 * Required because the project compiles with `exactOptionalPropertyTypes`,
 * which rejects explicit `undefined` on optional properties — and an omitted
 * key is exactly the "preserve last value" signal the cache merge relies on.
 */
function pickDefined<T extends object>(patch: Record<string, unknown>): Partial<T> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(patch)) {
    if (value !== undefined) out[key] = value;
  }
  return out as Partial<T>;
}

// ---------------------------------------------------------------------------
// Channel: camera-status
// Backend sends { timestamp, mode, running, fps, resolution, error }
// ---------------------------------------------------------------------------

export interface CameraStatusPayload {
  timestamp?: string;
  mode?: string;
  running?: boolean;
  fps?: number;
  camera_fps?: number;
  display_fps?: number;
  inference_fps?: number;
  resolution?: string;
  native_stream_url?: string;
  error?: string | null;
}

export function mapCameraStatus(payload: CameraStatusPayload): Partial<CameraState> {
  const { width, height } = parseResolution(payload.resolution);
  const running = Boolean(payload.running);
  return pickDefined<CameraState>({
    source: mapSource(payload.mode),
    state: connectionFrom(running, payload.error),
    fps: payload.fps,
    cameraFps: payload.camera_fps,
    displayFps: payload.display_fps,
    inferenceFps: payload.inference_fps,
    width,
    height,
    detectionActive: running,
    streamUrl: running ? "/api/camera/stream" : undefined,
    nativeStreamUrl: payload.native_stream_url,
  });
}

// ---------------------------------------------------------------------------
// Channel: telemetry
// Backend sends { timestamp, camera, alert, health, stats, rover, gps, gsm }
// ---------------------------------------------------------------------------

export interface TelemetryPayload {
  timestamp?: string;
  camera?: CameraStatusPayload;
  alert?: {
    detected?: boolean;
    severity?: string;
    class_name?: string | null;
    confidence?: number;
    message?: string;
  };
  health?: {
    score?: number;
    status?: string;
    note?: string;
  };
  stats?: {
    total?: number;
    small?: number;
    medium?: number;
    large?: number;
    broken?: number;
  };
  rover?: {
    online?: boolean;
    moving?: boolean;
  };
  gps?: {
    hasFix?: boolean;
    latitude?: number;
    longitude?: number;
  };
  gsm?: {
    online?: boolean;
    signalStrength?: number;
  };
}

export function mapTelemetryAlert(payload: TelemetryPayload): Partial<Alert> | undefined {
  const alert = payload.alert;
  if (!alert) return undefined;
  return {
    id: `alert-live-${payload.timestamp ?? nowIso()}`,
    severity: (alert.severity?.toUpperCase() ?? "SAFE") as Alert["severity"],
    crackClass: mapCrackClass(alert.class_name),
    confidence: alert.confidence ?? 0,
    message: alert.message ?? "Track is Safe",
    timestamp: payload.timestamp ?? nowIso(),
  };
}

export function mapTelemetryHealth(payload: TelemetryPayload): Partial<TrackHealth> {
  const health = payload.health;
  if (!health) return {};
  return pickDefined<TrackHealth>({
    overall: health.score,
    status: health.status?.toLowerCase(),
    updatedAt: payload.timestamp ?? nowIso(),
  });
}

export function mapTelemetryStatistics(payload: TelemetryPayload): Partial<Statistics> {
  const stats = payload.stats;
  if (!stats) return {};
  return pickDefined<Statistics>({
    totalDetections: stats.total,
    smallCrack: stats.small,
    mediumCrack: stats.medium,
    largeCrack: stats.large,
    brokenChain: stats.broken,
  });
}

export function mapTelemetryRover(payload: TelemetryPayload): Partial<RoverState> {
  const rover = payload.rover;
  if (!rover) return {};
  return pickDefined<RoverState>({
    state: rover.online ? "connected" : "disconnected",
    emergencyStopped: rover.online ? !rover.moving : undefined,
  });
}

export function mapTelemetryGps(payload: TelemetryPayload): Partial<GpsFix> {
  const gps = payload.gps;
  if (!gps) return {};
  return pickDefined<GpsFix>({
    latitude: gps.latitude,
    longitude: gps.longitude,
    hasFix: Boolean(gps.hasFix),
    updatedAt: payload.timestamp ?? nowIso(),
  });
}

export function mapTelemetryGsm(payload: TelemetryPayload): Partial<GsmStatus> {
  const gsm = payload.gsm;
  if (!gsm) return {};
  return pickDefined<GsmStatus>({
    state: gsm.online ? "connected" : "disconnected",
    signalStrength: gsm.signalStrength,
  });
}

export function mapTelemetryCamera(payload: TelemetryPayload): Partial<CameraState> | undefined {
  if (!payload.camera) return undefined;
  return mapCameraStatus(payload.camera);
}

// ---------------------------------------------------------------------------
// Channel: detections
// Backend sends { timestamp, alert, latestSnapshot }
// ---------------------------------------------------------------------------

export interface DetectionsPayload {
  timestamp?: string;
  alert?: {
    severity?: string;
    class_name?: string | null;
    confidence?: number;
    message?: string;
  };
  latestSnapshot?: Snapshot | null;
}

export function mapDetectionsAlert(payload: DetectionsPayload): Partial<Alert> | undefined {
  const alert = payload.alert;
  if (!alert) return undefined;
  return {
    id: `alert-det-${payload.timestamp ?? nowIso()}`,
    severity: (alert.severity?.toUpperCase() ?? "SAFE") as Alert["severity"],
    crackClass: mapCrackClass(alert.class_name),
    confidence: alert.confidence ?? 0,
    message: alert.message ?? "Track is Safe",
    timestamp: payload.timestamp ?? nowIso(),
  };
}

export function mapDetectionsSnapshot(payload: DetectionsPayload): Partial<Snapshot> | undefined {
  if (!payload.latestSnapshot) return undefined;
  return payload.latestSnapshot;
}

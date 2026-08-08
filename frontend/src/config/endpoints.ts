/**
 * Endpoint map mirroring the FastAPI backend.
 * Declared now so the REST/WebSocket client can be dropped in without touching UI code.
 */
export const API_BASE_URL =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ?? "http://localhost:8080";

/** Base URL of the WebSocket server. The WS client appends `/ws/${channel}`. */
export const WS_BASE_URL =
  (import.meta.env["VITE_WS_BASE_URL"] as string | undefined) ?? "ws://localhost:8080";

export const API_ENDPOINTS = {
  systemStatus: "/api/system/status",
  cameraState: "/api/camera/state",
  cameraConnect: "/api/camera/connect",
  cameraDisconnect: "/api/camera/disconnect",
  latestAlert: "/api/alerts/latest",
  trackHealth: "/api/track-health",
  gps: "/api/gps",
  gsmStatus: "/api/gsm/status",
  sendSms: "/api/gsm/send-sms",
  statistics: "/api/statistics",
  detectionDistribution: "/api/statistics/distribution",
  severityTrend: "/api/statistics/trend",
  detections: "/api/detections",
  latestSnapshot: "/api/detections/latest-snapshot",
  roverState: "/api/rover/state",
  roverCommand: "/api/rover/command",
  uploadVideo: "/api/uploads/video",
  reportGenerate: "/api/reports/generate",
} as const;

export const WS_CHANNELS = {
  telemetry: "/ws/telemetry",
  detections: "/ws/detections",
  videoFeed: "/ws/video",
} as const;

/**
 * Resolves a possibly-relative backend URL (e.g. the relative `/api/...` path
 * returned by the snapshot endpoint) to an absolute URL on the API host, which
 * may differ from the origin the frontend is served from. Absolute URLs pass
 * through unchanged.
 */
export function resolveApiUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (/^https?:\/\//i.test(path)) return path;
  return `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}

/** Static application configuration (no secrets, no backend logic). */
export const APP_CONFIG = {
  name: "Railway Crack Detection & Monitoring System",
  shortName: "RailGuard Monitor",

  version: "1.0.0",
  developer: "Railway Systems Engineering Team",
} as const;

/** Refresh cadence in ms for the polling data layer (later: WebSocket push). */
export const POLLING_INTERVALS = {
  systemStatus: 5000,
  camera: 2000,
  alert: 3000,
  health: 10000,
  gps: 4000,
  gsm: 10000,
  statistics: 8000,
  detections: 8000,
  snapshot: 15000,
  rover: 4000,
} as const;

/** Toggles for swapping the data source once the backend is available. */
export const FEATURE_FLAGS = {
  useMockData: false,
} as const;

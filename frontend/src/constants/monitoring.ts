import type {
  CameraSource,
  CrackClass,
  ConnectionState,
  DeviceId,
  HealthStatus,
  Severity,
} from "@/types/monitoring";

export const SEVERITY_ORDER: Severity[] = ["SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL"];

export const SEVERITY_LABELS: Record<Severity, string> = {
  SAFE: "Safe",
  LOW: "Low",
  MEDIUM: "Medium",
  HIGH: "High",
  CRITICAL: "Critical",
};

/** Semantic token names used for severity coloring (no raw hex in components). */
export const SEVERITY_TOKEN: Record<Severity, "success" | "primary" | "warning" | "danger"> = {
  SAFE: "success",
  LOW: "primary",
  MEDIUM: "warning",
  HIGH: "warning",
  CRITICAL: "danger",
};

export const CRACK_CLASSES: CrackClass[] = [
  "small_crack",
  "medium_crack",
  "large_crack",
  "broken_chain",
];

export const CRACK_CLASS_LABELS: Record<CrackClass, string> = {
  small_crack: "Small Crack",
  medium_crack: "Medium Crack",
  large_crack: "Large Crack",
  broken_chain: "Broken Chain",
};

export const CONNECTION_LABELS: Record<ConnectionState, string> = {
  connected: "Connected",
  connecting: "Connecting",
  disconnected: "Disconnected",
  error: "Error",
};

export const DEVICE_LABELS: Record<DeviceId, string> = {
  camera: "Camera",
  esp32: "ESP32",
  gps: "GPS",
  gsm: "GSM",
};

export const CAMERA_SOURCE_LABELS: Record<CameraSource, string> = {
  usb: "USB Camera",
  "esp32-cam": "ESP32-CAM",
  "demo-video": "Demo Video",
};

export const HEALTH_STATUS_LABELS: Record<HealthStatus, string> = {
  excellent: "Excellent",
  good: "Good",
  warning: "Warning",
  critical: "Critical",
};

export const HEALTH_THRESHOLDS = {
  excellent: 90,
  good: 75,
  warning: 50,
} as const;

export const HISTORY_PAGE_SIZE = 8;

/** Pie slice colors for the detection distribution chart. */
export const DISTRIBUTION_SLICE_COLORS = [
  "var(--color-chart-2)",
  "var(--color-chart-3)",
  "var(--color-chart-1)",
  "var(--color-chart-4)",
] as const;

/** Stacked area series for the severity trend chart. */
export const SEVERITY_TREND_SERIES = [
  { key: "low", label: "Low", color: "var(--color-chart-1)" },
  { key: "medium", label: "Medium", color: "var(--color-chart-3)" },
  { key: "high", label: "High", color: "var(--color-chart-5)" },
  { key: "critical", label: "Critical", color: "var(--color-chart-4)" },
] as const;

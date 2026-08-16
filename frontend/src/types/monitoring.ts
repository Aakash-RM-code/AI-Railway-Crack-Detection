/**
 * Domain types for the Railway Crack Detection & Rover Monitoring System.
 * These mirror the payloads the FastAPI backend will return.
 */

export type Severity = "SAFE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type CrackClass = "small_crack" | "medium_crack" | "large_crack" | "broken_chain";

export type ConnectionState = "connected" | "connecting" | "disconnected" | "error";

export type DeviceId = "camera" | "esp32" | "gps" | "gsm";

export type CameraSource = "esp32-cam";

export type RoverCommand =
  "forward" | "backward" | "left" | "right" | "stop" | "emergency_stop" | "set_speed";

export type HealthStatus = "excellent" | "good" | "warning" | "critical";

export interface DeviceStatus {
  id: DeviceId;
  label: string;
  state: ConnectionState;
  detail?: string;
}

export interface SystemStatus {
  online: boolean;
  uptimeSeconds: number;
  version: string;
  devices: DeviceStatus[];
}

export interface CameraState {
  source: CameraSource;
  state: ConnectionState;
  fps: number;
  width: number;
  height: number;
  detectionActive: boolean;
  streamUrl: string | null;
  /** Actual ESP32-CAM acquisition rate, measured by the backend. */
  cameraFps?: number;
  /** Frames rendered by the display path (browser native stream or backend proxy). */
  displayFps?: number;
  /** OpenVINO inference worker rate, measured by the backend. */
  inferenceFps?: number;
  /** ESP32-CAM native MJPEG URL for direct browser rendering (ESP32-CAM source). */
  nativeStreamUrl?: string | null;
}

/**
 * One detection box in source-frame pixel coordinates ([x1, y1, x2, y2]).
 * Delivered over the /ws/detections channel; drawn by the browser overlay.
 */
export interface DetectionBox {
  class_name: string;
  confidence: number;
  severity: Severity;
  bbox: [number, number, number, number];
}

/** Raw /ws/detections payload (backend sends snake_case fields here). */
export interface DetectionsMessage {
  timestamp?: string;
  alert?: Alert | null;
  detections?: DetectionBox[];
  latestSnapshot?: Snapshot | null;
}

export interface Alert {
  id: string;
  severity: Severity;
  crackClass: CrackClass | null;
  confidence: number; // 0..1
  message: string;
  timestamp: string; // ISO 8601
}

export interface TrackHealth {
  overall: number; // 0..100
  status: HealthStatus;
  inspectedMeters: number;
  updatedAt: string;
}

export interface GpsFix {
  latitude: number;
  longitude: number;
  satellites: number;
  hasFix: boolean;
  updatedAt: string;
}

export interface GsmStatus {
  state: ConnectionState;
  signalStrength: number; // 0..100
  operator: string | null;
  lastMessageAt: string | null;
}

export interface Statistics {
  totalDetections: number;
  smallCrack: number;
  mediumCrack: number;
  largeCrack: number;
  brokenChain: number;
  criticalAlerts: number;
}

export interface SeverityTrendPoint {
  timestamp: string;
  low: number;
  medium: number;
  high: number;
  critical: number;
}

export interface DetectionDistributionSlice {
  crackClass: CrackClass;
  count: number;
}

export interface Detection {
  id: string;
  timestamp: string;
  crackClass: CrackClass;
  confidence: number; // 0..1
  severity: Severity;
  latitude: number;
  longitude: number;
  status: "new" | "reviewed" | "resolved";
}

export interface Snapshot {
  id: string;
  imageUrl: string | null;
  timestamp: string;
  severity: Severity;
  crackClass: CrackClass | null;
}

export interface RoverState {
  state: ConnectionState;
  speed: number; // 0..255 (ESP32 firmware scale)
  lastCommand: RoverCommand | null;
  emergencyStopped: boolean;
}

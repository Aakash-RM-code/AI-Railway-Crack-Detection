import { CRACK_CLASSES, DEVICE_LABELS, HISTORY_PAGE_SIZE } from "@/constants/monitoring";
import { APP_CONFIG } from "@/config/app";
import type {
  CameraConnectRequest,
  CommandResult,
  DetectionQuery,
  MonitoringApi,
  Paginated,
  RoverCommandRequest,
  SendSmsRequest,
} from "@/services/api";
import {
  healthStatusFromScore,
  isoMinutesAgo,
  pickOne,
  randomBetween,
  randomInt,
  severityFromClass,
} from "@/services/mock/generators";
import type {
  Alert,
  CameraState,
  ConnectionState,
  Detection,
  DetectionDistributionSlice,
  DeviceId,
  GpsFix,
  GsmStatus,
  RoverState,
  SeverityTrendPoint,
  Snapshot,
  Statistics,
  SystemStatus,
  TrackHealth,
} from "@/types/monitoring";

const BASE_LAT = 19.076;
const BASE_LON = 72.8777;

const delay = <T>(value: T, ms = 120): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms));

/** Mutable in-memory state so UI actions feel real without a backend. */
const state = {
  camera: {
    source: "usb",
    state: "disconnected",
    fps: 0,
    width: 1280,
    height: 720,
    detectionActive: false,
    streamUrl: null,
  } as CameraState,
  rover: {
    state: "connected",
    speed: 150,
    lastCommand: null,
    emergencyStopped: false,
  } as RoverState,
};

const detections: Detection[] = Array.from({ length: 42 }, (_, index) => {
  const crackClass = pickOne(CRACK_CLASSES);
  const confidence = randomBetween(0.55, 0.99);
  return {
    id: `det-${index + 1}`,
    timestamp: isoMinutesAgo(index * 7 + randomInt(0, 5)),
    crackClass,
    confidence,
    severity: severityFromClass(crackClass, confidence),
    latitude: BASE_LAT + randomBetween(-0.05, 0.05),
    longitude: BASE_LON + randomBetween(-0.05, 0.05),
    status: pickOne(["new", "reviewed", "resolved"] as const),
  };
});

const deviceStatus = (id: DeviceId, fallback: ConnectionState) => ({
  id,
  label: DEVICE_LABELS[id],
  state: fallback,
});

export const mockApi: MonitoringApi = {
  getSystemStatus: () =>
    delay<SystemStatus>({
      online: true,
      uptimeSeconds: randomInt(3600, 86_400),
      version: APP_CONFIG.version,
      devices: [
        { ...deviceStatus("camera", state.camera.state) },
        { ...deviceStatus("esp32", state.rover.state) },
        { ...deviceStatus("gps", "connected") },
        { ...deviceStatus("gsm", "connected") },
      ],
    }),

  getCameraState: () =>
    delay<CameraState>({
      ...state.camera,
      fps: state.camera.state === "connected" ? randomInt(22, 30) : 0,
    }),

  connectCamera: ({ source }: CameraConnectRequest) => {
    state.camera = {
      ...state.camera,
      source,
      state: "connected",
      detectionActive: true,
      fps: randomInt(22, 30),
      streamUrl: null,
    };
    return delay(state.camera, 400);
  },

  disconnectCamera: () => {
    state.camera = { ...state.camera, state: "disconnected", detectionActive: false, fps: 0 };
    return delay(state.camera, 250);
  },

  getLatestAlert: () => {
    const latest = detections[0]!;
    return delay<Alert>({
      id: `alert-${latest.id}`,
      severity: latest.severity,
      crackClass: latest.crackClass,
      confidence: latest.confidence,
      message:
        latest.severity === "CRITICAL"
          ? "Critical rail defect detected. Immediate inspection required."
          : "Rail anomaly detected and logged for review.",
      timestamp: latest.timestamp,
    });
  },

  getTrackHealth: () => {
    const overall = randomBetween(58, 96);
    return delay<TrackHealth>({
      overall,
      status: healthStatusFromScore(overall),
      inspectedMeters: randomInt(1200, 8600),
      updatedAt: new Date().toISOString(),
    });
  },

  getGps: () =>
    delay<GpsFix>({
      latitude: BASE_LAT + randomBetween(-0.01, 0.01),
      longitude: BASE_LON + randomBetween(-0.01, 0.01),
      satellites: randomInt(6, 14),
      hasFix: true,
      updatedAt: new Date().toISOString(),
    }),

  getGsmStatus: () =>
    delay<GsmStatus>({
      state: "connected",
      signalStrength: randomInt(55, 98),
      operator: "Airtel",
      lastMessageAt: isoMinutesAgo(randomInt(2, 90)),
    }),

  sendSms: ({ phoneNumber }: SendSmsRequest) =>
    delay<CommandResult>({ ok: true, message: `Message queued for ${phoneNumber}` }, 500),

  getStatistics: () => {
    const counts = CRACK_CLASSES.map(
      (crackClass) => detections.filter((d) => d.crackClass === crackClass).length,
    );
    return delay<Statistics>({
      totalDetections: detections.length,
      smallCrack: counts[0] ?? 0,
      mediumCrack: counts[1] ?? 0,
      largeCrack: counts[2] ?? 0,
      brokenChain: counts[3] ?? 0,
      criticalAlerts: detections.filter((d) => d.severity === "CRITICAL").length,
    });
  },

  getDetectionDistribution: () =>
    delay<DetectionDistributionSlice[]>(
      CRACK_CLASSES.map((crackClass) => ({
        crackClass,
        count: detections.filter((d) => d.crackClass === crackClass).length,
      })),
    ),

  getSeverityTrend: () =>
    delay<SeverityTrendPoint[]>(
      Array.from({ length: 12 }, (_, index) => ({
        timestamp: isoMinutesAgo((11 - index) * 30),
        low: randomInt(0, 6),
        medium: randomInt(0, 5),
        high: randomInt(0, 4),
        critical: randomInt(0, 2),
      })),
    ),

  getDetections: (query: DetectionQuery = {}) => {
    const { search = "", severity = "ALL", page = 1, pageSize = HISTORY_PAGE_SIZE } = query;
    const term = search.trim().toLowerCase();
    const filtered = detections.filter((d) => {
      const matchesSeverity = severity === "ALL" || d.severity === severity;
      const matchesTerm =
        !term ||
        d.crackClass.includes(term) ||
        d.severity.toLowerCase().includes(term) ||
        d.status.includes(term);
      return matchesSeverity && matchesTerm;
    });
    const start = (page - 1) * pageSize;
    return delay<Paginated<Detection>>({
      items: filtered.slice(start, start + pageSize),
      total: filtered.length,
      page,
      pageSize,
    });
  },

  getLatestSnapshot: () => {
    const latest = detections[0]!;
    return delay<Snapshot>({
      id: `snap-${latest.id}`,
      imageUrl: null,
      timestamp: latest.timestamp,
      severity: latest.severity,
      crackClass: latest.crackClass,
    });
  },

  getRoverState: () => delay<RoverState>({ ...state.rover }),

  sendRoverCommand: ({ command, speed }: RoverCommandRequest) => {
    state.rover = {
      ...state.rover,
      lastCommand: command,
      emergencyStopped: command === "emergency_stop",
      // set_speed only changes speed; any movement command keeps current speed.
      speed:
        command === "emergency_stop"
          ? 0
          : command === "set_speed"
            ? (speed ?? state.rover.speed)
            : state.rover.speed,
    };
    return delay({ ...state.rover }, 150);
  },

  uploadDemoVideo: () => {
    state.camera = {
      ...state.camera,
      source: "demo-video",
      state: "connected",
      detectionActive: true,
      fps: randomInt(22, 30),
      streamUrl: null,
    };
    return delay(state.camera, 800);
  },

  generateInspectionReport: () =>
    delay({ path: "/reports/mock_report.pdf", url: "/api/reports/download/mock_report.pdf" }, 1000),
};

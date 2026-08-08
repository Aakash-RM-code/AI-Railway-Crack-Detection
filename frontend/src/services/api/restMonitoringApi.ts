/**
 * REST implementation of MonitoringApi.
 * Talks to the FastAPI backend using fetch with timeout, retry, and error handling.
 * No component changes required — this satisfies the same interface as mockApi.
 */

import { API_BASE_URL, API_ENDPOINTS } from "@/config/endpoints";
import type {
  CameraConnectRequest,
  CommandResult,
  DetectionQuery,
  MonitoringApi,
  Paginated,
  ReportResponse,
  RoverCommandRequest,
  SendSmsRequest,
} from "@/services/api";
import type {
  Alert,
  CameraState,
  Detection,
  DetectionDistributionSlice,
  GpsFix,
  GsmStatus,
  RoverState,
  SeverityTrendPoint,
  Snapshot,
  Statistics,
  SystemStatus,
  TrackHealth,
} from "@/types/monitoring";

// ──────────────────────────────────────────────
// HTTP client helpers
// ──────────────────────────────────────────────

const DEFAULT_TIMEOUT_MS = 8_000;
const MAX_RETRIES = 2;

async function httpGet<T>(
  path: string,
  params?: Record<string, string | number | undefined>,
): Promise<T> {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined) url.searchParams.set(k, String(v));
    }
  }

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
    try {
      const res = await fetch(url.toString(), { signal: controller.signal });
      clearTimeout(timer);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText} — ${path}`);
      return (await res.json()) as T;
    } catch (err) {
      clearTimeout(timer);
      if (attempt === MAX_RETRIES) throw err;
      await new Promise((r) => setTimeout(r, 300 * (attempt + 1)));
    }
  }
  throw new Error("Unreachable");
}

async function httpPost<T>(path: string, body?: unknown): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // exactOptionalPropertyTypes: body must be BodyInit | null, not undefined
      body: body !== undefined ? JSON.stringify(body) : null,
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText} — ${path}`);
    return (await res.json()) as T;
  } catch (err) {
    clearTimeout(timer);
    throw err;
  }
}

async function httpPostFormData<T>(path: string, formData: FormData): Promise<T> {
  const controller = new AbortController();
  // Larger timeout for file uploads
  const timer = setTimeout(() => controller.abort(), 60_000);
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText} — ${path}`);
    return (await res.json()) as T;
  } catch (err) {
    clearTimeout(timer);
    throw err;
  }
}

// ──────────────────────────────────────────────
// MonitoringApi — REST implementation
// ──────────────────────────────────────────────

export const restMonitoringApi: MonitoringApi = {
  getSystemStatus: () => httpGet<SystemStatus>(API_ENDPOINTS.systemStatus),

  getCameraState: () => httpGet<CameraState>(API_ENDPOINTS.cameraState),

  connectCamera: (req: CameraConnectRequest) =>
    // `CameraSource` ("usb" | "esp32-cam" | "demo-video") is sent verbatim —
    // the backend owns the enum→mode mapping and validates the contract.
    httpPost<CameraState>(API_ENDPOINTS.cameraConnect, {
      source: req.source,
      videoPath: req.videoPath,
    }),

  disconnectCamera: () => httpPost<CameraState>(API_ENDPOINTS.cameraDisconnect),

  getLatestAlert: () => httpGet<Alert>(API_ENDPOINTS.latestAlert),

  getTrackHealth: () => httpGet<TrackHealth>(API_ENDPOINTS.trackHealth),

  getGps: () => httpGet<GpsFix>(API_ENDPOINTS.gps),

  getGsmStatus: () => httpGet<GsmStatus>(API_ENDPOINTS.gsmStatus),

  sendSms: (req: SendSmsRequest) => httpPost<CommandResult>(API_ENDPOINTS.sendSms, req),

  getStatistics: () => httpGet<Statistics>(API_ENDPOINTS.statistics),

  getDetectionDistribution: () =>
    httpGet<DetectionDistributionSlice[]>(API_ENDPOINTS.detectionDistribution),

  getSeverityTrend: () => httpGet<SeverityTrendPoint[]>(API_ENDPOINTS.severityTrend),

  getDetections: (query: DetectionQuery = {}): Promise<Paginated<Detection>> =>
    httpGet<Paginated<Detection>>(API_ENDPOINTS.detections, {
      search: query.search,
      severity: query.severity,
      page: query.page,
      pageSize: query.pageSize,
    }),

  getLatestSnapshot: () => httpGet<Snapshot>(API_ENDPOINTS.latestSnapshot),

  getRoverState: () => httpGet<RoverState>(API_ENDPOINTS.roverState),

  sendRoverCommand: (req: RoverCommandRequest) =>
    httpPost<RoverState>(API_ENDPOINTS.roverCommand, req),

  uploadDemoVideo: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return httpPostFormData<CameraState>(API_ENDPOINTS.uploadVideo, formData);
  },

  generateInspectionReport: () => httpPost<ReportResponse>(API_ENDPOINTS.reportGenerate),
};

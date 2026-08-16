import type {
  Alert,
  CameraSource,
  CameraState,
  Detection,
  DetectionDistributionSlice,
  GpsFix,
  GsmStatus,
  RoverCommand,
  RoverState,
  Severity,
  SeverityTrendPoint,
  Snapshot,
  Statistics,
  SystemStatus,
  TrackHealth,
} from "@/types/monitoring";

/** Query/mutation payloads mirroring the future FastAPI request bodies. */
export interface DetectionQuery {
  search?: string;
  severity?: Severity | "ALL";
  page?: number;
  pageSize?: number;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface SendSmsRequest {
  phoneNumber: string;
  message: string;
}

export interface CommandResult {
  ok: boolean;
  message: string;
}

export interface RoverCommandRequest {
  command: RoverCommand;
  speed?: number;
}

export interface CameraConnectRequest {
  source: CameraSource;
}

export interface ReportResponse {
  path: string;
  url: string;
}

/**
 * The single contract the UI depends on.
 * Mock and REST/WebSocket implementations both satisfy this interface.
 */
export interface MonitoringApi {
  getSystemStatus(): Promise<SystemStatus>;
  getCameraState(): Promise<CameraState>;
  connectCamera(request: CameraConnectRequest): Promise<CameraState>;
  disconnectCamera(): Promise<CameraState>;
  getLatestAlert(): Promise<Alert>;
  getTrackHealth(): Promise<TrackHealth>;
  getGps(): Promise<GpsFix>;
  getGsmStatus(): Promise<GsmStatus>;
  sendSms(request: SendSmsRequest): Promise<CommandResult>;
  getStatistics(): Promise<Statistics>;
  getDetectionDistribution(): Promise<DetectionDistributionSlice[]>;
  getSeverityTrend(): Promise<SeverityTrendPoint[]>;
  getDetections(query?: DetectionQuery): Promise<Paginated<Detection>>;
  getLatestSnapshot(): Promise<Snapshot>;
  getRoverState(): Promise<RoverState>;
  sendRoverCommand(request: RoverCommandRequest): Promise<RoverState>;
  generateInspectionReport(): Promise<ReportResponse>;
}

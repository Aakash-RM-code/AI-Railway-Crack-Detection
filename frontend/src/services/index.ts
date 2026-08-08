import { FEATURE_FLAGS } from "@/config/app";
import type { MonitoringApi } from "@/services/api";
import { mockApi } from "@/services/mock/mockApi";
import { restMonitoringApi } from "@/services/api/restMonitoringApi";

/**
 * Single seam for all UI data access.
 * FEATURE_FLAGS.useMockData=true  → in-memory mock (no backend required).
 * FEATURE_FLAGS.useMockData=false → real FastAPI REST backend.
 */
export const monitoringApi: MonitoringApi = FEATURE_FLAGS.useMockData ? mockApi : restMonitoringApi;

export type { MonitoringApi };
export * from "./api";

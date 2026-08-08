/**
 * WebSocket realtime layer — shared types.
 */

/** The live channels the backend exposes under /ws. */
export type RealtimeChannel = "telemetry" | "detections" | "camera-status";

/**
 * Connectivity lifecycle for a single channel:
 * - "offline":    no socket, or the socket closed/errored. Polling resumes.
 * - "connecting": socket is open but no valid message received yet. Polling
 *                 stays active (fail-safe until first valid payload).
 * - "live":       at least one valid message received. Polling is suspended.
 */
export type RealtimeStatus = "offline" | "connecting" | "live";

/**
 * RealtimeWebSocket — single-channel WebSocket client.
 *
 * Responsibilities:
 * - connect to one backend /ws channel
 * - send periodic "ping" heartbeats
 * - report connection status to the status store
 * - exponential reconnect backoff (1s → 2s → 4s → 8s → 16s → 30s max)
 * - mark the channel "live" only after the first valid message arrives
 *
 * The client is framework-agnostic; React wiring lives in RealtimeProvider.
 */

import { WS_BASE_URL } from "@/config/endpoints";

import { setChannelStatus } from "./statusStore";
import type { RealtimeChannel } from "./types";

const HEARTBEAT_MS = 25_000;
const BASE_RECONNECT_MS = 1_000;
const MAX_RECONNECT_MS = 30_000;
const MAX_BACKOFF_EXPONENT = 30; // 2^30 s is absurdly large; cap by constant instead

interface RealtimeClientOptions {
  /** Called with every parsed JSON message. Only fires after channel is live. */
  onMessage: (payload: unknown) => void;
}

export interface RealtimeClient {
  start: () => void;
  stop: () => void;
  /** Current socket ready state, for tests/inspection. */
  readonly readyState: () => WebSocket["readyState"] | null;
}

export function createRealtimeClient(
  channel: RealtimeChannel,
  { onMessage }: RealtimeClientOptions,
): RealtimeClient {
  let socket: WebSocket | null = null;
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let reconnectAttempt = 0;
  let stopped = true;

  function backoffDelay(): number {
    const exp = Math.min(reconnectAttempt, Math.log2(MAX_RECONNECT_MS / BASE_RECONNECT_MS));
    return Math.min(BASE_RECONNECT_MS * 2 ** exp, MAX_RECONNECT_MS);
  }

  function clearHeartbeat() {
    if (heartbeatTimer !== null) {
      clearInterval(heartbeatTimer);
      heartbeatTimer = null;
    }
  }

  function startHeartbeat() {
    clearHeartbeat();
    heartbeatTimer = setInterval(() => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send("ping");
      }
    }, HEARTBEAT_MS);
  }

  function scheduleReconnect() {
    if (stopped) return;
    const delay = backoffDelay();
    if (reconnectTimer !== null) clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(connect, delay);
  }

  function connect() {
    if (stopped) return;
    setChannelStatus(channel, "connecting");

    socket = new WebSocket(`${WS_BASE_URL}/ws/${channel}`);

    socket.onopen = () => {
      reconnectAttempt = 0;
      startHeartbeat();
    };

    socket.onmessage = (event: MessageEvent<string>) => {
      let payload: unknown;
      try {
        payload = JSON.parse(event.data);
      } catch {
        return; // ignore malformed frames, keep channel "connecting"
      }
      setChannelStatus(channel, "live");
      onMessage(payload);
    };

    socket.onclose = () => {
      clearHeartbeat();
      socket = null;
      setChannelStatus(channel, "offline");
      reconnectAttempt += 1;
      scheduleReconnect();
    };

    socket.onerror = () => {
      // close() triggers onclose → reconnect path
      socket?.close();
    };
  }

  function stop() {
    stopped = true;
    clearHeartbeat();
    if (reconnectTimer !== null) clearTimeout(reconnectTimer);
    reconnectTimer = null;
    if (socket) {
      socket.onclose = null;
      socket.onerror = null;
      socket.close();
      socket = null;
    }
    setChannelStatus(channel, "offline");
  }

  return {
    start() {
      if (!stopped) return;
      stopped = false;
      connect();
    },
    stop,
    readyState() {
      return socket ? socket.readyState : null;
    },
  };
}

// Re-exported for completeness; clients construct URLs with the existing config.
export { MAX_RECONNECT_MS as RECONNECT_MAX_MS };

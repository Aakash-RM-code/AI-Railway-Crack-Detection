import { useQuery, type UseQueryOptions } from "@tanstack/react-query";

import { useIsRealtimeLive } from "@/services/realtime";

/**
 * Polling wrapper around the service layer, with optional realtime failover.
 *
 * - `staleTime` is capped below the interval so fresh data isn't skipped.
 * - a single retry keeps polling from hammering a down backend.
 * - when `realtimeChannel` is provided, polling stays ACTIVE until the channel
 *   goes "live" (first valid WebSocket message). Once live, polling for that
 *   query is paused and the WebSocket pushes take over. If the channel drops
 *   out of "live" (disconnect/unhealthy), polling resumes automatically.
 */
export function useLiveQuery<T>(
  key: readonly unknown[],
  fetcher: () => Promise<T>,
  intervalMs: number,
  options?: Omit<UseQueryOptions<T, Error, T, readonly unknown[]>, "queryKey" | "queryFn">,
  realtimeChannel?: Parameters<typeof useIsRealtimeLive>[0],
) {
  const realtimeLive = useIsRealtimeLive(realtimeChannel);

  return useQuery<T, Error, T, readonly unknown[]>({
    queryKey: key,
    queryFn: fetcher,
    refetchInterval: realtimeLive ? false : intervalMs,
    staleTime: intervalMs / 2,
    retry: 1,
    ...options,
  });
}

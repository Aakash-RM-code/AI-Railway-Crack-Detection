/**
 * Local error-reporting shim (replaces the original Lovable telemetry module).
 *
 * No data leaves the browser: in development the error is logged to the
 * console; in production it is intentionally a no-op so a third-party error
 * reporting service can be wired in later.
 */

export function reportLovableError(error: Error, context: Record<string, unknown> = {}): void {
  if (import.meta.env.DEV) {
    console.error("[error-report]", context, error);
  }
}

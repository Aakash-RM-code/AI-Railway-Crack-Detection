/**
 * Lightweight SSR error capture.
 *
 * TanStack Start's h3 layer swallows in-handler throws into a plain 500 JSON
 * response, so try/catch alone can't surface them. This module keeps a reference
 * to the last error that passed through console.error so the server entry can
 * attribute the swallowed response to the real cause.
 */

let lastError: Error | null = null;

export function reportError(error: unknown): void {
  lastError = error instanceof Error ? error : new Error(String(error));
}

export function consumeLastCapturedError(): Error | null {
  const error = lastError;
  lastError = null;
  return error;
}

const originalConsoleError = console.error;

console.error = ((...args: unknown[]) => {
  originalConsoleError(...args);
  const error = args.find((arg): arg is Error => arg instanceof Error);
  if (error) {
    reportError(error);
  }
}) as typeof console.error;

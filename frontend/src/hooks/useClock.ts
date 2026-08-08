import { useEffect, useState } from "react";

/** Ticking clock for the header date/time display. */
export function useClock(intervalMs = 1000) {
  const [now, setNow] = useState<Date | null>(null);

  useEffect(() => {
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  return now;
}

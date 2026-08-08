import { HEALTH_THRESHOLDS } from "@/constants/monitoring";
import type { CrackClass, HealthStatus, Severity } from "@/types/monitoring";

export const randomBetween = (min: number, max: number) => min + Math.random() * (max - min);

export const randomInt = (min: number, max: number) => Math.floor(randomBetween(min, max + 1));

export const pickOne = <T>(items: readonly T[]): T => items[randomInt(0, items.length - 1)] as T;

export const isoMinutesAgo = (minutes: number) =>
  new Date(Date.now() - minutes * 60_000).toISOString();

export const severityFromClass = (crackClass: CrackClass, confidence: number): Severity => {
  if (crackClass === "broken_chain") return "CRITICAL";
  if (crackClass === "large_crack") return confidence > 0.8 ? "CRITICAL" : "HIGH";
  if (crackClass === "medium_crack") return "MEDIUM";
  return confidence > 0.6 ? "LOW" : "SAFE";
};

export const healthStatusFromScore = (score: number): HealthStatus => {
  if (score >= HEALTH_THRESHOLDS.excellent) return "excellent";
  if (score >= HEALTH_THRESHOLDS.good) return "good";
  if (score >= HEALTH_THRESHOLDS.warning) return "warning";
  return "critical";
};

/**
 * DetectionOverlay — draws live detection boxes onto a canvas aligned with the
 * video element below it.
 *
 * Boxes arrive over /ws/detections in source-frame pixel coordinates and are
 * mapped onto the rendered video rect, respecting the object-contain fit of the
 * <img> so boxes track the video even with letterboxing.
 */

import { useEffect, useRef } from "react";

import type { DetectionBox } from "@/types/monitoring";

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "#dc2626",
  HIGH: "#f97316",
  MEDIUM: "#eab308",
  LOW: "#3b82f6",
  SAFE: "#22c55e",
  UNKNOWN: "#6b7280",
};

const FALLBACK_COLOR = "#6b7280";

interface DetectionOverlayProps {
  boxes: DetectionBox[];
  videoRef: React.RefObject<HTMLImageElement | null>;
}

export function DetectionOverlay({ boxes, videoRef }: DetectionOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const img = videoRef.current;
    if (!canvas || !img) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const cw = canvas.clientWidth;
    const ch = canvas.clientHeight;
    if (cw === 0 || ch === 0) return;

    canvas.width = Math.max(1, Math.round(cw * dpr));
    canvas.height = Math.max(1, Math.round(ch * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cw, ch);

    if (boxes.length === 0) return;

    const nw = img.naturalWidth || 1;
    const nh = img.naturalHeight || 1;
    const scale = Math.min(cw / nw, ch / nh);
    const dw = nw * scale;
    const dh = nh * scale;
    const dx = (cw - dw) / 2;
    const dy = (ch - dh) / 2;

    for (const box of boxes) {
      const [x1, y1, x2, y2] = box.bbox;
      const px = dx + x1 * scale;
      const py = dy + y1 * scale;
      const pw = (x2 - x1) * scale;
      const ph = (y2 - y1) * scale;
      const color = SEVERITY_COLORS[box.severity] ?? FALLBACK_COLOR;

      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.strokeRect(px, py, pw, ph);

      const label = `${box.class_name} ${Math.round(box.confidence * 100)}%`;
      ctx.font = "11px system-ui, sans-serif";
      const tw = ctx.measureText(label).width;
      const labelY = py - 16 < 0 ? py + 2 : py - 16;
      ctx.fillStyle = color;
      ctx.fillRect(px - 1, labelY - 13, tw + 6, 15);
      ctx.fillStyle = "#ffffff";
      ctx.fillText(label, px + 2, labelY);
    }
  }, [boxes, videoRef]);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 h-full w-full"
      aria-hidden="true"
    />
  );
}

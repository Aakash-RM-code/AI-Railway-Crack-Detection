import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { o as require_jsx_runtime, r as Slot } from "../_libs/@radix-ui/react-collection+[...].mjs";
import { i as useQueryClient, n as useQuery, t as useMutation } from "../_libs/tanstack__react-query.mjs";
import { n as toast } from "../_libs/sonner.mjs";
import { a as resolveApiUrl, c as POLLING_INTERVALS, i as API_ENDPOINTS, n as useIsRealtimeLive, o as APP_CONFIG, r as API_BASE_URL, s as FEATURE_FLAGS } from "./router-z3rEwVU0.mjs";
import { C as ChevronDown, D as ArrowUp, E as CameraOff, O as ArrowDown, S as ChevronUp, T as Camera, _ as LoaderCircle, a as TrendingUp, b as Clock, c as SignalHigh, d as Satellite, f as OctagonX, g as MapPin, h as MessageSquare, i as TriangleAlert, k as Activity, l as ShieldCheck, m as Minus, n as WifiOff, o as TrainFront, p as OctagonAlert, r as Unlink, s as Square, t as X, u as Search, v as Layers, w as Check, x as CircleAlert, y as ImageOff } from "../_libs/lucide-react.mjs";
import { n as clsx, t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
import { a as Area, c as Cell, d as Legend, i as XAxis, l as ResponsiveContainer, n as PieChart, o as CartesianGrid, r as YAxis, s as Pie, t as AreaChart, u as Tooltip } from "../_libs/recharts+[...].mjs";
import { n as Root, t as Indicator } from "../_libs/radix-ui__react-progress.mjs";
import { a as SelectItemIndicator, c as SelectScrollDownButton$1, d as SelectValue$1, f as SelectViewport, i as SelectItem$1, l as SelectScrollUpButton$1, n as SelectContent$1, o as SelectItemText, r as SelectIcon, s as SelectPortal, t as Select$1, u as SelectTrigger$1 } from "../_libs/@radix-ui/react-select+[...].mjs";
import { i as SliderTrack, n as SliderRange, r as SliderThumb, t as Slider$1 } from "../_libs/radix-ui__react-slider.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-NmuHb8NK.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
function LabeledValue({ label, value, hint, className }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: cn("min-w-0", className),
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-xs uppercase tracking-wide text-muted-foreground",
				children: label
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "truncate text-sm font-medium text-foreground",
				children: value
			}),
			hint && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "truncate text-xs text-muted-foreground",
				children: hint
			})
		]
	});
}
function Skeleton({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		"data-slot": "skeleton",
		className: cn("bg-accent animate-pulse rounded-md", className),
		...props
	});
}
var buttonVariants = cva("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0", {
	variants: {
		variant: {
			default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
			destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
			outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
			secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
			ghost: "hover:bg-accent hover:text-accent-foreground",
			link: "text-primary underline-offset-4 hover:underline"
		},
		size: {
			default: "h-9 px-4 py-2",
			sm: "h-8 rounded-md px-3 text-xs",
			lg: "h-10 rounded-md px-8",
			icon: "h-9 w-9"
		}
	},
	defaultVariants: {
		variant: "default",
		size: "default"
	}
});
function Button({ className, variant, size, asChild = false, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(asChild ? Slot : "button", {
		"data-slot": "button",
		className: cn(buttonVariants({
			variant,
			size,
			className
		})),
		...props
	});
}
/** Presentation-only formatting helpers shared by dashboard cards. */
function formatTime(iso) {
	return new Date(iso).toLocaleTimeString([], {
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit"
	});
}
function formatDateTime(iso) {
	return new Date(iso).toLocaleString([], {
		month: "short",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit"
	});
}
function formatConfidence(confidence) {
	return `${Math.round(confidence * 100)}%`;
}
function formatCoordinate(value) {
	return value.toFixed(5);
}
function formatNumber(value) {
	return new Intl.NumberFormat().format(value);
}
function formatDistance(meters) {
	return meters >= 1e3 ? `${(meters / 1e3).toFixed(2)} km` : `${Math.round(meters)} m`;
}
function formatUptime(totalSeconds) {
	const seconds = Math.max(0, Math.floor(totalSeconds));
	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor(seconds % 3600 / 60);
	const secs = seconds % 60;
	const pad = (value) => String(value).padStart(2, "0");
	return `${pad(hours)}:${pad(minutes)}:${pad(secs)}`;
}
function formatTimeFromMs(timestampMs) {
	if (!Number.isFinite(timestampMs) || timestampMs <= 0) return "—";
	return new Date(timestampMs).toLocaleTimeString([], {
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit"
	});
}
function CardSkeleton() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex flex-col gap-3",
		"aria-hidden": true,
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-6 w-32" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-4 w-full" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-4 w-3/4" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-2 grid grid-cols-2 gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-14 w-full" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-14 w-full" })]
			})
		]
	});
}
/** Shared card shell used by every dashboard panel. */
function SectionCard({ title, description, actions, children, className, contentClassName, loading = false, error = false, errorMessage = "Telemetry unavailable. Retrying…", onRetry, updatedAt }) {
	const showBody = !loading && !error;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: cn("flex min-w-0 flex-col rounded-xl border border-border bg-card shadow-card", className),
		"aria-busy": loading || void 0,
		children: [
			(title || actions) && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "flex flex-wrap items-start justify-between gap-3 border-b border-border px-4 py-3 sm:px-5",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "min-w-0",
					children: [title && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "truncate text-sm font-semibold tracking-tight text-foreground",
						children: title
					}), description && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-0.5 text-xs text-muted-foreground",
						children: description
					})]
				}), actions && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "flex items-center gap-2",
					children: actions
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: cn("flex-1 p-4 sm:p-5", showBody && contentClassName),
				children: [
					loading && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardSkeleton, {}),
					error && !loading && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						role: "status",
						className: "flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, {
								className: "size-4 shrink-0",
								"aria-hidden": true
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "min-w-0 flex-1",
								children: errorMessage
							}),
							onRetry && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								type: "button",
								size: "sm",
								variant: "outline",
								className: "ml-auto shrink-0 border-destructive/40 hover:border-destructive/60",
								onClick: onRetry,
								children: "Retry"
							})
						]
					}),
					showBody && children
				]
			}),
			updatedAt !== void 0 && updatedAt > 0 && !loading && !error && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("footer", {
				className: "flex items-center justify-between gap-3 border-t border-border px-4 py-2.5 sm:px-5",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "inline-flex items-center gap-1.5 text-xs text-muted-foreground",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Clock, {
							className: "size-3",
							"aria-hidden": true
						}),
						"Updated ",
						formatTimeFromMs(updatedAt)
					]
				})
			})
		]
	});
}
var SEVERITY_ORDER = [
	"SAFE",
	"LOW",
	"MEDIUM",
	"HIGH",
	"CRITICAL"
];
var SEVERITY_LABELS = {
	SAFE: "Safe",
	LOW: "Low",
	MEDIUM: "Medium",
	HIGH: "High",
	CRITICAL: "Critical"
};
/** Semantic token names used for severity coloring (no raw hex in components). */
var SEVERITY_TOKEN = {
	SAFE: "success",
	LOW: "primary",
	MEDIUM: "warning",
	HIGH: "warning",
	CRITICAL: "danger"
};
var CRACK_CLASSES = [
	"small_crack",
	"medium_crack",
	"large_crack",
	"broken_chain"
];
var CRACK_CLASS_LABELS = {
	small_crack: "Small Crack",
	medium_crack: "Medium Crack",
	large_crack: "Large Crack",
	broken_chain: "Broken Chain"
};
var CONNECTION_LABELS = {
	connected: "Connected",
	connecting: "Connecting",
	disconnected: "Disconnected",
	error: "Error"
};
var DEVICE_LABELS = {
	camera: "Camera",
	esp32: "ESP32",
	gps: "GPS",
	gsm: "GSM"
};
var CAMERA_SOURCE_LABELS = {
	usb: "USB Camera",
	"esp32-cam": "ESP32-CAM",
	"demo-video": "Demo Video"
};
var HEALTH_STATUS_LABELS = {
	excellent: "Excellent",
	good: "Good",
	warning: "Warning",
	critical: "Critical"
};
var HEALTH_THRESHOLDS = {
	excellent: 90,
	good: 75,
	warning: 50
};
/** Pie slice colors for the detection distribution chart. */
var DISTRIBUTION_SLICE_COLORS = [
	"var(--color-chart-2)",
	"var(--color-chart-3)",
	"var(--color-chart-1)",
	"var(--color-chart-4)"
];
/** Stacked area series for the severity trend chart. */
var SEVERITY_TREND_SERIES = [
	{
		key: "low",
		label: "Low",
		color: "var(--color-chart-1)"
	},
	{
		key: "medium",
		label: "Medium",
		color: "var(--color-chart-3)"
	},
	{
		key: "high",
		label: "High",
		color: "var(--color-chart-5)"
	},
	{
		key: "critical",
		label: "Critical",
		color: "var(--color-chart-4)"
	}
];
var TOKEN_STYLES = {
	success: "border-success/40 bg-success/15 text-success",
	primary: "border-primary/40 bg-primary/15 text-primary",
	warning: "border-warning/40 bg-warning/15 text-warning",
	danger: "border-destructive/40 bg-destructive/15 text-destructive"
};
function SeverityBadge({ severity, className }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: cn("inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium", TOKEN_STYLES[SEVERITY_TOKEN[severity]], className),
		children: SEVERITY_LABELS[severity]
	});
}
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
function useLiveQuery(key, fetcher, intervalMs, options, realtimeChannel) {
	const realtimeLive = useIsRealtimeLive(realtimeChannel);
	return useQuery({
		queryKey: key,
		queryFn: fetcher,
		refetchInterval: realtimeLive ? false : intervalMs,
		staleTime: intervalMs / 2,
		retry: 1,
		...options
	});
}
var randomBetween = (min, max) => min + Math.random() * (max - min);
var randomInt = (min, max) => Math.floor(randomBetween(min, max + 1));
var pickOne = (items) => items[randomInt(0, items.length - 1)];
var isoMinutesAgo = (minutes) => (/* @__PURE__ */ new Date(Date.now() - minutes * 6e4)).toISOString();
var severityFromClass = (crackClass, confidence) => {
	if (crackClass === "broken_chain") return "CRITICAL";
	if (crackClass === "large_crack") return confidence > .8 ? "CRITICAL" : "HIGH";
	if (crackClass === "medium_crack") return "MEDIUM";
	return confidence > .6 ? "LOW" : "SAFE";
};
var healthStatusFromScore = (score) => {
	if (score >= HEALTH_THRESHOLDS.excellent) return "excellent";
	if (score >= HEALTH_THRESHOLDS.good) return "good";
	if (score >= HEALTH_THRESHOLDS.warning) return "warning";
	return "critical";
};
var BASE_LAT = 19.076;
var BASE_LON = 72.8777;
var delay = (value, ms = 120) => new Promise((resolve) => setTimeout(() => resolve(value), ms));
/** Mutable in-memory state so UI actions feel real without a backend. */
var state = {
	camera: {
		source: "usb",
		state: "disconnected",
		fps: 0,
		width: 1280,
		height: 720,
		detectionActive: false,
		streamUrl: null
	},
	rover: {
		state: "connected",
		speed: 150,
		lastCommand: null,
		emergencyStopped: false
	}
};
var detections = Array.from({ length: 42 }, (_, index) => {
	const crackClass = pickOne(CRACK_CLASSES);
	const confidence = randomBetween(.55, .99);
	return {
		id: `det-${index + 1}`,
		timestamp: isoMinutesAgo(index * 7 + randomInt(0, 5)),
		crackClass,
		confidence,
		severity: severityFromClass(crackClass, confidence),
		latitude: BASE_LAT + randomBetween(-.05, .05),
		longitude: BASE_LON + randomBetween(-.05, .05),
		status: pickOne([
			"new",
			"reviewed",
			"resolved"
		])
	};
});
var deviceStatus = (id, fallback) => ({
	id,
	label: DEVICE_LABELS[id],
	state: fallback
});
var mockApi = {
	getSystemStatus: () => delay({
		online: true,
		uptimeSeconds: randomInt(3600, 86400),
		version: APP_CONFIG.version,
		devices: [
			{ ...deviceStatus("camera", state.camera.state) },
			{ ...deviceStatus("esp32", state.rover.state) },
			{ ...deviceStatus("gps", "connected") },
			{ ...deviceStatus("gsm", "connected") }
		]
	}),
	getCameraState: () => delay({
		...state.camera,
		fps: state.camera.state === "connected" ? randomInt(22, 30) : 0
	}),
	connectCamera: ({ source }) => {
		state.camera = {
			...state.camera,
			source,
			state: "connected",
			detectionActive: true,
			fps: randomInt(22, 30),
			streamUrl: null
		};
		return delay(state.camera, 400);
	},
	disconnectCamera: () => {
		state.camera = {
			...state.camera,
			state: "disconnected",
			detectionActive: false,
			fps: 0
		};
		return delay(state.camera, 250);
	},
	getLatestAlert: () => {
		const latest = detections[0];
		return delay({
			id: `alert-${latest.id}`,
			severity: latest.severity,
			crackClass: latest.crackClass,
			confidence: latest.confidence,
			message: latest.severity === "CRITICAL" ? "Critical rail defect detected. Immediate inspection required." : "Rail anomaly detected and logged for review.",
			timestamp: latest.timestamp
		});
	},
	getTrackHealth: () => {
		const overall = randomBetween(58, 96);
		return delay({
			overall,
			status: healthStatusFromScore(overall),
			inspectedMeters: randomInt(1200, 8600),
			updatedAt: (/* @__PURE__ */ new Date()).toISOString()
		});
	},
	getGps: () => delay({
		latitude: BASE_LAT + randomBetween(-.01, .01),
		longitude: BASE_LON + randomBetween(-.01, .01),
		satellites: randomInt(6, 14),
		hasFix: true,
		updatedAt: (/* @__PURE__ */ new Date()).toISOString()
	}),
	getGsmStatus: () => delay({
		state: "connected",
		signalStrength: randomInt(55, 98),
		operator: "Airtel",
		lastMessageAt: isoMinutesAgo(randomInt(2, 90))
	}),
	sendSms: ({ phoneNumber }) => delay({
		ok: true,
		message: `Message queued for ${phoneNumber}`
	}, 500),
	getStatistics: () => {
		const counts = CRACK_CLASSES.map((crackClass) => detections.filter((d) => d.crackClass === crackClass).length);
		return delay({
			totalDetections: detections.length,
			smallCrack: counts[0] ?? 0,
			mediumCrack: counts[1] ?? 0,
			largeCrack: counts[2] ?? 0,
			brokenChain: counts[3] ?? 0,
			criticalAlerts: detections.filter((d) => d.severity === "CRITICAL").length
		});
	},
	getDetectionDistribution: () => delay(CRACK_CLASSES.map((crackClass) => ({
		crackClass,
		count: detections.filter((d) => d.crackClass === crackClass).length
	}))),
	getSeverityTrend: () => delay(Array.from({ length: 12 }, (_, index) => ({
		timestamp: isoMinutesAgo((11 - index) * 30),
		low: randomInt(0, 6),
		medium: randomInt(0, 5),
		high: randomInt(0, 4),
		critical: randomInt(0, 2)
	}))),
	getDetections: (query = {}) => {
		const { search = "", severity = "ALL", page = 1, pageSize = 8 } = query;
		const term = search.trim().toLowerCase();
		const filtered = detections.filter((d) => {
			const matchesSeverity = severity === "ALL" || d.severity === severity;
			const matchesTerm = !term || d.crackClass.includes(term) || d.severity.toLowerCase().includes(term) || d.status.includes(term);
			return matchesSeverity && matchesTerm;
		});
		const start = (page - 1) * pageSize;
		return delay({
			items: filtered.slice(start, start + pageSize),
			total: filtered.length,
			page,
			pageSize
		});
	},
	getLatestSnapshot: () => {
		const latest = detections[0];
		return delay({
			id: `snap-${latest.id}`,
			imageUrl: null,
			timestamp: latest.timestamp,
			severity: latest.severity,
			crackClass: latest.crackClass
		});
	},
	getRoverState: () => delay({ ...state.rover }),
	sendRoverCommand: ({ command, speed }) => {
		state.rover = {
			...state.rover,
			lastCommand: command,
			emergencyStopped: command === "emergency_stop",
			speed: command === "emergency_stop" ? 0 : command === "set_speed" ? speed ?? state.rover.speed : state.rover.speed
		};
		return delay({ ...state.rover }, 150);
	}
};
/**
* REST implementation of MonitoringApi.
* Talks to the FastAPI backend using fetch with timeout, retry, and error handling.
* No component changes required — this satisfies the same interface as mockApi.
*/
var DEFAULT_TIMEOUT_MS = 8e3;
var MAX_RETRIES = 2;
async function httpGet(path, params) {
	const url = new URL(`${API_BASE_URL}${path}`);
	if (params) {
		for (const [k, v] of Object.entries(params)) if (v !== void 0) url.searchParams.set(k, String(v));
	}
	for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
		const controller = new AbortController();
		const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
		try {
			const res = await fetch(url.toString(), { signal: controller.signal });
			clearTimeout(timer);
			if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText} — ${path}`);
			return await res.json();
		} catch (err) {
			clearTimeout(timer);
			if (attempt === MAX_RETRIES) throw err;
			await new Promise((r) => setTimeout(r, 300 * (attempt + 1)));
		}
	}
	throw new Error("Unreachable");
}
async function httpPost(path, body) {
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);
	try {
		const res = await fetch(`${API_BASE_URL}${path}`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: body !== void 0 ? JSON.stringify(body) : null,
			signal: controller.signal
		});
		clearTimeout(timer);
		if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText} — ${path}`);
		return await res.json();
	} catch (err) {
		clearTimeout(timer);
		throw err;
	}
}
/**
* Single seam for all UI data access.
* FEATURE_FLAGS.useMockData=true  → in-memory mock (no backend required).
* FEATURE_FLAGS.useMockData=false → real FastAPI REST backend.
*/
var monitoringApi = FEATURE_FLAGS.useMockData ? mockApi : {
	getSystemStatus: () => httpGet(API_ENDPOINTS.systemStatus),
	getCameraState: () => httpGet(API_ENDPOINTS.cameraState),
	connectCamera: (req) => httpPost(API_ENDPOINTS.cameraConnect, {
		source: req.source,
		videoPath: req.videoPath
	}),
	disconnectCamera: () => httpPost(API_ENDPOINTS.cameraDisconnect),
	getLatestAlert: () => httpGet(API_ENDPOINTS.latestAlert),
	getTrackHealth: () => httpGet(API_ENDPOINTS.trackHealth),
	getGps: () => httpGet(API_ENDPOINTS.gps),
	getGsmStatus: () => httpGet(API_ENDPOINTS.gsmStatus),
	sendSms: (req) => httpPost(API_ENDPOINTS.sendSms, req),
	getStatistics: () => httpGet(API_ENDPOINTS.statistics),
	getDetectionDistribution: () => httpGet(API_ENDPOINTS.detectionDistribution),
	getSeverityTrend: () => httpGet(API_ENDPOINTS.severityTrend),
	getDetections: (query = {}) => httpGet(API_ENDPOINTS.detections, {
		search: query.search,
		severity: query.severity,
		page: query.page,
		pageSize: query.pageSize
	}),
	getLatestSnapshot: () => httpGet(API_ENDPOINTS.latestSnapshot),
	getRoverState: () => httpGet(API_ENDPOINTS.roverState),
	sendRoverCommand: (req) => httpPost(API_ENDPOINTS.roverCommand, req)
};
function ActiveAlertCard() {
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(["alert"], () => monitoringApi.getLatestAlert(), POLLING_INTERVALS.alert, void 0, "telemetry");
	const critical = data?.severity === "HIGH" || data?.severity === "CRITICAL";
	const Icon = critical ? TriangleAlert : ShieldCheck;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SectionCard, {
		title: "Active Alert",
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		actions: data ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SeverityBadge, { severity: data.severity }) : null,
		contentClassName: "flex flex-col gap-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-start gap-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: `grid size-10 shrink-0 place-items-center rounded-lg ${critical ? "bg-destructive/15 text-destructive" : "bg-success/15 text-success"}`,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, {
					className: `size-5 ${critical ? "animate-pulse" : ""}`,
					"aria-hidden": true
				})
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "min-w-0 text-sm text-foreground",
				"aria-live": "polite",
				"aria-atomic": "true",
				children: data?.message ?? "Awaiting telemetry…"
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid grid-cols-2 gap-4",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Class",
					value: data?.crackClass ? CRACK_CLASS_LABELS[data.crackClass] : "None"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Confidence",
					value: formatConfidence(data?.confidence ?? 0)
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Detected",
					value: data ? formatTime(data.timestamp) : "—"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Alert ID",
					value: data?.id ?? "—"
				})
			]
		})]
	});
}
var DetectionDistributionChart = (0, import_react.memo)(function DetectionDistributionChart() {
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(["distribution"], () => monitoringApi.getDetectionDistribution(), POLLING_INTERVALS.statistics);
	const chartData = (0, import_react.useMemo)(() => (data ?? []).map((slice) => ({
		name: CRACK_CLASS_LABELS[slice.crackClass],
		value: slice.count
	})), [data]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SectionCard, {
		title: "Detection Distribution",
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "h-64 w-full",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
				width: "100%",
				height: "100%",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(PieChart, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Pie, {
					data: chartData,
					dataKey: "value",
					nameKey: "name",
					innerRadius: "55%",
					outerRadius: "80%",
					paddingAngle: 2,
					stroke: "var(--color-card)",
					children: chartData.map((entry, index) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cell, { fill: DISTRIBUTION_SLICE_COLORS[index % DISTRIBUTION_SLICE_COLORS.length] }, entry.name))
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { contentStyle: {
					background: "var(--color-popover)",
					border: "1px solid var(--color-border)",
					borderRadius: "0.5rem",
					color: "var(--color-popover-foreground)",
					fontSize: "0.75rem"
				} })] })
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
			className: "mt-2 grid grid-cols-2 gap-2",
			children: chartData.map((entry, index) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
				className: "flex items-center gap-2 text-xs text-muted-foreground",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "size-2.5 rounded-full",
						style: { background: DISTRIBUTION_SLICE_COLORS[index % DISTRIBUTION_SLICE_COLORS.length] }
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "truncate",
						children: entry.name
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "ml-auto font-medium text-foreground",
						children: entry.value
					})
				]
			}, entry.name))
		})]
	});
});
var SeverityTrendChart = (0, import_react.memo)(function SeverityTrendChart() {
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(["severity-trend"], () => monitoringApi.getSeverityTrend(), POLLING_INTERVALS.statistics);
	const chartData = (0, import_react.useMemo)(() => (data ?? []).map((point) => ({
		...point,
		label: formatTime(point.timestamp).slice(0, 5)
	})), [data]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionCard, {
		title: "Severity Trend",
		description: "Detections per interval",
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "h-64 w-full",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
				width: "100%",
				height: "100%",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(AreaChart, {
					data: chartData,
					margin: {
						top: 8,
						right: 8,
						bottom: 0,
						left: -20
					},
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("defs", { children: SEVERITY_TREND_SERIES.map((series) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("linearGradient", {
							id: `fill-${series.key}`,
							x1: "0",
							y1: "0",
							x2: "0",
							y2: "1",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
								offset: "0%",
								stopColor: series.color,
								stopOpacity: .5
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("stop", {
								offset: "100%",
								stopColor: series.color,
								stopOpacity: .04
							})]
						}, series.key)) }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
							stroke: "var(--color-border)",
							strokeDasharray: "3 3",
							vertical: false
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
							dataKey: "label",
							tick: {
								fontSize: 11,
								fill: "var(--color-muted-foreground)"
							},
							tickLine: false,
							axisLine: false
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
							allowDecimals: false,
							tick: {
								fontSize: 11,
								fill: "var(--color-muted-foreground)"
							},
							tickLine: false,
							axisLine: false
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { contentStyle: {
							background: "var(--color-popover)",
							border: "1px solid var(--color-border)",
							borderRadius: "0.5rem",
							color: "var(--color-popover-foreground)",
							fontSize: "0.75rem"
						} }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Legend, { wrapperStyle: { fontSize: "0.75rem" } }),
						SEVERITY_TREND_SERIES.map((series) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Area, {
							type: "monotone",
							dataKey: series.key,
							name: series.label,
							stackId: "1",
							stroke: series.color,
							fill: `url(#fill-${series.key})`,
							strokeWidth: 2
						}, series.key))
					]
				})
			})
		})
	});
});
var STATE_STYLES = {
	connected: "bg-success",
	connecting: "bg-warning animate-pulse",
	disconnected: "bg-muted-foreground",
	error: "bg-destructive"
};
function StatusDot({ state, className }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		role: "img",
		"aria-label": CONNECTION_LABELS[state],
		className: cn("inline-block size-2 shrink-0 rounded-full", STATE_STYLES[state], className)
	});
}
/**
* useMjpegStream — manages the lifecycle of an MJPEG browser stream.
*
* Builds the full stream URL from the backend base URL, tracks live/error state,
* and schedules automatic reconnection when the stream is interrupted.
*/
var STREAM_PATH = "/api/camera/stream";
var RECONNECT_DELAY_MS = 3e3;
function useMjpegStream({ enabled }) {
	const [status, setStatus] = (0, import_react.useState)("idle");
	const [revision, setRevision] = (0, import_react.useState)(0);
	const retryTimer = (0, import_react.useRef)(null);
	const clearRetry = () => {
		if (retryTimer.current !== null) {
			clearTimeout(retryTimer.current);
			retryTimer.current = null;
		}
	};
	(0, import_react.useEffect)(() => {
		if (!enabled) {
			clearRetry();
			setStatus("idle");
			return;
		}
		setStatus("loading");
		return clearRetry;
	}, [enabled]);
	const onLoad = (0, import_react.useCallback)(() => {
		clearRetry();
		setStatus("live");
	}, []);
	const onError = (0, import_react.useCallback)(() => {
		if (!enabled) return;
		setStatus("error");
		clearRetry();
		retryTimer.current = setTimeout(() => {
			setRevision((r) => r + 1);
			setStatus("loading");
		}, RECONNECT_DELAY_MS);
	}, [enabled]);
	return {
		src: enabled ? `${API_BASE_URL}${STREAM_PATH}?r=${revision}` : null,
		status,
		onLoad,
		onError
	};
}
/**
* MjpegPlayer — renders a live MJPEG stream from the FastAPI backend.
*
* Delegates all stream lifecycle to useMjpegStream.
* Shows appropriate states: loading spinner, live feed, error overlay, and disconnected.
* This component is layout-agnostic — it fills its container absolutely.
*/
function MjpegPlayer({ enabled }) {
	const { src, status, onLoad, onError } = useMjpegStream({ enabled });
	if (!enabled) return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "absolute inset-0 flex flex-col items-center justify-center gap-2 text-muted-foreground",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CameraOff, {
			className: "size-8",
			"aria-hidden": true
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "text-xs",
			children: "No camera connected"
		})]
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
		src && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("img", {
			src,
			alt: "Live MJPEG camera feed",
			className: "absolute inset-0 h-full w-full object-contain",
			onLoad,
			onError
		}, src),
		status === "loading" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "absolute inset-0 flex flex-col items-center justify-center gap-2 bg-background/70 text-muted-foreground",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, {
				className: "size-8 animate-spin",
				"aria-hidden": true
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "text-xs",
				children: "Connecting to stream…"
			})]
		}),
		status === "error" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "absolute inset-0 flex flex-col items-center justify-center gap-2 bg-background/70 text-destructive",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, {
				className: "size-8",
				"aria-hidden": true
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "text-xs",
				children: "Stream interrupted — reconnecting…"
			})]
		}),
		status === "live" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Camera, {
			className: "absolute bottom-12 left-3 size-5 text-primary opacity-40",
			"aria-hidden": true
		})
	] });
}
var SOURCES = [
	"usb",
	"esp32-cam",
	"demo-video"
];
function CameraFeedCard() {
	const queryClient = useQueryClient();
	const { data, isError, refetch, dataUpdatedAt } = useLiveQuery(["camera"], () => monitoringApi.getCameraState(), POLLING_INTERVALS.camera, void 0, "camera-status");
	const connect = useMutation({
		mutationFn: (source) => monitoringApi.connectCamera({ source }),
		onSuccess: (state) => queryClient.setQueryData(["camera"], state)
	});
	const disconnect = useMutation({
		mutationFn: () => monitoringApi.disconnectCamera(),
		onSuccess: (state) => queryClient.setQueryData(["camera"], state)
	});
	const state = data?.state ?? "disconnected";
	const live = state === "connected";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SectionCard, {
		title: "Live Camera Feed",
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		description: data ? CAMERA_SOURCE_LABELS[data.source] : "Awaiting source",
		className: "h-full",
		actions: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center gap-2 rounded-md border border-border px-2 py-1",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusDot, { state }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "text-xs text-muted-foreground",
				children: live ? `${data?.fps ?? 0} FPS` : "Offline"
			})]
		}),
		contentClassName: "flex flex-col gap-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "relative aspect-video w-full overflow-hidden rounded-lg border border-border bg-background",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MjpegPlayer, { enabled: live }),
				live && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "absolute left-3 top-3 z-10 flex items-center gap-2 rounded-md bg-background/80 px-2 py-1 text-xs font-medium text-foreground",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2 animate-pulse rounded-full bg-destructive" }), " LIVE"]
				}),
				data && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "absolute bottom-3 right-3 z-10 rounded-md bg-background/80 px-2 py-1 text-xs text-muted-foreground",
					children: [
						data.width,
						"×",
						data.height
					]
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-wrap items-center gap-2",
			children: [SOURCES.map((source) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
				size: "sm",
				variant: data?.source === source && live ? "default" : "outline",
				disabled: connect.isPending,
				onClick: () => connect.mutate(source),
				children: CAMERA_SOURCE_LABELS[source]
			}, source)), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
				size: "sm",
				variant: "ghost",
				className: "ml-auto",
				disabled: !live || disconnect.isPending,
				onClick: () => disconnect.mutate(),
				children: "Disconnect"
			})]
		})]
	});
}
function GpsCard() {
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(["gps"], () => monitoringApi.getGps(), POLLING_INTERVALS.gps, void 0, "telemetry");
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SectionCard, {
		title: "GPS Location",
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		actions: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
			className: "flex items-center gap-1.5 text-xs text-muted-foreground",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Satellite, {
					className: "size-4",
					"aria-hidden": true
				}),
				data?.satellites ?? 0,
				" sats"
			]
		}),
		contentClassName: "flex flex-col gap-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center gap-3 rounded-lg border border-border bg-background/60 p-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MapPin, {
				className: `size-5 ${data?.hasFix ? "text-primary" : "text-muted-foreground"}`,
				"aria-hidden": true
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "min-w-0",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "truncate font-mono text-sm text-foreground",
					children: data ? `${formatCoordinate(data.latitude)}, ${formatCoordinate(data.longitude)}` : "—"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-xs text-muted-foreground",
					children: data?.hasFix ? "Fix acquired" : "No satellite fix"
				})]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid grid-cols-2 gap-4",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Latitude",
					value: data ? formatCoordinate(data.latitude) : "—"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Longitude",
					value: data ? formatCoordinate(data.longitude) : "—"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Updated",
					value: data ? formatTime(data.updatedAt) : "—"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Satellites",
					value: data?.satellites ?? 0
				})
			]
		})]
	});
}
function Input({ className, type, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
		type,
		"data-slot": "input",
		className: cn("border-input file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground flex h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm", "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]", className),
		...props
	});
}
function Textarea({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("textarea", {
		"data-slot": "textarea",
		className: cn("border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 aria-invalid:border-destructive flex field-sizing-content min-h-16 w-full rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 md:text-sm", className),
		...props
	});
}
function GsmCard() {
	const [phoneNumber, setPhoneNumber] = (0, import_react.useState)("");
	const [message, setMessage] = (0, import_react.useState)("");
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(["gsm"], () => monitoringApi.getGsmStatus(), POLLING_INTERVALS.gsm, void 0, "telemetry");
	const sendSms = useMutation({
		mutationFn: () => monitoringApi.sendSms({
			phoneNumber,
			message
		}),
		onSuccess: (result) => {
			if (result.ok) {
				toast.success(result.message);
				setMessage("");
			} else toast.error(result.message);
		},
		onError: () => toast.error("Failed to send SMS")
	});
	const canSend = phoneNumber.trim().length >= 6 && message.trim().length > 0;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SectionCard, {
		title: "GSM Messaging",
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		actions: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
			className: "flex items-center gap-1.5 text-xs text-muted-foreground",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusDot, { state: data?.state ?? "disconnected" }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SignalHigh, {
					className: "size-4",
					"aria-hidden": true
				}),
				data?.signalStrength ?? 0,
				"%"
			]
		}),
		contentClassName: "flex flex-col gap-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid grid-cols-2 gap-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
				label: "Operator",
				value: data?.operator ?? "—"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
				label: "Last message",
				value: data?.lastMessageAt ? formatTime(data.lastMessageAt) : "—"
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
			className: "flex flex-col gap-3",
			onSubmit: (event) => {
				event.preventDefault();
				if (canSend) sendSms.mutate();
			},
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
					value: phoneNumber,
					onChange: (event) => setPhoneNumber(event.target.value),
					placeholder: "+91 98765 43210",
					"aria-label": "Recipient phone number",
					inputMode: "tel"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Textarea, {
					value: message,
					onChange: (event) => setMessage(event.target.value),
					placeholder: "Alert message…",
					"aria-label": "SMS message",
					rows: 3
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					type: "submit",
					size: "sm",
					disabled: !canSend || sendSms.isPending,
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MessageSquare, {
						className: "size-4",
						"aria-hidden": true
					}), sendSms.isPending ? "Sending…" : "Send SMS Alert"]
				})
			]
		})]
	});
}
function Progress({ className, value, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Root, {
		"data-slot": "progress",
		className: cn("bg-primary/20 relative h-2 w-full overflow-hidden rounded-full", className),
		...props,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Indicator, {
			"data-slot": "progress-indicator",
			className: "bg-primary h-full w-full flex-1 transition-all",
			style: { transform: `translateX(-${100 - (value || 0)}%)` }
		})
	});
}
var STATUS_STYLES = {
	excellent: "text-success",
	good: "text-success",
	warning: "text-warning",
	critical: "text-destructive"
};
function TrackHealthCard() {
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(["track-health"], () => monitoringApi.getTrackHealth(), POLLING_INTERVALS.health, void 0, "telemetry");
	const score = data?.overall ?? 0;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SectionCard, {
		title: "Track Health",
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		actions: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Activity, {
			className: "size-4 text-muted-foreground",
			"aria-hidden": true
		}),
		contentClassName: "flex flex-col gap-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-baseline gap-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-4xl font-semibold tracking-tight text-foreground",
						children: Math.round(score)
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-sm text-muted-foreground",
						children: "/ 100"
					}),
					data && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: `ml-auto text-sm font-medium ${STATUS_STYLES[data.status]}`,
						children: HEALTH_STATUS_LABELS[data.status]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Progress, {
				value: score,
				"aria-label": "Overall track health score"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid grid-cols-2 gap-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Inspected",
					value: data ? formatDistance(data.inspectedMeters) : "—"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Updated",
					value: data ? formatTime(data.updatedAt) : "—"
				})]
			})
		]
	});
}
function Select({ ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Select$1, {
		"data-slot": "select",
		...props
	});
}
function SelectValue({ ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue$1, {
		"data-slot": "select-value",
		...props
	});
}
function SelectTrigger({ className, size = "default", children, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectTrigger$1, {
		"data-slot": "select-trigger",
		"data-size": size,
		className: cn("border-input data-[placeholder]:text-muted-foreground aria-invalid:border-destructive focus-visible:border-ring focus-visible:ring-ring/50 flex w-fit items-center justify-between gap-2 rounded-md border bg-transparent px-3 py-2 text-sm whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 data-[size=default]:h-9 data-[size=sm]:h-8 *:data-[slot=select-value]:line-clamp-1 *:data-[slot=select-value]:flex *:data-[slot=select-value]:items-center *:data-[slot=select-value]:gap-2 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4", className),
		...props,
		children: [children, /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectIcon, {
			asChild: true,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "opacity-50" })
		})]
	});
}
function SelectContent({ className, children, position = "popper", ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectPortal, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent$1, {
		"data-slot": "select-content",
		className: cn("bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2 relative z-50 max-h-(--radix-select-content-available-height) min-w-[8rem] overflow-x-hidden overflow-y-auto rounded-md border shadow-md", position === "popper" && "data-[side=bottom]:translate-y-1 data-[side=top]:-translate-y-1", className),
		position,
		...props,
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectScrollUpButton, {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectViewport, {
				className: cn("p-1", position === "popper" && "h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)] scroll-my-1"),
				children
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectScrollDownButton, {})
		]
	}) });
}
function SelectItem({ className, children, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectItem$1, {
		"data-slot": "select-item",
		className: cn("focus:bg-accent focus:text-accent-foreground [&_svg:not([class*='text-'])]:text-muted-foreground relative flex w-full cursor-default items-center gap-2 rounded-sm py-1.5 pr-8 pl-2 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4", className),
		...props,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "absolute right-2 flex size-3.5 items-center justify-center",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItemIndicator, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "size-4" }) })
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItemText, { children })]
	});
}
function SelectScrollUpButton({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectScrollUpButton$1, {
		"data-slot": "select-scroll-up-button",
		className: cn("flex cursor-default items-center justify-center py-1", className),
		...props,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronUp, { className: "size-4" })
	});
}
function SelectScrollDownButton({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectScrollDownButton$1, {
		"data-slot": "select-scroll-down-button",
		className: cn("flex cursor-default items-center justify-center py-1", className),
		...props,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "size-4" })
	});
}
function Table({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		"data-slot": "table-container",
		className: "relative w-full overflow-x-auto",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("table", {
			"data-slot": "table",
			className: cn("w-full caption-bottom text-sm", className),
			...props
		})
	});
}
function TableHeader({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", {
		"data-slot": "table-header",
		className: cn("[&_tr]:border-b", className),
		...props
	});
}
function TableBody({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", {
		"data-slot": "table-body",
		className: cn("[&_tr:last-child]:border-0", className),
		...props
	});
}
function TableRow({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", {
		"data-slot": "table-row",
		className: cn("hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors", className),
		...props
	});
}
function TableHead({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
		"data-slot": "table-head",
		className: cn("text-muted-foreground h-10 px-2 text-left align-middle font-medium whitespace-nowrap [&:has([role=checkbox])]:pr-0", className),
		...props
	});
}
function TableCell({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
		"data-slot": "table-cell",
		className: cn("p-2 align-middle [&:has([role=checkbox])]:pr-0", className),
		...props
	});
}
function DetectionHistoryTable() {
	const [search, setSearch] = (0, import_react.useState)("");
	const [severity, setSeverity] = (0, import_react.useState)("ALL");
	const [page, setPage] = (0, import_react.useState)(1);
	const deferredSearch = (0, import_react.useDeferredValue)(search);
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery([
		"detections",
		deferredSearch,
		severity,
		page
	], () => monitoringApi.getDetections({
		search: deferredSearch,
		severity,
		page,
		pageSize: 8
	}), POLLING_INTERVALS.detections);
	const total = data?.total ?? 0;
	const pageCount = Math.max(1, Math.ceil(total / 8));
	const hasFilters = search.trim() !== "" || severity !== "ALL";
	const resetFilters = () => {
		setSearch("");
		setSeverity("ALL");
		setPage(1);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SectionCard, {
		title: "Detection History",
		description: `${total} record${total === 1 ? "" : "s"}`,
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		contentClassName: "flex flex-col gap-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-col gap-3 sm:flex-row sm:items-center",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "relative flex-1",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Search, {
						className: "pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground",
						"aria-hidden": true
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
						value: search,
						onChange: (event) => {
							setSearch(event.target.value);
							setPage(1);
						},
						placeholder: "Search by ID or class…",
						"aria-label": "Search detections",
						className: "pl-9"
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select, {
						value: severity,
						onValueChange: (value) => {
							setSeverity(value);
							setPage(1);
						},
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, {
							className: "w-full sm:w-44",
							"aria-label": "Filter by severity",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, { placeholder: "Severity" })
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
							value: "ALL",
							children: "All severities"
						}), SEVERITY_ORDER.map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
							value: item,
							children: SEVERITY_LABELS[item]
						}, item))] })]
					}), hasFilters && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						type: "button",
						size: "sm",
						variant: "ghost",
						onClick: resetFilters,
						"aria-label": "Clear filters",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, {
							className: "size-4",
							"aria-hidden": true
						}), "Clear"]
					})]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Table, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, { children: "Time" }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, { children: "Class" }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, { children: "Severity" }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
					className: "text-right",
					children: "Confidence"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
					className: "hidden md:table-cell",
					children: "Location"
				})
			] }) }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableBody, { children: [(data?.items ?? []).map((detection) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
					className: "whitespace-nowrap text-muted-foreground",
					children: formatDateTime(detection.timestamp)
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
					className: "whitespace-nowrap",
					children: CRACK_CLASS_LABELS[detection.crackClass]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SeverityBadge, { severity: detection.severity }) }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
					className: "text-right tabular-nums",
					children: formatConfidence(detection.confidence)
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableCell, {
					className: "hidden whitespace-nowrap font-mono text-xs text-muted-foreground md:table-cell",
					children: [
						formatCoordinate(detection.latitude),
						", ",
						formatCoordinate(detection.longitude)
					]
				})
			] }, detection.id)), data && data.items.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableRow, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
				colSpan: 5,
				className: "py-8 text-center text-muted-foreground",
				children: hasFilters ? "No detections match the current filters." : "No detections recorded yet."
			}) })] })] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center justify-between gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
					className: "text-xs text-muted-foreground",
					children: [
						"Page ",
						page,
						" of ",
						pageCount
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						size: "sm",
						variant: "outline",
						disabled: page <= 1,
						onClick: () => setPage((current) => Math.max(1, current - 1)),
						children: "Previous"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						size: "sm",
						variant: "outline",
						disabled: page >= pageCount,
						onClick: () => setPage((current) => Math.min(pageCount, current + 1)),
						children: "Next"
					})]
				})]
			})
		]
	});
}
function Slider({ className, defaultValue, value, min = 0, max = 100, ...props }) {
	const _values = import_react.useMemo(() => Array.isArray(value) ? value : Array.isArray(defaultValue) ? defaultValue : [min, max], [
		value,
		defaultValue,
		min,
		max
	]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Slider$1, {
		"data-slot": "slider",
		min,
		max,
		className: cn("relative flex w-full touch-none items-center select-none data-[disabled]:opacity-50", className),
		...value !== void 0 ? { value } : {},
		...defaultValue !== void 0 ? { defaultValue } : {},
		...props,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SliderTrack, {
			"data-slot": "slider-track",
			className: "bg-muted relative h-2 w-full grow overflow-hidden rounded-full",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SliderRange, {
				"data-slot": "slider-range",
				className: "bg-primary absolute h-full"
			})
		}), _values.map((valueItem, index) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SliderThumb, {
			"data-slot": "slider-thumb",
			className: "border-primary bg-background ring-ring/50 block size-4 shrink-0 rounded-full border shadow-sm transition-[color,box-shadow] hover:ring-4 focus-visible:ring-4 focus-visible:outline-hidden disabled:pointer-events-none disabled:opacity-50"
		}, index))]
	});
}
var PAD = [
	{
		command: "forward",
		icon: ArrowUp,
		label: "Forward",
		cell: "col-start-2 row-start-1"
	},
	{
		command: "stop",
		icon: Square,
		label: "Stop",
		cell: "col-start-2 row-start-2"
	},
	{
		command: "backward",
		icon: ArrowDown,
		label: "Backward",
		cell: "col-start-2 row-start-3"
	}
];
var SPEED_MAX = 255;
function RoverControlCard() {
	const queryClient = useQueryClient();
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(["rover"], () => monitoringApi.getRoverState(), POLLING_INTERVALS.rover, void 0, "telemetry");
	const send = useMutation({
		mutationFn: (payload) => monitoringApi.sendRoverCommand(payload),
		onSuccess: (state) => queryClient.setQueryData(["rover"], state)
	});
	const speed = data?.speed ?? 0;
	const stopped = data?.emergencyStopped ?? false;
	const disabled = send.isPending || data?.state !== "connected";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SectionCard, {
		title: "Rover Control",
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		actions: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusDot, { state: data?.state ?? "disconnected" }),
		contentClassName: "flex flex-col gap-5",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mx-auto grid w-full max-w-[13rem] grid-cols-3 grid-rows-3 gap-2",
				children: PAD.map(({ command, icon: Icon, label, cell }) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					variant: command === "stop" ? "secondary" : "outline",
					size: "icon",
					"aria-label": label,
					className: `${cell} size-full aspect-square`,
					disabled: disabled || stopped && command !== "stop",
					onClick: () => send.mutate({ command }),
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, {
						className: "size-4",
						"aria-hidden": true
					})
				}, command))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "space-y-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center justify-between",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-xs uppercase tracking-wide text-muted-foreground",
						children: "Speed"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "text-sm font-medium text-foreground",
						children: [
							speed,
							" / ",
							SPEED_MAX
						]
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Slider, {
					value: [speed],
					min: 0,
					max: SPEED_MAX,
					step: 5,
					"aria-label": "Rover speed",
					disabled,
					onValueCommit: (values) => send.mutate({
						command: "set_speed",
						speed: values[0] ?? 0
					})
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center justify-between gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
					label: "Last command",
					value: data?.lastCommand ? data.lastCommand.replace("_", " ") : "—"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
					variant: "destructive",
					size: "sm",
					disabled: send.isPending,
					onClick: () => send.mutate({ command: stopped ? "stop" : "emergency_stop" }),
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(OctagonX, {
						className: "size-4",
						"aria-hidden": true
					}), stopped ? "Release" : "E-Stop"]
				})]
			})
		]
	});
}
function LatestSnapshotCard() {
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(["snapshot"], () => monitoringApi.getLatestSnapshot(), POLLING_INTERVALS.snapshot, void 0, "detections");
	const snapshotUrl = resolveApiUrl(data?.imageUrl);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SectionCard, {
		title: "Latest Snapshot",
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		actions: data ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SeverityBadge, { severity: data.severity }) : null,
		contentClassName: "flex flex-col gap-4",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "relative aspect-video w-full overflow-hidden rounded-lg border border-border bg-background",
			children: snapshotUrl ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("img", {
				src: snapshotUrl,
				alt: `Detection snapshot ${data?.id ?? ""}`,
				loading: "lazy",
				className: "size-full object-cover"
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "absolute inset-0 flex flex-col items-center justify-center gap-2 text-muted-foreground",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ImageOff, {
					className: "size-8",
					"aria-hidden": true
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-xs",
					children: "No snapshot available yet"
				})]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "grid grid-cols-2 gap-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
				label: "Class",
				value: data?.crackClass ? CRACK_CLASS_LABELS[data.crackClass] : "None"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LabeledValue, {
				label: "Captured",
				value: data ? formatTime(data.timestamp) : "—"
			})]
		})]
	});
}
var TILES = [
	{
		key: "totalDetections",
		label: "Total Detections",
		icon: TrendingUp,
		accent: "text-primary"
	},
	{
		key: "smallCrack",
		label: "Small Cracks",
		icon: Minus,
		accent: "text-success"
	},
	{
		key: "mediumCrack",
		label: "Medium Cracks",
		icon: Layers,
		accent: "text-warning"
	},
	{
		key: "largeCrack",
		label: "Large Cracks",
		icon: OctagonAlert,
		accent: "text-warning"
	},
	{
		key: "brokenChain",
		label: "Broken Chains",
		icon: Unlink,
		accent: "text-destructive"
	},
	{
		key: "criticalAlerts",
		label: "Critical Alerts",
		icon: OctagonAlert,
		accent: "text-destructive"
	}
];
function StatisticsCard() {
	const { data, isPending, isError, refetch, dataUpdatedAt } = useLiveQuery(["statistics"], () => monitoringApi.getStatistics(), POLLING_INTERVALS.statistics, void 0, "telemetry");
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SectionCard, {
		title: "Detection Statistics",
		className: "h-full",
		loading: isPending,
		error: isError,
		onRetry: refetch,
		updatedAt: dataUpdatedAt,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "grid grid-cols-2 gap-3 sm:grid-cols-3",
			children: TILES.map(({ key, label, icon: Icon, accent }) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "rounded-lg border border-border bg-background/60 p-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center justify-between",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "text-xs text-muted-foreground",
						children: label
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, {
						className: `size-4 ${accent}`,
						"aria-hidden": true
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 text-2xl font-semibold tracking-tight text-foreground",
					children: formatNumber(data?.[key] ?? 0)
				})]
			}, key))
		})
	});
}
/**
* Mobile-first dashboard grid: 1 column on mobile, 2 on tablet, 12 on desktop.
* Children control their own span via `GridItem`.
*/
function DashboardGrid({ children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-5 lg:grid-cols-12",
		children
	});
}
var SPAN_CLASSES = {
	3: "lg:col-span-3",
	4: "lg:col-span-4",
	5: "lg:col-span-5",
	6: "lg:col-span-6",
	8: "lg:col-span-8",
	12: "sm:col-span-2 lg:col-span-12"
};
function GridItem({ span = 4, fullWidthOnTablet = false, className, children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: cn("flex min-w-0 flex-col", fullWidthOnTablet && "sm:col-span-2", SPAN_CLASSES[span], className),
		children
	});
}
function DashboardFooter() {
	const { data: status } = useLiveQuery(["system-status"], () => monitoringApi.getSystemStatus(), POLLING_INTERVALS.systemStatus);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("footer", {
		className: "rounded-xl border border-border bg-card px-4 py-3 shadow-card sm:px-5",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-col items-start justify-between gap-2 text-xs text-muted-foreground sm:flex-row sm:items-center",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", { children: ["Version ", APP_CONFIG.version] }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "truncate",
					children: APP_CONFIG.developer
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
					className: "inline-flex items-center gap-1.5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusDot, { state: status?.online === false ? "error" : "connected" }), status?.online === false ? "Offline" : "All systems operational"]
				})
			]
		})
	});
}
function ConnectionChip({ label, state }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex items-center gap-2 rounded-md border border-border bg-background/60 px-2.5 py-1.5",
		title: `${label}: ${CONNECTION_LABELS[state]}`,
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusDot, { state }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "text-xs font-medium text-foreground",
				children: label
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "text-xs text-muted-foreground",
				children: CONNECTION_LABELS[state]
			})
		]
	});
}
/** Ticking clock for the header date/time display. */
function useClock(intervalMs = 1e3) {
	const [now, setNow] = (0, import_react.useState)(null);
	(0, import_react.useEffect)(() => {
		setNow(/* @__PURE__ */ new Date());
		const id = setInterval(() => setNow(/* @__PURE__ */ new Date()), intervalMs);
		return () => clearInterval(id);
	}, [intervalMs]);
	return now;
}
function DashboardHeader() {
	const now = useClock();
	const { data: status } = useLiveQuery(["system-status"], () => monitoringApi.getSystemStatus(), POLLING_INTERVALS.systemStatus);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("header", {
		className: "rounded-xl border border-border bg-card shadow-card",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-col gap-4 p-4 sm:p-5 lg:flex-row lg:items-center lg:justify-between",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex min-w-0 items-start gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-primary",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TrainFront, {
						className: "size-5",
						"aria-hidden": "true"
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "min-w-0",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "text-base font-semibold leading-tight tracking-tight text-foreground sm:text-lg lg:text-xl",
						children: APP_CONFIG.name
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "inline-flex items-center gap-1.5",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusDot, { state: status?.online === false ? "error" : "connected" }), status?.online === false ? "System Offline" : "System Online"]
						}), status && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "inline-flex items-center gap-1.5",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Activity, {
									className: "size-3",
									"aria-hidden": "true"
								}),
								"Uptime ",
								formatUptime(status.uptimeSeconds)
							]
						})]
					})]
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-col gap-3 lg:items-end",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "text-xs text-muted-foreground sm:text-sm",
					suppressHydrationWarning: true,
					children: now ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "font-mono tabular-nums text-foreground",
						children: [
							now.toLocaleDateString(void 0, {
								weekday: "short",
								year: "numeric",
								month: "short",
								day: "2-digit"
							}),
							" ",
							"· ",
							now.toLocaleTimeString(void 0, { hour12: false })
						]
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "font-mono text-muted-foreground",
						children: "--"
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "flex flex-wrap gap-2",
					children: (status?.devices ?? []).map((device) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ConnectionChip, {
						label: device.label,
						state: device.state
					}, device.id))
				})]
			})]
		})
	});
}
/** Page chrome: skip link, header, responsive content container, offline banner, footer. */
function DashboardLayout({ children }) {
	const { data: status } = useLiveQuery(["system-status"], () => monitoringApi.getSystemStatus(), POLLING_INTERVALS.systemStatus);
	const offline = status?.online === false;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-screen bg-background",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
			href: "#main-content",
			className: "sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground focus:shadow-lg",
			children: "Skip to content"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "mx-auto flex w-full max-w-[1600px] flex-col gap-4 px-3 py-4 sm:gap-5 sm:px-5 sm:py-6 lg:px-8",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DashboardHeader, {}),
				offline && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					role: "status",
					className: "flex items-center gap-2 rounded-xl border border-destructive/40 bg-destructive/10 px-4 py-2.5 text-sm text-destructive",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(WifiOff, {
						className: "size-4 shrink-0",
						"aria-hidden": true
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "min-w-0",
						children: "System offline — telemetry may be stale."
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("main", {
					id: "main-content",
					tabIndex: -1,
					className: "flex-1 outline-none",
					children
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DashboardFooter, {})
			]
		})]
	});
}
function Dashboard() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DashboardLayout, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DashboardGrid, { children: [
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 8,
			fullWidthOnTablet: true,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CameraFeedCard, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 4,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RoverControlCard, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 4,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ActiveAlertCard, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 4,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TrackHealthCard, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 4,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(GpsCard, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 4,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(GsmCard, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 8,
			fullWidthOnTablet: true,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatisticsCard, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 6,
			fullWidthOnTablet: true,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DetectionDistributionChart, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 6,
			fullWidthOnTablet: true,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SeverityTrendChart, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 4,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LatestSnapshotCard, {})
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(GridItem, {
			span: 8,
			fullWidthOnTablet: true,
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DetectionHistoryTable, {})
		})
	] }) });
}
//#endregion
export { Dashboard as component };

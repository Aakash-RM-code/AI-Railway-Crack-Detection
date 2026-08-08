import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { _ as Link, f as createRouter, g as createRootRouteWithContext, h as createFileRoute, l as Scripts, m as lazyRouteComponent, p as Outlet, u as HeadContent, v as useRouter } from "../_libs/@tanstack/react-router+[...].mjs";
import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-collection+[...].mjs";
import { t as QueryClient } from "../_libs/tanstack__query-core.mjs";
import { i as useQueryClient, r as QueryClientProvider } from "../_libs/tanstack__react-query.mjs";
import { t as Toaster } from "../_libs/sonner.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/router-z3rEwVU0.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var __defProp = Object.defineProperty;
var __exportAll = (all, no_symbols) => {
	let target = {};
	for (var name in all) __defProp(target, name, {
		get: all[name],
		enumerable: true
	});
	if (!no_symbols) __defProp(target, Symbol.toStringTag, { value: "Module" });
	return target;
};
function Toaster$1({ ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Toaster, {
		theme: "dark",
		className: "toaster group",
		toastOptions: { classNames: {
			toast: "group toast group-[.toaster]:bg-popover group-[.toaster]:text-popover-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg",
			description: "group-[.toast]:text-muted-foreground",
			actionButton: "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
			cancelButton: "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground"
		} },
		...props
	});
}
/** Static application configuration (no secrets, no backend logic). */
var APP_CONFIG = {
	name: "Railway Crack Detection & Monitoring System",
	shortName: "RailGuard Monitor",
	version: "1.0.0",
	developer: "Railway Systems Engineering Team"
};
/** Refresh cadence in ms for the polling data layer (later: WebSocket push). */
var POLLING_INTERVALS = {
	systemStatus: 5e3,
	camera: 2e3,
	alert: 3e3,
	health: 1e4,
	gps: 4e3,
	gsm: 1e4,
	statistics: 8e3,
	detections: 8e3,
	snapshot: 15e3,
	rover: 4e3
};
/** Toggles for swapping the data source once the backend is available. */
var FEATURE_FLAGS = { useMockData: false };
var styles_default = "/assets/styles-CB94-b0w.css";
/**
* Endpoint map mirroring the FastAPI backend.
* Declared now so the REST/WebSocket client can be dropped in without touching UI code.
*/
var API_BASE_URL = {
	"BASE_URL": "/",
	"DEV": false,
	"MODE": "production",
	"PROD": true,
	"SSR": true,
	"TSS_DEV_SERVER": "false",
	"TSS_DEV_SSR_STYLES_BASEPATH": "/",
	"TSS_DEV_SSR_STYLES_ENABLED": "true",
	"TSS_DISABLE_CSRF_MIDDLEWARE_WARNING": "false",
	"TSS_INLINE_CSS_ENABLED": "false",
	"TSS_ROUTER_BASEPATH": "",
	"TSS_SERVER_FN_BASE": "/_serverFn/"
}["VITE_API_BASE_URL"] ?? "http://localhost:8080";
/** Base URL of the WebSocket server. The WS client appends `/ws/${channel}`. */
var WS_BASE_URL = {
	"BASE_URL": "/",
	"DEV": false,
	"MODE": "production",
	"PROD": true,
	"SSR": true,
	"TSS_DEV_SERVER": "false",
	"TSS_DEV_SSR_STYLES_BASEPATH": "/",
	"TSS_DEV_SSR_STYLES_ENABLED": "true",
	"TSS_DISABLE_CSRF_MIDDLEWARE_WARNING": "false",
	"TSS_INLINE_CSS_ENABLED": "false",
	"TSS_ROUTER_BASEPATH": "",
	"TSS_SERVER_FN_BASE": "/_serverFn/"
}["VITE_WS_BASE_URL"] ?? "ws://localhost:8080";
var API_ENDPOINTS = {
	systemStatus: "/api/system/status",
	cameraState: "/api/camera/state",
	cameraConnect: "/api/camera/connect",
	cameraDisconnect: "/api/camera/disconnect",
	latestAlert: "/api/alerts/latest",
	trackHealth: "/api/track-health",
	gps: "/api/gps",
	gsmStatus: "/api/gsm/status",
	sendSms: "/api/gsm/send-sms",
	statistics: "/api/statistics",
	detectionDistribution: "/api/statistics/distribution",
	severityTrend: "/api/statistics/trend",
	detections: "/api/detections",
	latestSnapshot: "/api/detections/latest-snapshot",
	roverState: "/api/rover/state",
	roverCommand: "/api/rover/command"
};
/**
* Resolves a possibly-relative backend URL (e.g. the relative `/api/...` path
* returned by the snapshot endpoint) to an absolute URL on the API host, which
* may differ from the origin the frontend is served from. Absolute URLs pass
* through unchanged.
*/
function resolveApiUrl(path) {
	if (!path) return null;
	if (/^https?:\/\//i.test(path)) return path;
	return `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}
/**
* Per-channel realtime connection status store.
*
* A tiny external store (no provider context) so any hook/component can read
* the live status of any channel and React Query polling can be gated on it.
* Written this way to stay outside the React tree and keep the layer modular.
*/
var statusMap = {
	telemetry: "offline",
	detections: "offline",
	"camera-status": "offline"
};
var listeners = /* @__PURE__ */ new Set();
function getChannelStatus(channel) {
	return statusMap[channel];
}
function setChannelStatus(channel, status) {
	if (statusMap[channel] === status) return;
	statusMap = {
		...statusMap,
		[channel]: status
	};
	for (const listener of listeners) listener();
}
function subscribe(listener) {
	listeners.add(listener);
	return () => {
		listeners.delete(listener);
	};
}
/**
* Returns the current status of a channel, re-rendering on change.
* A single WS channel "camera-status" is treated as the union for the camera
* card; other channels map 1:1.
*/
function useRealtimeStatus(channel) {
	const [status, setStatus] = (0, import_react.useState)(() => getChannelStatus(channel));
	(0, import_react.useEffect)(() => {
		setStatus(getChannelStatus(channel));
		return subscribe(() => {
			setStatus(getChannelStatus(channel));
		});
	}, [channel]);
	return status;
}
/** True when the channel has received at least one valid message (live). */
function useIsRealtimeLive(channel) {
	const status = useRealtimeStatus(channel ?? "telemetry");
	return channel === void 0 ? false : status === "live";
}
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
var HEARTBEAT_MS = 25e3;
var BASE_RECONNECT_MS = 1e3;
var MAX_RECONNECT_MS = 3e4;
function createRealtimeClient(channel, { onMessage }) {
	let socket = null;
	let heartbeatTimer = null;
	let reconnectTimer = null;
	let reconnectAttempt = 0;
	let stopped = true;
	function backoffDelay() {
		return Math.min(BASE_RECONNECT_MS * 2 ** Math.min(reconnectAttempt, Math.log2(MAX_RECONNECT_MS / BASE_RECONNECT_MS)), MAX_RECONNECT_MS);
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
			if (socket && socket.readyState === WebSocket.OPEN) socket.send("ping");
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
		socket.onmessage = (event) => {
			let payload;
			try {
				payload = JSON.parse(event.data);
			} catch {
				return;
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
		}
	};
}
function mapSource(mode) {
	if (mode === "esp32cam" || mode === "esp32-cam") return "esp32-cam";
	if (mode === "demo" || mode === "demo-video") return "demo-video";
	return "usb";
}
function mapCrackClass(cls) {
	const name = (cls ?? "").toLowerCase();
	if (name.includes("small")) return "small_crack";
	if (name.includes("medium")) return "medium_crack";
	if (name.includes("large")) return "large_crack";
	if (name.includes("broken")) return "broken_chain";
	return null;
}
function parseResolution(resolution) {
	if (!resolution) return {};
	const match = resolution.match(/(\d+)\s*[x×]\s*(\d+)/);
	if (!match) return {};
	return {
		width: Number(match[1]),
		height: Number(match[2])
	};
}
function connectionFrom(running, error) {
	if (error) return "error";
	return running ? "connected" : "disconnected";
}
function nowIso() {
	return (/* @__PURE__ */ new Date()).toISOString();
}
/**
* Strips keys whose value is `undefined` and returns a clean `Partial<T>`.
* Required because the project compiles with `exactOptionalPropertyTypes`,
* which rejects explicit `undefined` on optional properties — and an omitted
* key is exactly the "preserve last value" signal the cache merge relies on.
*/
function pickDefined(patch) {
	const out = {};
	for (const [key, value] of Object.entries(patch)) if (value !== void 0) out[key] = value;
	return out;
}
function mapCameraStatus(payload) {
	const { width, height } = parseResolution(payload.resolution);
	const running = Boolean(payload.running);
	return pickDefined({
		source: mapSource(payload.mode),
		state: connectionFrom(running, payload.error),
		fps: payload.fps,
		width,
		height,
		detectionActive: running,
		streamUrl: running ? "/api/camera/stream" : void 0
	});
}
function mapTelemetryAlert(payload) {
	const alert = payload.alert;
	if (!alert) return void 0;
	return {
		id: `alert-live-${payload.timestamp ?? nowIso()}`,
		severity: alert.severity?.toUpperCase() ?? "SAFE",
		crackClass: mapCrackClass(alert.class_name),
		confidence: alert.confidence ?? 0,
		message: alert.message ?? "Track is Safe",
		timestamp: payload.timestamp ?? nowIso()
	};
}
function mapTelemetryHealth(payload) {
	const health = payload.health;
	if (!health) return {};
	return pickDefined({
		overall: health.score,
		status: health.status?.toLowerCase(),
		updatedAt: payload.timestamp ?? nowIso()
	});
}
function mapTelemetryStatistics(payload) {
	const stats = payload.stats;
	if (!stats) return {};
	return pickDefined({
		totalDetections: stats.total,
		smallCrack: stats.small,
		mediumCrack: stats.medium,
		largeCrack: stats.large,
		brokenChain: stats.broken
	});
}
function mapTelemetryRover(payload) {
	const rover = payload.rover;
	if (!rover) return {};
	return pickDefined({
		state: rover.online ? "connected" : "disconnected",
		emergencyStopped: rover.online ? !rover.moving : void 0
	});
}
function mapTelemetryGps(payload) {
	const gps = payload.gps;
	if (!gps) return {};
	return pickDefined({
		latitude: gps.latitude,
		longitude: gps.longitude,
		hasFix: Boolean(gps.hasFix),
		updatedAt: payload.timestamp ?? nowIso()
	});
}
function mapTelemetryGsm(payload) {
	const gsm = payload.gsm;
	if (!gsm) return {};
	return pickDefined({
		state: gsm.online ? "connected" : "disconnected",
		signalStrength: gsm.signalStrength
	});
}
function mapTelemetryCamera(payload) {
	if (!payload.camera) return void 0;
	return mapCameraStatus(payload.camera);
}
function mapDetectionsAlert(payload) {
	const alert = payload.alert;
	if (!alert) return void 0;
	return {
		id: `alert-det-${payload.timestamp ?? nowIso()}`,
		severity: alert.severity?.toUpperCase() ?? "SAFE",
		crackClass: mapCrackClass(alert.class_name),
		confidence: alert.confidence ?? 0,
		message: alert.message ?? "Track is Safe",
		timestamp: payload.timestamp ?? nowIso()
	};
}
function mapDetectionsSnapshot(payload) {
	if (!payload.latestSnapshot) return void 0;
	return payload.latestSnapshot;
}
/**
* RealtimeProvider — mounts one WebSocket client per channel and applies live
* payloads into the React Query cache as partial merges.
*
* Merge strategy: each mapped field is `undefined` unless the WebSocket carried
* it, and `setQueryData` merges the patch over the last known value (from REST
* or a previous push). This keeps the frontend domain types complete even
* though the WebSocket payloads are deliberately small subsets — and preserves
* REST as the automatic fallback whenever a channel is not "live".
*
* Restore-points: when a channel is NOT live, the existing REST polling already
* running through useLiveQuery keeps the same query keys fresh.
*/
/** Merges a partial patch over the previous cache value, preserving unknowns. */
function mergeCache(prev, patch) {
	return {
		...prev ?? {},
		...patch
	};
}
function patchQuery(queryClient, queryKey, patch) {
	if (patch === void 0) return;
	queryClient.setQueryData(queryKey, (prev) => mergeCache(prev, patch));
}
function handleCameraStatus(queryClient, payload) {
	patchQuery(queryClient, ["camera"], mapCameraStatus(payload));
}
function handleTelemetry(queryClient, payload) {
	const alert = mapTelemetryAlert(payload);
	if (alert) patchQuery(queryClient, ["alert"], alert);
	const camera = mapTelemetryCamera(payload);
	if (camera) patchQuery(queryClient, ["camera"], camera);
	patchQuery(queryClient, ["track-health"], mapTelemetryHealth(payload));
	patchQuery(queryClient, ["statistics"], mapTelemetryStatistics(payload));
	patchQuery(queryClient, ["rover"], mapTelemetryRover(payload));
	patchQuery(queryClient, ["gps"], mapTelemetryGps(payload));
	patchQuery(queryClient, ["gsm"], mapTelemetryGsm(payload));
}
function handleDetections(queryClient, payload) {
	const alert = mapDetectionsAlert(payload);
	if (alert) patchQuery(queryClient, ["alert"], alert);
	const snapshot = mapDetectionsSnapshot(payload);
	if (snapshot) patchQuery(queryClient, ["snapshot"], snapshot);
	queryClient.invalidateQueries({ queryKey: ["detections"] });
}
function RealtimeProvider({ children }) {
	const queryClient = useQueryClient();
	const clientsRef = (0, import_react.useRef)(/* @__PURE__ */ new Map());
	(0, import_react.useEffect)(() => {
		if (typeof window === "undefined") return;
		const clients = /* @__PURE__ */ new Map();
		clients.set("camera-status", createRealtimeClient("camera-status", { onMessage: (payload) => handleCameraStatus(queryClient, payload) }));
		clients.set("telemetry", createRealtimeClient("telemetry", { onMessage: (payload) => handleTelemetry(queryClient, payload) }));
		clients.set("detections", createRealtimeClient("detections", { onMessage: (payload) => handleDetections(queryClient, payload) }));
		for (const [, client] of clients) client.start();
		clientsRef.current = clients;
		return () => {
			for (const [, client] of clients) client.stop();
			clientsRef.current.clear();
		};
	}, [queryClient]);
	return children;
}
var ROOT_DESCRIPTION = "Railway crack detection & rover monitoring system for real-time track inspection and telemetry.";
function NotFoundComponent() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex min-h-screen items-center justify-center bg-background px-4",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "max-w-md text-center",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "text-7xl font-bold text-foreground",
					children: "404"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "mt-4 text-xl font-semibold text-foreground",
					children: "Page not found"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 text-sm text-muted-foreground",
					children: "The page you're looking for doesn't exist or has been moved."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-6",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/",
						className: "inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90",
						children: "Go home"
					})
				})
			]
		})
	});
}
function ErrorComponent({ error, reset }) {
	console.error(error);
	const router = useRouter();
	(0, import_react.useEffect)(() => {}, [error]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex min-h-screen items-center justify-center bg-background px-4",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "max-w-md text-center",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "text-xl font-semibold tracking-tight text-foreground",
					children: "This page didn't load"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 text-sm text-muted-foreground",
					children: "Something went wrong on our end. You can try refreshing or head back home."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-6 flex flex-wrap justify-center gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						onClick: () => {
							router.invalidate();
							reset();
						},
						className: "inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90",
						children: "Try again"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
						href: "/",
						className: "inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent",
						children: "Go home"
					})]
				})
			]
		})
	});
}
var Route$1 = createRootRouteWithContext()({
	head: () => ({
		meta: [
			{ charSet: "utf-8" },
			{
				name: "viewport",
				content: "width=device-width, initial-scale=1"
			},
			{ title: `${APP_CONFIG.shortName} — ${APP_CONFIG.name}` },
			{
				name: "description",
				content: ROOT_DESCRIPTION
			},
			{
				name: "author",
				content: APP_CONFIG.developer
			},
			{
				property: "og:title",
				content: `${APP_CONFIG.shortName} — ${APP_CONFIG.name}`
			},
			{
				property: "og:description",
				content: ROOT_DESCRIPTION
			},
			{
				property: "og:type",
				content: "website"
			},
			{
				name: "twitter:card",
				content: "summary_large_image"
			}
		],
		links: [{
			rel: "stylesheet",
			href: styles_default
		}, {
			rel: "icon",
			href: "/favicon.svg",
			type: "image/svg+xml"
		}]
	}),
	shellComponent: RootShell,
	component: RootComponent,
	notFoundComponent: NotFoundComponent,
	errorComponent: ErrorComponent
});
function RootShell({ children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("html", {
		lang: "en",
		className: "dark",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("head", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(HeadContent, {}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("body", {
			className: "bg-background text-foreground antialiased",
			children: [children, /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Scripts, {})]
		})]
	});
}
function RootComponent() {
	const { queryClient } = Route$1.useRouteContext();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(QueryClientProvider, {
		client: queryClient,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(RealtimeProvider, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Outlet, {}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Toaster$1, {
			position: "top-right",
			richColors: true
		})] })
	});
}
var $$splitComponentImporter = () => import("./routes-NmuHb8NK.mjs");
var TITLE = `${APP_CONFIG.name} | Live Dashboard`;
var DESCRIPTION = "Industrial dashboard for real-time railway crack detection, rover control, GPS/GSM telemetry and track health monitoring.";
var rootRouteChildren = { IndexRoute: createFileRoute("/")({
	head: () => ({ meta: [
		{ title: TITLE },
		{
			name: "description",
			content: DESCRIPTION
		},
		{
			property: "og:title",
			content: TITLE
		},
		{
			property: "og:description",
			content: DESCRIPTION
		},
		{
			property: "og:type",
			content: "website"
		},
		{
			name: "twitter:card",
			content: "summary_large_image"
		}
	] }),
	component: lazyRouteComponent($$splitComponentImporter, "component")
}).update({
	id: "/",
	path: "/",
	getParentRoute: () => Route$1
}) };
var routeTree = Route$1._addFileChildren(rootRouteChildren)._addFileTypes();
var router_exports = /* @__PURE__ */ __exportAll({ getRouter: () => getRouter });
var getRouter = () => {
	const queryClient = new QueryClient();
	return createRouter({
		routeTree,
		context: { queryClient },
		scrollRestoration: true,
		defaultPreloadStaleTime: 0
	});
};
//#endregion
export { resolveApiUrl as a, POLLING_INTERVALS as c, API_ENDPOINTS as i, useIsRealtimeLive as n, APP_CONFIG as o, API_BASE_URL as r, FEATURE_FLAGS as s, router_exports as t };

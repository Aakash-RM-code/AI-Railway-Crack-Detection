# RailGuard Monitor — Frontend

Real-time dashboard for a railway crack detection & rover monitoring system.
Built with **TanStack Start**, **React 19**, **TypeScript**, **Vite**, **Tailwind CSS v4** and **shadcn/ui**.

## Features

- Live camera feed card (mock data layer by default)
- Rover control pad with speed slider and emergency stop
- Active alerts, track health, GPS & GSM telemetry
- Detection history with search, severity filter and pagination
- Statistics tiles and severity/distribution charts

## Getting started

Requires Node.js 20+ and npm.

```sh
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` (`strictPort` set in `vite.config.ts`).
Note: Lovable's hosted preview sandbox forces port **8080**; the local dev server
uses 5173 so it does not collide with the backend (which also runs on 8080).

## Scripts

| Script           | Description                                   |
| ---------------- | --------------------------------------------- |
| `npm run dev`    | Start the Vite dev server                     |
| `npm run build`  | Production build (client + SSR + Nitro)       |
| `npm run preview`| Preview the production build                  |
| `npm run lint`   | ESLint + Prettier check                       |
| `npm run format` | Auto-format the codebase with Prettier        |

## Environment variables

Copy `.env.example` to `.env` to point the frontend at a backend:

```sh
cp .env.example .env
```

| Variable              | Default                   | Purpose                              |
| --------------------- | ------------------------- | ------------------------------------ |
| `VITE_API_BASE_URL`   | `http://localhost:8080`   | Base URL for REST API calls          |
| `VITE_WS_BASE_URL`    | `ws://localhost:8080`     | Base URL for WebSocket connections (client appends `/ws/<channel>`) |

The backend dev server runs on **8080** (see `../README.md`). The frontend dev
server binds its own port (configurable); in the Lovable sandbox it is forced
to 8080, so when running backend + frontend together locally set
`VITE_API_BASE_URL`/`VITE_WS_BASE_URL` to the backend host explicitly.

## Architecture

- **Data layer**: a single `monitoringApi` seam (`src/services/index.ts`) with a
  mock implementation (`src/services/mock/`). Swap in a REST/WebSocket
  implementation of the `MonitoringApi` interface without touching UI code.
- **Data fetching**: React Query polling via `useLiveQuery` (`src/hooks/`).
- **Routing**: file-based routing under `src/routes/` (TanStack Router).
- **Theming**: Tailwind v4 design tokens defined in `src/styles.css`.
